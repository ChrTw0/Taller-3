"""Schedule Service - Business logic for course schedules."""

from typing import List, Optional
from datetime import datetime, time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..models.course import Schedule, Course
from ..schemas.course import ScheduleCreate, ScheduleUpdate


class ScheduleService:
    """Service for managing course schedules."""

    async def create_schedule(
        self,
        db: AsyncSession,
        course_id: int,
        schedule_data: ScheduleCreate
    ) -> Schedule:
        """Create a new schedule for a course."""

        # Verify course exists
        course_result = await db.execute(
            select(Course).where(Course.id == course_id, Course.is_active == True)
        )
        course = course_result.scalar_one_or_none()

        if not course:
            raise ValueError(f"Course {course_id} not found or inactive")

        # Validate day_of_week
        if not 0 <= schedule_data.day_of_week <= 6:
            raise ValueError("day_of_week must be between 0 (Monday) and 6 (Sunday)")

        # Validate times
        if schedule_data.end_time <= schedule_data.start_time:
            raise ValueError("end_time must be after start_time")

        # Check for conflicts (same course, same day, overlapping times)
        conflicts = await self._check_schedule_conflicts(
            db, course_id, schedule_data.day_of_week,
            schedule_data.start_time, schedule_data.end_time
        )

        if conflicts:
            raise ValueError(
                f"Schedule conflict: Course already has a schedule on day {schedule_data.day_of_week} "
                f"that overlaps with {schedule_data.start_time}-{schedule_data.end_time}"
            )

        # Create schedule
        schedule = Schedule(
            course_id=course_id,
            day_of_week=schedule_data.day_of_week,
            start_time=schedule_data.start_time,
            end_time=schedule_data.end_time,
            classroom_id=schedule_data.classroom_id,
            is_active=True
        )

        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)

        logger.info(
            f"✅ Schedule created: course_id={course_id}, "
            f"day={schedule_data.day_of_week}, "
            f"time={schedule_data.start_time}-{schedule_data.end_time}"
        )

        return schedule

    async def get_course_schedules(
        self,
        db: AsyncSession,
        course_id: int,
        include_inactive: bool = False
    ) -> List[Schedule]:
        """Get all schedules for a course."""

        query = select(Schedule).where(Schedule.course_id == course_id)

        if not include_inactive:
            query = query.where(Schedule.is_active == True)

        query = query.order_by(Schedule.day_of_week, Schedule.start_time)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_schedule_by_id(
        self,
        db: AsyncSession,
        schedule_id: int
    ) -> Optional[Schedule]:
        """Get schedule by ID."""

        result = await db.execute(
            select(Schedule).where(Schedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def update_schedule(
        self,
        db: AsyncSession,
        schedule_id: int,
        schedule_data: ScheduleUpdate
    ) -> Optional[Schedule]:
        """Update schedule."""

        schedule = await self.get_schedule_by_id(db, schedule_id)

        if not schedule:
            return None

        # Validate if updating times
        if schedule_data.start_time and schedule_data.end_time:
            if schedule_data.end_time <= schedule_data.start_time:
                raise ValueError("end_time must be after start_time")

        # Update fields
        update_data = schedule_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(schedule, field, value)

        await db.commit()
        await db.refresh(schedule)

        logger.info(f"✅ Schedule updated: schedule_id={schedule_id}")

        return schedule

    async def delete_schedule(
        self,
        db: AsyncSession,
        schedule_id: int
    ) -> bool:
        """Delete (deactivate) schedule."""

        schedule = await self.get_schedule_by_id(db, schedule_id)

        if not schedule:
            return False

        schedule.is_active = False
        await db.commit()

        logger.info(f"✅ Schedule deleted: schedule_id={schedule_id}")

        return True

    async def get_current_active_schedule(
        self,
        db: AsyncSession,
        course_id: int,
        tolerance_minutes: int = 15
    ) -> Optional[Schedule]:
        """
        Get the schedule that is currently active based on current day and time.

        Args:
            course_id: Course ID
            tolerance_minutes: Minutes before/after schedule to consider "active"

        Returns:
            Active schedule if found, None otherwise
        """

        now = datetime.now()
        current_day = now.weekday()  # 0=Monday, 6=Sunday
        current_time = now.time()

        # Get all schedules for this course on current day
        result = await db.execute(
            select(Schedule).where(
                Schedule.course_id == course_id,
                Schedule.day_of_week == current_day,
                Schedule.is_active == True
            )
        )
        schedules = list(result.scalars().all())

        # Find schedule that matches current time (with tolerance)
        for schedule in schedules:
            # Calculate tolerance windows
            start_with_tolerance = self._subtract_minutes(schedule.start_time, tolerance_minutes)
            end_with_tolerance = self._add_minutes(schedule.end_time, tolerance_minutes)

            # Check if current time is within the window
            if start_with_tolerance <= current_time <= end_with_tolerance:
                logger.info(
                    f"✅ Active schedule found: course={course_id}, "
                    f"day={current_day}, time={schedule.start_time}-{schedule.end_time}"
                )
                return schedule

        logger.info(f"ℹ️ No active schedule at this time for course {course_id}")
        return None

    async def _check_schedule_conflicts(
        self,
        db: AsyncSession,
        course_id: int,
        day_of_week: int,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> bool:
        """Check if there are conflicting schedules."""

        query = select(Schedule).where(
            Schedule.course_id == course_id,
            Schedule.day_of_week == day_of_week,
            Schedule.is_active == True
        )

        if exclude_schedule_id:
            query = query.where(Schedule.id != exclude_schedule_id)

        result = await db.execute(query)
        existing_schedules = list(result.scalars().all())

        # Check for time overlaps
        for existing in existing_schedules:
            # Overlaps if: new_start < existing_end AND new_end > existing_start
            if start_time < existing.end_time and end_time > existing.start_time:
                return True

        return False

    def _add_minutes(self, t: time, minutes: int) -> time:
        """Add minutes to a time object."""
        total_minutes = t.hour * 60 + t.minute + minutes
        hours = (total_minutes // 60) % 24
        mins = total_minutes % 60
        return time(hour=hours, minute=mins)

    def _subtract_minutes(self, t: time, minutes: int) -> time:
        """Subtract minutes from a time object."""
        total_minutes = t.hour * 60 + t.minute - minutes
        if total_minutes < 0:
            total_minutes = 0
        hours = total_minutes // 60
        mins = total_minutes % 60
        return time(hour=hours, minute=mins)
