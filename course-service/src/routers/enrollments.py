"""Course Service Enrollment Management Routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from ..core.database import get_session
from ..models.course import Enrollment
from ..schemas.course import (
    EnrollmentCreate, EnrollmentResponse,
    BaseResponse, ErrorResponse
)
from ..services.course_service import CourseService

router = APIRouter(prefix="/enrollments", tags=["Enrollment Management"])

@router.get(
    "/",
    response_model=List[EnrollmentResponse],
    responses={500: {"model": ErrorResponse}}
)
async def get_all_enrollments(
    status: Optional[str] = Query(None),
    course_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session)
):
    """Get all enrollments with optional filters."""

    try:
        query = select(Enrollment)

        if status:
            query = query.where(Enrollment.status == status)
        if course_id:
            query = query.where(Enrollment.course_id == course_id)
        if student_id:
            query = query.where(Enrollment.student_id == student_id)

        result = await db.execute(query)
        enrollments = result.scalars().all()

        return [EnrollmentResponse.model_validate(enrollment) for enrollment in enrollments]

    except Exception as e:
        logger.error(f"Error fetching enrollments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post(
    "/course/{course_id}",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def enroll_student_in_course(
    course_id: int,
    enrollment_data: EnrollmentCreate,
    db: AsyncSession = Depends(get_session)
):
    """Enroll a student in a course."""

    logger.info(f"Enrolling student {enrollment_data.student_code} in course {course_id}")

    try:
        enrollment = await CourseService.enroll_student(db, course_id, enrollment_data)
        return EnrollmentResponse.model_validate(enrollment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error enrolling student: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/course/{course_id}",
    response_model=List[EnrollmentResponse],
    responses={404: {"model": ErrorResponse}}
)
async def get_course_enrollments(
    course_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Get all enrollments for a course."""

    course = await CourseService.get_course_by_id(db, course_id, include_details=True)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Filter active enrollments
    active_enrollments = [e for e in course.enrollments if e.status == "active"]
    return [EnrollmentResponse.model_validate(enrollment) for enrollment in active_enrollments]

@router.get(
    "/student/{student_id}",
    response_model=List[EnrollmentResponse],
    responses={404: {"model": ErrorResponse}}
)
async def get_student_enrollments(
    student_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Get all active enrollments for a student."""

    from sqlalchemy import select
    from ..models.course import Enrollment

    result = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.status == "active"
        )
    )
    enrollments = result.scalars().all()

    return [EnrollmentResponse.model_validate(enrollment) for enrollment in enrollments]