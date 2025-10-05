"""Course Service Business Logic."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from loguru import logger
import httpx

from ..models.course import Course, Classroom, CourseClassroom, Schedule, Enrollment
from ..schemas.course import (
    CourseCreate, CourseUpdate, ClassroomCreate, ClassroomUpdate,
    ScheduleCreate, EnrollmentCreate
)
from ..core.config import get_settings

settings = get_settings()

class CourseService:
    """Course business logic service."""

    @staticmethod
    async def create_course(db: AsyncSession, course_data: CourseCreate) -> Course:
        """Create a new course."""
        logger.info(f"Creating course: {course_data.code}")

        # Validate teacher exists (call User Service)
        teacher_valid = await CourseService._validate_teacher(course_data.teacher_id, course_data.teacher_code)
        if not teacher_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid teacher ID or code"
            )

        # Check if course code already exists
        existing_course = await CourseService.get_course_by_code(db, course_data.code)
        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course code already exists"
            )

        # Create course
        db_course = Course(
            code=course_data.code,
            name=course_data.name,
            description=course_data.description,
            credits=course_data.credits,
            academic_year=course_data.academic_year,
            semester=course_data.semester,
            teacher_id=course_data.teacher_id,
            teacher_code=course_data.teacher_code,
            max_students=course_data.max_students,
            detection_radius=course_data.detection_radius,
        )

        try:
            db.add(db_course)
            await db.commit()
            await db.refresh(db_course)
            logger.info(f"Course created successfully: {db_course.id}")
            return db_course
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database error creating course: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating course"
            )

    @staticmethod
    async def get_course_by_id(db: AsyncSession, course_id: int, include_details: bool = False) -> Optional[Course]:
        """Get course by ID."""
        query = select(Course).where(Course.id == course_id)

        if include_details:
            query = query.options(
                selectinload(Course.classroom_assignments).selectinload(CourseClassroom.classroom),
                selectinload(Course.schedules),
                selectinload(Course.enrollments)
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_course_by_code(db: AsyncSession, course_code: str) -> Optional[Course]:
        """Get course by code."""
        result = await db.execute(select(Course).where(Course.code == course_code))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_courses(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        teacher_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[Course], int]:
        """Get list of courses with filters and pagination."""

        query = select(Course)
        count_query = select(func.count(Course.id))

        # Apply filters
        if teacher_id:
            query = query.where(Course.teacher_id == teacher_id)
            count_query = count_query.where(Course.teacher_id == teacher_id)

        if academic_year:
            query = query.where(Course.academic_year == academic_year)
            count_query = count_query.where(Course.academic_year == academic_year)

        if is_active is not None:
            query = query.where(Course.is_active == is_active)
            count_query = count_query.where(Course.is_active == is_active)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Course.created_at.desc())

        result = await db.execute(query)
        courses = result.scalars().all()

        return courses, total

    @staticmethod
    async def update_course(db: AsyncSession, course_id: int, course_update: CourseUpdate) -> Optional[Course]:
        """Update course."""
        logger.info(f"Updating course: {course_id}")

        course = await CourseService.get_course_by_id(db, course_id)
        if not course:
            return None

        update_data = course_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(course, field, value)

        try:
            await db.commit()
            await db.refresh(course)
            logger.info(f"Course updated successfully: {course_id}")
            return course
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database error updating course: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating course"
            )

    @staticmethod
    async def delete_course(db: AsyncSession, course_id: int) -> bool:
        """Soft delete course (deactivate)."""
        logger.info(f"Deactivating course: {course_id}")

        course = await CourseService.get_course_by_id(db, course_id)
        if not course:
            return False

        course.is_active = False
        await db.commit()
        logger.info(f"Course deactivated successfully: {course_id}")
        return True

    @staticmethod
    async def add_classroom(db: AsyncSession, course_id: int, classroom_data: ClassroomCreate) -> Classroom:
        """Add classroom to course."""
        logger.info(f"Adding classroom to course: {course_id}")

        # Verify course exists
        course = await CourseService.get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Create classroom
        db_classroom = Classroom(
            course_id=course_id,
            building=classroom_data.building,
            room_number=classroom_data.room_number,
            floor=classroom_data.floor,
            latitude=classroom_data.latitude,
            longitude=classroom_data.longitude,
            altitude=classroom_data.altitude,
            capacity=classroom_data.capacity,
            equipment=classroom_data.equipment,
        )

        try:
            db.add(db_classroom)
            await db.commit()
            await db.refresh(db_classroom)
            logger.info(f"Classroom added successfully: {db_classroom.id}")
            return db_classroom
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database error adding classroom: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error adding classroom"
            )

    @staticmethod
    async def get_course_coordinates(db: AsyncSession, course_id: int) -> dict:
        """Get course coordinates for Attendance Service - CRITICAL for attendance-service."""
        course = await CourseService.get_course_by_id(db, course_id, include_details=True)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        classrooms_data = []
        # Iterate through course_classroom assignments to get classrooms
        for assignment in course.classroom_assignments:
            if assignment.is_active and assignment.classroom and assignment.classroom.is_active:
                classrooms_data.append({
                    "id": assignment.classroom.id,
                    "latitude": float(assignment.classroom.latitude),
                    "longitude": float(assignment.classroom.longitude),
                    "building": assignment.classroom.building,
                    "room_number": assignment.classroom.room_number
                })

        if not classrooms_data:
            logger.warning(f"Course {course_id} has no active classrooms assigned")

        return {
            "course_id": course.id,
            "course_code": course.code,
            "detection_radius": float(course.detection_radius),
            "classrooms": classrooms_data
        }

    @staticmethod
    async def enroll_student(db: AsyncSession, course_id: int, enrollment_data: EnrollmentCreate) -> Enrollment:
        """Enroll student in course."""
        logger.info(f"Enrolling student {enrollment_data.student_code} in course {course_id}")

        # Verify course exists and is active
        course = await CourseService.get_course_by_id(db, course_id)
        if not course or not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found or inactive"
            )

        # Check if student is already enrolled
        existing_enrollment = await db.execute(
            select(Enrollment).where(
                Enrollment.course_id == course_id,
                Enrollment.student_id == enrollment_data.student_id,
                Enrollment.status == "active"
            )
        )
        if existing_enrollment.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student already enrolled in this course"
            )

        # Check enrollment capacity
        active_enrollments = await db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.course_id == course_id,
                Enrollment.status == "active"
            )
        )
        enrollment_count = active_enrollments.scalar()

        if enrollment_count >= course.max_students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is full"
            )

        # Validate student exists (call User Service)
        student_valid = await CourseService._validate_student(enrollment_data.student_id, enrollment_data.student_code)
        if not student_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid student ID or code"
            )

        # Create enrollment
        db_enrollment = Enrollment(
            course_id=course_id,
            student_id=enrollment_data.student_id,
            student_code=enrollment_data.student_code,
        )

        try:
            db.add(db_enrollment)
            await db.commit()
            await db.refresh(db_enrollment)
            logger.info(f"Student enrolled successfully: {db_enrollment.id}")
            return db_enrollment
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database error enrolling student: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error enrolling student"
            )

    @staticmethod
    async def _validate_teacher(teacher_id: int, teacher_code: str) -> bool:
        """Validate teacher exists in User Service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.user_service_url}/api/v1/users/{teacher_id}",
                    timeout=10.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    return user_data.get("code") == teacher_code and user_data.get("role") in ["teacher", "admin"]
                return False
        except Exception as e:
            logger.error(f"Error validating teacher: {e}")
            return False

    @staticmethod
    async def _validate_student(student_id: int, student_code: str) -> bool:
        """Validate student exists in User Service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.user_service_url}/api/v1/users/{student_id}",
                    timeout=10.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    return user_data.get("code") == student_code and user_data.get("is_active") == True
                return False
        except Exception as e:
            logger.error(f"Error validating student: {e}")
            return False