"""Attendance Service GPS Processing Routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..core.database import get_session
from ..schemas.attendance import (
    GPSEventCreate, GPSEventCreateResponse, GPSProcessingResult,
    ErrorResponse
)
from ..services.attendance_service import AttendanceService

router = APIRouter(prefix="/gps", tags=["GPS Processing"])

@router.post(
    "/event",
    response_model=GPSEventCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Process GPS Event",
    description="**MAIN ENDPOINT**: Process GPS event from mobile app and determine attendance"
)
async def process_gps_event(
    gps_data: GPSEventCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    🎯 **CORE ENDPOINT**: Process GPS event from mobile application.

    This is the main endpoint of the GeoAttend system that:
    1. Validates GPS coordinates and accuracy
    2. Checks user enrollment in course
    3. Calculates distance to classroom
    4. Registers attendance if within range
    5. Sends notifications

    **Mobile App Usage:**
    ```javascript
    const gpsData = {
        user_id: 123,
        course_id: 456,
        latitude: -12.0464,
        longitude: -77.0428,
        accuracy: 5.0,
        event_timestamp: "2024-10-01T10:30:00Z"
    };

    fetch('/api/v1/attendance/gps/event', {
        method: 'POST',
        body: JSON.stringify(gpsData)
    });
    ```
    """

    logger.info(f"🎯 GPS EVENT: Processing for user {gps_data.user_id}, course {gps_data.course_id}")

    try:
        attendance_service = AttendanceService()
        result = await attendance_service.process_gps_event(db, gps_data)

        logger.info(f"✅ GPS processed successfully: {result.gps_event_id}, attendance: {result.attendance_recorded}")

        return GPSEventCreateResponse(
            message="GPS event processed successfully",
            data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error processing GPS event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing GPS event"
        )

@router.post(
    "/validate",
    response_model=dict,
    summary="Validate GPS Coordinates",
    description="Validate GPS coordinates without processing attendance"
)
async def validate_gps_coordinates(
    latitude: float,
    longitude: float,
    accuracy: float,
    course_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    Validate GPS coordinates and calculate distance to classroom.
    Useful for testing and debugging.
    """

    logger.info(f"🧪 GPS VALIDATION: Course {course_id}, coords ({latitude}, {longitude})")

    try:
        attendance_service = AttendanceService()

        # Validate coordinates
        from ..utils.gps_calculator import GPSCalculator

        if not GPSCalculator.validate_coordinates(latitude, longitude):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GPS coordinates"
            )

        if not GPSCalculator.validate_accuracy(accuracy, 10.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GPS accuracy too low"
            )

        # Get course coordinates
        course_coordinates = await attendance_service.service_client.get_course_coordinates(course_id)
        if not course_coordinates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course coordinates not found"
            )

        # Calculate distances
        if not course_coordinates["classrooms"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No classrooms defined for this course"
            )

        nearest_classroom, min_distance = GPSCalculator.find_nearest_classroom(
            latitude, longitude, course_coordinates["classrooms"]
        )

        within_range = min_distance <= float(course_coordinates["detection_radius"])

        return {
            "valid_coordinates": True,
            "course_id": course_id,
            "detection_radius": course_coordinates["detection_radius"],
            "nearest_classroom": nearest_classroom,
            "distance_meters": round(min_distance, 2),
            "within_range": within_range,
            "accuracy": accuracy
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error validating GPS coordinates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )