"""Course Service Database Models."""

from datetime import datetime, time
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, func, Text, Integer, Numeric, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ..core.database import Base

class Course(Base):
    """Course model for academic course management."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Academic info
    credits: Mapped[int] = mapped_column(Integer, default=3)
    academic_year: Mapped[str] = mapped_column(String(10))
    semester: Mapped[str] = mapped_column(String(10))  

    # Teacher assignment
    teacher_id: Mapped[int] = mapped_column(Integer)  
    teacher_code: Mapped[str] = mapped_column(String(20))  

    # Course settings
    max_students: Mapped[int] = mapped_column(Integer, default=50)
    detection_radius: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal('2.0'))  

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    classroom_assignments: Mapped[list["CourseClassroom"]] = relationship("CourseClassroom", back_populates="course")
    schedules: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="course")
    enrollments: Mapped[list["Enrollment"]] = relationship("Enrollment", back_populates="course")

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, code={self.code}, name={self.name})>"

class Classroom(Base):
    """Classroom model with GPS coordinates - Independent resource."""

    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))

    # Location info
    building: Mapped[str] = mapped_column(String(100))
    room_number: Mapped[str] = mapped_column(String(20))
    floor: Mapped[int] = mapped_column(Integer, nullable=True)

    # GPS Coordinates (essential for attendance)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    altitude: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=True)
    gps_radius: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal('50.0'))  # Detection radius in meters

    # Additional info
    capacity: Mapped[int] = mapped_column(Integer, default=30)
    equipment: Mapped[str] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    course_assignments: Mapped[list["CourseClassroom"]] = relationship("CourseClassroom", back_populates="classroom")

    def __repr__(self) -> str:
        return f"<Classroom(id={self.id}, code={self.code}, name={self.name})>"

class CourseClassroom(Base):
    """Many-to-many relationship between Courses and Classrooms with schedule info."""

    __tablename__ = "course_classrooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id", ondelete="CASCADE"))

    # Schedule info
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=True)  # 0=Monday, 6=Sunday (nullable for flexibility)
    start_time: Mapped[time] = mapped_column(Time, nullable=True)
    end_time: Mapped[time] = mapped_column(Time, nullable=True)

    # Priority flag
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)  # Main classroom for the course

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="classroom_assignments")
    classroom: Mapped["Classroom"] = relationship("Classroom", back_populates="course_assignments")

    def __repr__(self) -> str:
        return f"<CourseClassroom(course_id={self.course_id}, classroom_id={self.classroom_id})>"

class Schedule(Base):
    """Class schedule model."""

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))

    # Schedule info
    day_of_week: Mapped[int] = mapped_column(Integer)  # 0=Monday, 6=Sunday
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    # Optional classroom override
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="schedules")

    def __repr__(self) -> str:
        return f"<Schedule(id={self.id}, course_id={self.course_id}, day={self.day_of_week})>"

class Enrollment(Base):
    """Student enrollment in courses."""

    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))

    # Student info (reference to User Service)
    student_id: Mapped[int] = mapped_column(Integer)  # Reference to User Service
    student_code: Mapped[str] = mapped_column(String(20))  # Cache for performance

    # Enrollment status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, dropped, completed
    enrollment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    drop_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")

    def __repr__(self) -> str:
        return f"<Enrollment(id={self.id}, student_code={self.student_code}, course_id={self.course_id})>"