"""Attendance Service Attendance Records Routes."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..core.database import get_session
from ..schemas.attendance import (
    AttendanceRecordResponse, AttendanceListResponse,
    AttendanceStats, ErrorResponse
)
from ..models.attendance import AttendanceStatus, AttendanceSource
from ..services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance Records"])

@router.get(
    "/records",
    response_model=AttendanceListResponse,
    summary="Get Attendance Records",
    description="Get attendance records with filters and pagination"
)
async def get_attendance_records(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    status_filter: Optional[AttendanceStatus] = Query(None, description="Filter by attendance status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_session)
):
    """Get attendance records with optional filters."""

    logger.info(f"📋 ATTENDANCE RECORDS: user={user_id}, course={course_id}, skip={skip}, limit={limit}")

    try:
        attendance_service = AttendanceService()
        records, total = await attendance_service.get_attendance_records(
            db,
            user_id=user_id,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date,
            status_filter=status_filter,
            skip=skip,
            limit=limit
        )

        return AttendanceListResponse(
            message="Attendance records retrieved successfully",
            data=[AttendanceRecordResponse.model_validate(record) for record in records],
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    except Exception as e:
        logger.error(f"❌ Error getting attendance records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/user/{user_id}/stats",
    response_model=dict,
    responses={404: {"model": ErrorResponse}},
    summary="Get User Attendance Statistics",
    description="Get detailed attendance statistics for a specific user"
)
async def get_user_attendance_stats(
    user_id: int,
    course_id: Optional[int] = Query(None, description="Filter by specific course"),
    start_date: Optional[datetime] = Query(None, description="Start date for stats"),
    end_date: Optional[datetime] = Query(None, description="End date for stats"),
    db: AsyncSession = Depends(get_session)
):
    """Get attendance statistics for a user."""

    logger.info(f"📊 USER STATS: user={user_id}, course={course_id}")

    try:
        attendance_service = AttendanceService()

        # Validate user exists
        user_data = await attendance_service.service_client.get_user(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        stats = await attendance_service.get_user_attendance_stats(
            db, user_id, course_id, start_date, end_date
        )

        return {
            "user_id": user_id,
            "user_code": user_data.get("code"),
            "course_id": course_id,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "statistics": stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/course/{course_id}/records",
    response_model=AttendanceListResponse,
    summary="Get Course Attendance Records",
    description="Get all attendance records for a specific course"
)
async def get_course_attendance_records(
    course_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    status_filter: Optional[AttendanceStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_session)
):
    """Get attendance records for a specific course."""

    logger.info(f"📚 COURSE ATTENDANCE: course={course_id}")

    try:
        attendance_service = AttendanceService()

        # Validate course exists
        course_data = await attendance_service.service_client.get_course(course_id)
        if not course_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        records, total = await attendance_service.get_attendance_records(
            db,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date,
            status_filter=status_filter,
            skip=skip,
            limit=limit
        )

        return AttendanceListResponse(
            message=f"Attendance records for course {course_data.get('code', course_id)}",
            data=[AttendanceRecordResponse.model_validate(record) for record in records],
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting course attendance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/course/{course_id}/stats",
    response_model=dict,
    summary="Get Course Attendance Statistics",
    description="Get attendance statistics summary for a course"
)
async def get_course_attendance_stats(
    course_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for stats"),
    end_date: Optional[datetime] = Query(None, description="End date for stats"),
    db: AsyncSession = Depends(get_session)
):
    """Get attendance statistics for a course."""

    logger.info(f"📊 COURSE STATS: course={course_id}")

    try:
        attendance_service = AttendanceService()

        # Validate course exists
        course_data = await attendance_service.service_client.get_course(course_id)
        if not course_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Get enrollments
        enrollments = await attendance_service.service_client.get_course_enrollments(course_id)
        total_students = len(enrollments) if enrollments else 0

        # Get attendance records
        records, total_records = await attendance_service.get_attendance_records(
            db,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date
        )

        # Calculate stats
        if total_records == 0:
            return {
                "course_id": course_id,
                "course_code": course_data.get("code"),
                "course_name": course_data.get("name"),
                "total_students": total_students,
                "total_records": 0,
                "statistics": {
                    "attendance_rate": 0.0,
                    "punctuality_rate": 0.0,
                    "present_count": 0,
                    "late_count": 0,
                    "absent_count": 0
                }
            }

        present_count = len([r for r in records if r.status == AttendanceStatus.PRESENT])
        late_count = len([r for r in records if r.status == AttendanceStatus.LATE])
        absent_count = len([r for r in records if r.status == AttendanceStatus.ABSENT])

        attendance_rate = (present_count + late_count) / total_records * 100 if total_records > 0 else 0
        punctuality_rate = present_count / total_records * 100 if total_records > 0 else 0

        return {
            "course_id": course_id,
            "course_code": course_data.get("code"),
            "course_name": course_data.get("name"),
            "total_students": total_students,
            "total_records": total_records,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "statistics": {
                "attendance_rate": round(attendance_rate, 2),
                "punctuality_rate": round(punctuality_rate, 2),
                "present_count": present_count,
                "late_count": late_count,
                "absent_count": absent_count
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting course stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )