"""Course Service Course Management Routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..core.database import get_session
from ..schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, CourseDetailResponse,
    CourseCoordinates, CourseCreateResponse, CourseListResponse,
    BaseResponse, ErrorResponse
)
from ..services.course_service import CourseService
from ..models.course import Course

router = APIRouter(prefix="/courses", tags=["Course Management"])

@router.post(
    "/",
    response_model=CourseCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}}
)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_session)
):
    """Create a new course."""

    logger.info(f"Creating new course: {course_data.code}")

    try:
        course = await CourseService.create_course(db, course_data)
        return CourseCreateResponse(
            message="Course created successfully",
            data=CourseResponse.model_validate(course)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/",
    response_model=CourseListResponse,
    responses={400: {"model": ErrorResponse}}
)
async def list_courses(
    skip: int = Query(0, ge=0, description="Number of courses to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of courses to return"),
    teacher_id: Optional[int] = Query(None, description="Filter by teacher ID"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_session)
):
    """List courses with optional filters."""

    try:
        courses, total = await CourseService.get_courses(
            db,
            skip=skip,
            limit=limit,
            teacher_id=teacher_id,
            academic_year=academic_year,
            is_active=is_active
        )

        return CourseListResponse(
            message="Courses retrieved successfully",
            data=[CourseResponse.model_validate(course) for course in courses],
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )
    except Exception as e:
        logger.error(f"Unexpected error listing courses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_course(
    course_id: int,
    include_details: bool = Query(False, description="Include classrooms, schedules, and enrollments"),
    db: AsyncSession = Depends(get_session)
):
    """Get course by ID."""

    course = await CourseService.get_course_by_id(db, course_id, include_details=include_details)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    if include_details:
        # Count active enrollments
        enrollment_count = len([e for e in course.enrollments if e.status == "active"])
        course_data = CourseDetailResponse.model_validate(course)
        course_data.enrollment_count = enrollment_count
        return course_data
    else:
        # Return basic course info without relationships to avoid lazy loading issues
        return CourseResponse.model_validate(course)

@router.get(
    "/code/{course_code}",
    response_model=CourseResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_course_by_code(
    course_code: str,
    db: AsyncSession = Depends(get_session)
):
    """Get course by code."""

    course = await CourseService.get_course_by_code(db, course_code)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return CourseResponse.model_validate(course)

@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update course."""

    logger.info(f"Updating course: {course_id}")

    try:
        updated_course = await CourseService.update_course(db, course_id, course_update)
        if not updated_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        return CourseResponse.model_validate(updated_course)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete(
    "/{course_id}",
    response_model=BaseResponse,
    responses={404: {"model": ErrorResponse}}
)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Deactivate course."""

    logger.info(f"Deactivating course: {course_id}")

    success = await CourseService.delete_course(db, course_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return BaseResponse(message="Course deactivated successfully")

@router.get(
    "/{course_id}/coordinates",
    response_model=CourseCoordinates,
    responses={404: {"model": ErrorResponse}},
    summary="Get course GPS coordinates",
    description="Special endpoint for Attendance Service to get course coordinates and detection radius"
)
async def get_course_coordinates(
    course_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Get course GPS coordinates for Attendance Service."""

    logger.info(f"Getting coordinates for course: {course_id}")

    try:
        coordinates = await CourseService.get_course_coordinates(db, course_id)
        return CourseCoordinates.model_validate(coordinates)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting coordinates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )