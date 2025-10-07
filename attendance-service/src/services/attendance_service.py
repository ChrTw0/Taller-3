"""Attendance Service Business Logic."""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from loguru import logger
from decimal import Decimal

from ..models.attendance import (
    GPSEvent, AttendanceRecord, AttendanceSession,
    EventStatus, AttendanceStatus, AttendanceSource
)
from ..schemas.attendance import (
    GPSEventCreate, AttendanceRecordCreate, GPSProcessingResult,
    AttendanceReportRequest
)
from ..utils.gps_calculator import GPSCalculator
from ..core.config import get_settings
from .http_client import ServiceClient

settings = get_settings()

class AttendanceService:
    """Attendance business logic service."""

    def __init__(self):
        self.service_client = ServiceClient()
        self.gps_calculator = GPSCalculator()

    async def process_gps_event(self, db: AsyncSession, gps_data: GPSEventCreate) -> GPSProcessingResult:
        """
        Main method: Process GPS event from mobile app.
        This is the core functionality of the attendance system.
        """
        logger.info(f"Processing GPS event for user {gps_data.user_id}, course {gps_data.course_id}")

        # Step 1: Validate GPS coordinates
        if not self.gps_calculator.validate_coordinates(
            float(gps_data.latitude), float(gps_data.longitude)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GPS coordinates"
            )

        # Step 2: Validate GPS accuracy
        if not self.gps_calculator.validate_accuracy(
            float(gps_data.accuracy), settings.gps_accuracy_threshold
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GPS accuracy too low: {gps_data.accuracy}m (threshold: {settings.gps_accuracy_threshold}m)"
            )

        # Step 3: Get user information
        user_data = await self.service_client.get_user(gps_data.user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Step 4: Validate user enrollment in course
        is_enrolled = await self.service_client.validate_user_enrollment(
            gps_data.user_id, gps_data.course_id
        )
        if not is_enrolled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not enrolled in this course"
            )

        # Step 4.5: Validate class schedule (NEW - Schedule validation)
        current_schedule = await self.service_client.get_current_schedule(gps_data.course_id)
        if not current_schedule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active class schedule at this time. Please check the class schedule and try again during class hours."
            )

        logger.info(
            f"✅ Schedule validation passed: course {gps_data.course_id}, "
            f"day {current_schedule.get('day_of_week')}, "
            f"time {current_schedule.get('start_time')}-{current_schedule.get('end_time')}"
        )

        # Step 5: Get course coordinates
        course_coordinates = await self.service_client.get_course_coordinates(gps_data.course_id)
        if not course_coordinates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course coordinates not found"
            )

        # Step 6: Create GPS event record
        gps_event = await self._create_gps_event(db, gps_data, user_data)

        # Step 7: Calculate distances to all classrooms
        distance_result = await self._calculate_distances(
            gps_event, course_coordinates
        )

        # Step 8: Update GPS event with calculation results
        gps_event.calculated_distance = Decimal(str(distance_result["min_distance"]))
        gps_event.nearest_classroom_id = distance_result["nearest_classroom"]["id"]
        gps_event.within_range = distance_result["within_range"]
        gps_event.status = EventStatus.PROCESSED
        gps_event.processed_at = datetime.utcnow()

        # Step 9: Create attendance record if within range
        attendance_record = None
        if distance_result["within_range"]:
            attendance_record = await self._create_attendance_record(
                db, gps_event, distance_result
            )

            # Step 10: Send notification (async)
            await self._send_attendance_notification(
                gps_event, attendance_record, distance_result
            )

        await db.commit()

        # Step 11: Return processing result
        return GPSProcessingResult(
            success=True,
            message="GPS event processed successfully",
            gps_event_id=gps_event.id,
            distance_calculated=gps_event.calculated_distance,
            within_range=gps_event.within_range,
            attendance_recorded=attendance_record is not None,
            attendance_record_id=attendance_record.id if attendance_record else None,
            nearest_classroom=distance_result["nearest_classroom"]
        )

    async def _create_gps_event(
        self, db: AsyncSession, gps_data: GPSEventCreate, user_data: dict
    ) -> GPSEvent:
        """Create GPS event record in database."""

        gps_event = GPSEvent(
            user_id=gps_data.user_id,
            user_code=user_data["code"],
            course_id=gps_data.course_id,
            course_code="",  # Will be filled when we get course data
            latitude=gps_data.latitude,
            longitude=gps_data.longitude,
            accuracy=gps_data.accuracy,
            altitude=gps_data.altitude,
            event_timestamp=gps_data.event_timestamp,
            device_id=gps_data.device_id,
            device_type=gps_data.device_type,
            app_version=gps_data.app_version,
            status=EventStatus.PENDING
        )

        try:
            db.add(gps_event)
            await db.flush()  # Get ID without committing
            logger.info(f"GPS event created: {gps_event.id}")
            return gps_event
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database error creating GPS event: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating GPS event"
            )

    async def _calculate_distances(
        self, gps_event: GPSEvent, course_coordinates: dict
    ) -> dict:
        """Calculate distances to all classrooms and determine if within range."""

        user_lat = float(gps_event.latitude)
        user_lng = float(gps_event.longitude)
        classrooms = course_coordinates["classrooms"]
        detection_radius = float(course_coordinates["detection_radius"])

        if not classrooms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No classrooms defined for this course"
            )

        # Find nearest classroom
        nearest_classroom, min_distance = self.gps_calculator.find_nearest_classroom(
            user_lat, user_lng, classrooms, settings.earth_radius_km
        )

        # Check if within detection radius
        within_range = min_distance <= detection_radius

        logger.info(f"Distance calculation: {min_distance:.2f}m to {nearest_classroom['room_number']}, within range: {within_range}")

        return {
            "nearest_classroom": nearest_classroom,
            "min_distance": min_distance,
            "within_range": within_range,
            "detection_radius": detection_radius,
            "all_distances": []  # Could calculate all if needed
        }

    async def _create_attendance_record(
        self, db: AsyncSession, gps_event: GPSEvent, distance_result: dict
    ) -> AttendanceRecord:
        """Create attendance record for successful GPS validation."""

        # Check for duplicate attendance (prevent multiple records in short time)
        recent_cutoff = datetime.utcnow() - timedelta(seconds=settings.min_time_between_records)

        existing_record = await db.execute(
            select(AttendanceRecord).where(
                and_(
                    AttendanceRecord.user_id == gps_event.user_id,
                    AttendanceRecord.course_id == gps_event.course_id,
                    AttendanceRecord.created_at > recent_cutoff
                )
            )
        )

        if existing_record.scalar_one_or_none():
            logger.warning(f"Duplicate attendance attempt blocked for user {gps_event.user_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attendance already recorded recently"
            )

        # Determine if late
        now = datetime.utcnow()
        is_late = False
        minutes_late = None

        # TODO: Get actual scheduled start time from course schedule
        # For now, assume on time

        attendance_record = AttendanceRecord(
            gps_event_id=gps_event.id,
            user_id=gps_event.user_id,
            user_code=gps_event.user_code,
            course_id=gps_event.course_id,
            course_code=gps_event.course_code,
            status=AttendanceStatus.LATE if is_late else AttendanceStatus.PRESENT,
            source=AttendanceSource.GPS_AUTO,
            class_date=now.date(),
            actual_arrival=gps_event.event_timestamp,
            classroom_id=distance_result["nearest_classroom"]["id"],
            classroom_name=f"{distance_result['nearest_classroom']['building']} {distance_result['nearest_classroom']['room_number']}",
            recorded_distance=Decimal(str(distance_result["min_distance"])),
            is_late=is_late,
            minutes_late=minutes_late,
            created_by="system"
        )

        try:
            db.add(attendance_record)
            await db.flush()
            logger.info(f"Attendance record created: {attendance_record.id}")
            return attendance_record
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database error creating attendance record: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating attendance record"
            )

    async def _send_attendance_notification(
        self, gps_event: GPSEvent, attendance_record: AttendanceRecord, distance_result: dict
    ):
        """Send notification about attendance registration."""

        notification_data = {
            "user_id": gps_event.user_id,
            "course_id": gps_event.course_id,
            "message": f"Attendance recorded at {distance_result['nearest_classroom']['building']} {distance_result['nearest_classroom']['room_number']}",
            "notification_type": "attendance_recorded",
            "metadata": {
                "distance": float(distance_result["min_distance"]),
                "classroom": distance_result["nearest_classroom"]["room_number"],
                "timestamp": gps_event.event_timestamp.isoformat()
            }
        }

        try:
            await self.service_client.send_notification(notification_data)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            # Don't fail the whole process if notification fails

    async def get_attendance_records(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        course_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status_filter: Optional[AttendanceStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AttendanceRecord], int]:
        """Get attendance records with filters."""

        query = select(AttendanceRecord)
        count_query = select(func.count(AttendanceRecord.id))

        # Apply filters
        conditions = []

        if user_id:
            conditions.append(AttendanceRecord.user_id == user_id)

        if course_id:
            conditions.append(AttendanceRecord.course_id == course_id)

        if start_date:
            conditions.append(AttendanceRecord.class_date >= start_date.date())

        if end_date:
            conditions.append(AttendanceRecord.class_date <= end_date.date())

        if status_filter:
            conditions.append(AttendanceRecord.status == status_filter)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(AttendanceRecord.created_at.desc())

        result = await db.execute(query)
        records = result.scalars().all()

        return records, total

    async def get_user_attendance_stats(
        self,
        db: AsyncSession,
        user_id: int,
        course_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get attendance statistics for a user."""

        query = select(AttendanceRecord).where(AttendanceRecord.user_id == user_id)

        if course_id:
            query = query.where(AttendanceRecord.course_id == course_id)

        if start_date:
            query = query.where(AttendanceRecord.class_date >= start_date.date())

        if end_date:
            query = query.where(AttendanceRecord.class_date <= end_date.date())

        result = await db.execute(query)
        records = result.scalars().all()

        total_sessions = len(records)
        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "attended_sessions": 0,
                "late_sessions": 0,
                "absent_sessions": 0,
                "attendance_rate": 0.0,
                "punctuality_rate": 0.0
            }

        attended_sessions = len([r for r in records if r.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE]])
        late_sessions = len([r for r in records if r.status == AttendanceStatus.LATE])
        absent_sessions = len([r for r in records if r.status == AttendanceStatus.ABSENT])

        attendance_rate = attended_sessions / total_sessions * 100
        punctuality_rate = (attended_sessions - late_sessions) / total_sessions * 100 if total_sessions > 0 else 0

        return {
            "total_sessions": total_sessions,
            "attended_sessions": attended_sessions,
            "late_sessions": late_sessions,
            "absent_sessions": absent_sessions,
            "attendance_rate": round(attendance_rate, 2),
            "punctuality_rate": round(punctuality_rate, 2)
        }

    async def mark_absences_for_session(
        self,
        db: AsyncSession,
        course_id: int,
        schedule_id: int,
        class_date: datetime
    ) -> dict:
        """
        Mark students as absent if they didn't register attendance for this session.
        Should be called after class ends.
        """
        from sqlalchemy import select, and_
        from ..models.attendance import AttendanceRecord
        from decimal import Decimal

        logger.info(f"📋 Processing absences for course {course_id}, schedule {schedule_id}, date {class_date}")

        # 1. Get enrolled students from course-service
        try:
            enrollments_data = await self.http_client.get_course_enrollments(course_id)
            if not enrollments_data:
                logger.warning(f"No enrollments found for course {course_id}")
                return {
                    "course_id": course_id,
                    "schedule_id": schedule_id,
                    "class_date": class_date.isoformat(),
                    "total_enrolled": 0,
                    "already_registered": 0,
                    "marked_absent": 0,
                    "absent_students": []
                }

            enrolled_students = enrollments_data.get("enrollments", [])
            total_enrolled = len(enrolled_students)
            logger.info(f"📚 Found {total_enrolled} enrolled students")

        except Exception as e:
            logger.error(f"Error fetching enrollments: {e}")
            raise

        # 2. Get students who already have attendance for this date
        class_date_only = class_date.date()
        existing_records = await db.execute(
            select(AttendanceRecord).where(
                and_(
                    AttendanceRecord.course_id == course_id,
                    AttendanceRecord.class_date == class_date_only
                )
            )
        )
        existing_records_list = existing_records.scalars().all()
        students_with_attendance = {record.user_id for record in existing_records_list}

        logger.info(f"✅ {len(students_with_attendance)} students already have attendance")

        # 3. Mark absent students who didn't register
        absent_students = []
        marked_count = 0

        for enrollment in enrolled_students:
            user_id = enrollment.get("student_id")
            user_code = enrollment.get("student_code", "")

            if user_id not in students_with_attendance:
                # Create absent record
                absent_record = AttendanceRecord(
                    user_id=user_id,
                    user_code=user_code,
                    course_id=course_id,
                    course_code="",
                    status=AttendanceStatus.ABSENT,
                    source=AttendanceSource.SYSTEM_AUTO,
                    class_date=class_date_only,
                    is_late=False,
                    created_by="system_auto"
                )

                db.add(absent_record)
                marked_count += 1
                absent_students.append({
                    "user_id": user_id,
                    "user_code": user_code
                })

                logger.info(f"❌ Marked absent: user_id={user_id}, user_code={user_code}")

        # Commit all absences
        if marked_count > 0:
            await db.commit()
            logger.info(f"💾 Committed {marked_count} absence records")

        return {
            "course_id": course_id,
            "schedule_id": schedule_id,
            "class_date": class_date.isoformat(),
            "total_enrolled": total_enrolled,
            "already_registered": len(students_with_attendance),
            "marked_absent": marked_count,
            "absent_students": absent_students
        }