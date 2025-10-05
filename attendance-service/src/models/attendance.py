"""Attendance Service Database Models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, func, Text, Integer, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base

class EventStatus(str, Enum):
    """GPS event processing status."""
    PENDING = "pending"
    PROCESSED = "processed"
    REJECTED = "rejected"
    ERROR = "error"

class AttendanceStatus(str, Enum):
    """Attendance record status."""
    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    EXCUSED = "excused"

class AttendanceSource(str, Enum):
    """Source of attendance record."""
    GPS_AUTO = "gps_auto"
    MANUAL = "manual"
    IMPORTED = "imported"
    CORRECTED = "corrected"

class GPSEvent(Base):
    """GPS event received from mobile applications."""

    __tablename__ = "gps_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # User and course info (references to other services)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    user_code: Mapped[str] = mapped_column(String(20), index=True)  # Cache for performance
    course_id: Mapped[int] = mapped_column(Integer, index=True)
    course_code: Mapped[str] = mapped_column(String(20))  # Cache for performance

    # GPS Data
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))  # User's location
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))  # User's location
    accuracy: Mapped[Decimal] = mapped_column(Numeric(8, 2))  # GPS accuracy in meters
    altitude: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=True)  # Optional

    # Processing info
    status: Mapped[EventStatus] = mapped_column(SQLEnum(EventStatus), default=EventStatus.PENDING)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Distance calculation results
    calculated_distance: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=True)  # meters
    nearest_classroom_id: Mapped[int] = mapped_column(Integer, nullable=True)
    within_range: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Device info (optional)
    device_id: Mapped[str] = mapped_column(String(255), nullable=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=True)  # android, ios
    app_version: Mapped[str] = mapped_column(String(20), nullable=True)

    # Timestamps
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # When GPS was captured
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<GPSEvent(id={self.id}, user_code={self.user_code}, course_code={self.course_code}, status={self.status})>"

class AttendanceRecord(Base):
    """Final attendance record after GPS processing."""

    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # References
    gps_event_id: Mapped[int] = mapped_column(Integer, nullable=True)  # Source GPS event (if any)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    user_code: Mapped[str] = mapped_column(String(20), index=True)
    course_id: Mapped[int] = mapped_column(Integer, index=True)
    course_code: Mapped[str] = mapped_column(String(20))

    # Attendance info
    status: Mapped[AttendanceStatus] = mapped_column(SQLEnum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    source: Mapped[AttendanceSource] = mapped_column(SQLEnum(AttendanceSource), default=AttendanceSource.GPS_AUTO)

    # Class session info
    class_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Location info
    classroom_id: Mapped[int] = mapped_column(Integer, nullable=True)
    classroom_name: Mapped[str] = mapped_column(String(100), nullable=True)  # Cache
    recorded_distance: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=True)  # meters

    # Additional info
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)
    minutes_late: Mapped[int] = mapped_column(Integer, nullable=True)

    # Audit info
    created_by: Mapped[str] = mapped_column(String(50), default="system")  # system, admin, teacher
    modified_by: Mapped[str] = mapped_column(String(50), nullable=True)
    modification_reason: Mapped[str] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<AttendanceRecord(id={self.id}, user_code={self.user_code}, course_code={self.course_code}, status={self.status})>"

class AttendanceSession(Base):
    """Class session tracking for attendance."""

    __tablename__ = "attendance_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Course info
    course_id: Mapped[int] = mapped_column(Integer, index=True)
    course_code: Mapped[str] = mapped_column(String(20))
    teacher_id: Mapped[int] = mapped_column(Integer)

    # Session info
    session_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Session status
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    attendance_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Statistics (calculated)
    total_enrolled: Mapped[int] = mapped_column(Integer, default=0)
    total_present: Mapped[int] = mapped_column(Integer, default=0)
    total_late: Mapped[int] = mapped_column(Integer, default=0)
    total_absent: Mapped[int] = mapped_column(Integer, default=0)

    # Notes
    session_notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<AttendanceSession(id={self.id}, course_code={self.course_code}, date={self.session_date})>"