"""Course Service Schedule Routes."""

from typing import List, Optional
from datetime import time
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..core.database import get_session
from ..schemas.course import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    BaseResponse, ScheduleCreateResponse, ScheduleListResponse,
    ScheduleOptionalResponse, ErrorResponse
)
from ..services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post(
    "/course/{course_id}",
    response_model=ScheduleCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Schedule for Course",
    description="Create a new class schedule for a course"
)
async def create_schedule(
    course_id: int,
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_session)
):
    """Create a new schedule for a course."""

    logger.info(f"📅 CREATE SCHEDULE: course_id={course_id}, day={schedule_data.day_of_week}")

    try:
        schedule_service = ScheduleService()

        schedule = await schedule_service.create_schedule(
            db, course_id, schedule_data
        )

        return ScheduleCreateResponse(
            success=True,
            message=f"Schedule created successfully for course {course_id}",
            data=ScheduleResponse.model_validate(schedule)
        )

    except ValueError as e:
        logger.warning(f"⚠️ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error creating schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/course/{course_id}",
    response_model=ScheduleListResponse,
    summary="Get Course Schedules",
    description="Get all schedules for a specific course"
)
async def get_course_schedules(
    course_id: int,
    include_inactive: bool = Query(False, description="Include inactive schedules"),
    db: AsyncSession = Depends(get_session)
):
    """Get all schedules for a course."""

    logger.info(f"📅 GET SCHEDULES: course_id={course_id}")

    try:
        schedule_service = ScheduleService()

        schedules = await schedule_service.get_course_schedules(
            db, course_id, include_inactive
        )

        return ScheduleListResponse(
            success=True,
            message=f"Schedules for course {course_id}",
            data=[ScheduleResponse.model_validate(s) for s in schedules]
        )

    except Exception as e:
        logger.error(f"❌ Error getting schedules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{schedule_id}",
    response_model=ScheduleCreateResponse,
    summary="Get Schedule by ID",
    description="Get a specific schedule by ID"
)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Get schedule by ID."""

    logger.info(f"📅 GET SCHEDULE: schedule_id={schedule_id}")

    try:
        schedule_service = ScheduleService()

        schedule = await schedule_service.get_schedule_by_id(db, schedule_id)

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        return ScheduleCreateResponse(
            success=True,
            message="Schedule retrieved successfully",
            data=ScheduleResponse.model_validate(schedule)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put(
    "/{schedule_id}",
    response_model=ScheduleCreateResponse,
    summary="Update Schedule",
    description="Update an existing schedule"
)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update schedule."""

    logger.info(f"📅 UPDATE SCHEDULE: schedule_id={schedule_id}")

    try:
        schedule_service = ScheduleService()

        schedule = await schedule_service.update_schedule(
            db, schedule_id, schedule_data
        )

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        return ScheduleCreateResponse(
            success=True,
            message="Schedule updated successfully",
            data=ScheduleResponse.model_validate(schedule)
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"⚠️ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error updating schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{schedule_id}",
    response_model=BaseResponse,
    summary="Delete Schedule",
    description="Delete (deactivate) a schedule"
)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Delete (deactivate) schedule."""

    logger.info(f"📅 DELETE SCHEDULE: schedule_id={schedule_id}")

    try:
        schedule_service = ScheduleService()

        success = await schedule_service.delete_schedule(db, schedule_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        return BaseResponse(
            success=True,
            message="Schedule deleted successfully",
            data=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/course/{course_id}/current",
    response_model=ScheduleOptionalResponse,
    summary="Get Current Active Schedule",
    description="Get the schedule that is currently active (if any) based on current day/time"
)
async def get_current_schedule(
    course_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Get current active schedule for a course based on current day and time."""

    logger.info(f"📅 GET CURRENT SCHEDULE: course_id={course_id}")

    try:
        schedule_service = ScheduleService()

        schedule = await schedule_service.get_current_active_schedule(db, course_id)

        if not schedule:
            return ScheduleOptionalResponse(
                success=True,
                message="No active schedule at this time",
                data=None
            )

        return ScheduleOptionalResponse(
            success=True,
            message="Current active schedule",
            data=ScheduleResponse.model_validate(schedule)
        )

    except Exception as e:
        logger.error(f"❌ Error getting current schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
