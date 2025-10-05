"""Course-Classroom Assignment Routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from loguru import logger

from ..core.database import get_session
from ..models.course import Course, Classroom, CourseClassroom
from ..schemas.course import (
    CourseClassroomCreate, CourseClassroomUpdate, CourseClassroomResponse,
    BaseResponse, ErrorResponse
)

router = APIRouter(tags=["Course-Classroom Assignments"])

@router.post(
    "/courses/{course_id}/classrooms/",
    response_model=CourseClassroomResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def assign_classroom_to_course(
    course_id: int,
    assignment_data: CourseClassroomCreate,
    db: AsyncSession = Depends(get_session)
):
    """Assign a classroom to a course with schedule."""

    logger.info(f"Assigning classroom {assignment_data.classroom_id} to course {course_id}")

    # Verify course exists
    course_result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )

    # Verify classroom exists
    classroom_result = await db.execute(
        select(Classroom).where(Classroom.id == assignment_data.classroom_id)
    )
    classroom = classroom_result.scalar_one_or_none()

    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {assignment_data.classroom_id} not found"
        )

    # Check for existing assignment
    existing_result = await db.execute(
        select(CourseClassroom).where(
            CourseClassroom.course_id == course_id,
            CourseClassroom.classroom_id == assignment_data.classroom_id
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Classroom {classroom.code} is already assigned to this course"
        )

    # If marked as primary, unset other primaries
    if assignment_data.is_primary:
        await db.execute(
            select(CourseClassroom).where(
                CourseClassroom.course_id == course_id,
                CourseClassroom.is_primary == True
            )
        )
        # Update all to not primary
        result = await db.execute(
            select(CourseClassroom).where(CourseClassroom.course_id == course_id)
        )
        for cc in result.scalars().all():
            cc.is_primary = False

    try:
        assignment = CourseClassroom(
            course_id=course_id,
            **assignment_data.model_dump()
        )
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        # Load classroom relationship
        assignment_with_classroom = await db.execute(
            select(CourseClassroom)
            .options(selectinload(CourseClassroom.classroom))
            .where(CourseClassroom.id == assignment.id)
        )
        assignment = assignment_with_classroom.scalar_one()

        logger.info(f"Classroom assigned successfully: {assignment.id}")
        return CourseClassroomResponse.model_validate(assignment)

    except Exception as e:
        await db.rollback()
        logger.error(f"Error assigning classroom: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/courses/{course_id}/classrooms/",
    response_model=List[CourseClassroomResponse],
    responses={404: {"model": ErrorResponse}}
)
async def get_course_classrooms(
    course_id: int,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_session)
):
    """Get all classrooms assigned to a course."""

    # Verify course exists
    course_result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )

    try:
        query = (
            select(CourseClassroom)
            .options(selectinload(CourseClassroom.classroom))
            .where(CourseClassroom.course_id == course_id)
        )

        if not include_inactive:
            query = query.where(CourseClassroom.is_active == True)

        result = await db.execute(query)
        assignments = result.scalars().all()

        return [CourseClassroomResponse.model_validate(a) for a in assignments]

    except Exception as e:
        logger.error(f"Error fetching course classrooms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put(
    "/courses/{course_id}/classrooms/{classroom_id}",
    response_model=CourseClassroomResponse,
    responses={404: {"model": ErrorResponse}}
)
async def update_course_classroom(
    course_id: int,
    classroom_id: int,
    update_data: CourseClassroomUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update course-classroom assignment (schedule, primary status)."""

    result = await db.execute(
        select(CourseClassroom)
        .options(selectinload(CourseClassroom.classroom))
        .where(
            CourseClassroom.course_id == course_id,
            CourseClassroom.classroom_id == classroom_id
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course-classroom assignment not found"
        )

    try:
        # If setting as primary, unset others
        if update_data.is_primary == True:
            other_assignments = await db.execute(
                select(CourseClassroom).where(
                    CourseClassroom.course_id == course_id,
                    CourseClassroom.id != assignment.id
                )
            )
            for other in other_assignments.scalars().all():
                other.is_primary = False

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(assignment, key, value)

        await db.commit()
        await db.refresh(assignment)

        logger.info(f"Course-classroom assignment updated: {assignment.id}")
        return CourseClassroomResponse.model_validate(assignment)

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating assignment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete(
    "/courses/{course_id}/classrooms/{classroom_id}",
    response_model=BaseResponse,
    responses={404: {"model": ErrorResponse}}
)
async def unassign_classroom_from_course(
    course_id: int,
    classroom_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Remove classroom assignment from course (soft delete)."""

    result = await db.execute(
        select(CourseClassroom).where(
            CourseClassroom.course_id == course_id,
            CourseClassroom.classroom_id == classroom_id
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course-classroom assignment not found"
        )

    try:
        assignment.is_active = False
        await db.commit()

        logger.info(f"Classroom unassigned from course: {assignment.id}")
        return BaseResponse(
            success=True,
            message="Classroom unassigned successfully"
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error unassigning classroom: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
