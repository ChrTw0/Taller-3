"""Attendance Service Pydantic Schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, validator

from ..models.attendance import EventStatus, AttendanceStatus, AttendanceSource

# GPS Event schemas
class GPSEventCreate(BaseModel):
    """Schema for creating a GPS event from mobile app."""
    user_id: int = Field(..., gt=0, description="User ID from User Service")
    course_id: int = Field(..., gt=0, description="Course ID from Course Service")
    latitude: Decimal = Field(..., ge=Decimal('-90'), le=Decimal('90'), description="GPS latitude")
    longitude: Decimal = Field(..., ge=Decimal('-180'), le=Decimal('180'), description="GPS longitude")
    accuracy: Decimal = Field(..., ge=Decimal('0'), le=Decimal('100'), description="GPS accuracy in meters")
    altitude: Optional[Decimal] = Field(None, description="GPS altitude in meters")
    event_timestamp: datetime = Field(..., description="When GPS was captured on device")

    # Optional device info
    device_id: Optional[str] = Field(None, max_length=255)
    device_type: Optional[str] = Field(None, max_length=50, pattern="^(android|ios|web)$")
    app_version: Optional[str] = Field(None, max_length=20)

    @validator('accuracy')
    def validate_accuracy(cls, v):
        """Validate GPS accuracy is reasonable."""
        if v > 50:  # 50 meters is quite inaccurate
            raise ValueError('GPS accuracy too low for reliable attendance')
        return v

class GPSEventResponse(BaseModel):
    """Schema for GPS event response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_code: str
    course_id: int
    course_code: str
    latitude: Decimal
    longitude: Decimal
    accuracy: Decimal
    status: EventStatus
    calculated_distance: Optional[Decimal] = None
    within_range: Optional[bool] = None
    event_timestamp: datetime
    received_at: datetime
    processed_at: Optional[datetime] = None

# Attendance Record schemas
class AttendanceRecordCreate(BaseModel):
    """Schema for creating attendance record."""
    user_id: int = Field(..., gt=0)
    course_id: int = Field(..., gt=0)
    status: AttendanceStatus = AttendanceStatus.PRESENT
    source: AttendanceSource = AttendanceSource.GPS_AUTO
    class_date: datetime
    actual_arrival: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)

class AttendanceRecordUpdate(BaseModel):
    """Schema for updating attendance record."""
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = Field(None, max_length=500)
    modification_reason: Optional[str] = Field(None, max_length=500)

class AttendanceRecordResponse(BaseModel):
    """Schema for attendance record response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    gps_event_id: Optional[int] = None
    user_id: int
    user_code: str
    course_id: int
    course_code: str
    status: AttendanceStatus
    source: AttendanceSource
    class_date: datetime
    actual_arrival: Optional[datetime] = None
    classroom_name: Optional[str] = None
    recorded_distance: Optional[Decimal] = None
    is_late: bool
    minutes_late: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# GPS Processing Result schemas
class GPSProcessingResult(BaseModel):
    """Result of GPS event processing."""
    success: bool
    message: str
    gps_event_id: int
    distance_calculated: Optional[Decimal] = None
    within_range: Optional[bool] = None
    attendance_recorded: bool = False
    attendance_record_id: Optional[int] = None
    nearest_classroom: Optional[dict] = None

class AttendanceSessionCreate(BaseModel):
    """Schema for creating attendance session."""
    course_id: int = Field(..., gt=0)
    session_date: datetime
    scheduled_start: datetime
    scheduled_end: datetime

class AttendanceSessionResponse(BaseModel):
    """Schema for attendance session response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    course_code: str
    teacher_id: int
    session_date: datetime
    scheduled_start: datetime
    scheduled_end: datetime
    is_active: bool
    is_completed: bool
    total_enrolled: int
    total_present: int
    total_late: int
    total_absent: int
    created_at: datetime

# Report schemas
class AttendanceReportRequest(BaseModel):
    """Schema for attendance report request."""
    course_id: Optional[int] = None
    user_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    status_filter: Optional[AttendanceStatus] = None
    source_filter: Optional[AttendanceSource] = None

class AttendanceStats(BaseModel):
    """Attendance statistics."""
    total_sessions: int
    attended_sessions: int
    late_sessions: int
    absent_sessions: int
    attendance_rate: float
    punctuality_rate: float

class UserAttendanceReport(BaseModel):
    """User attendance report."""
    user_id: int
    user_code: str
    course_id: int
    course_code: str
    stats: AttendanceStats
    recent_records: List[AttendanceRecordResponse]

class CourseAttendanceReport(BaseModel):
    """Course attendance report."""
    course_id: int
    course_code: str
    course_name: str
    total_students: int
    session_stats: AttendanceStats
    student_reports: List[UserAttendanceReport]

# Notification schemas
class AttendanceNotification(BaseModel):
    """Schema for attendance notifications."""
    user_id: int
    course_id: int
    message: str
    notification_type: str = Field(..., pattern="^(attendance_recorded|attendance_late|attendance_absent)$")
    metadata: Optional[dict] = None

# API Response schemas
class BaseResponse(BaseModel):
    """Base API response."""
    success: bool = True
    message: str = "Operation completed successfully"

class GPSEventCreateResponse(BaseResponse):
    """GPS event creation response."""
    data: GPSProcessingResult

class AttendanceListResponse(BaseResponse):
    """Attendance list response."""
    data: List[AttendanceRecordResponse]
    total: int
    page: int
    per_page: int

class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None

# Validation schemas
class CoordinateValidation(BaseModel):
    """Validation result for coordinates."""
    is_valid: bool
    latitude: Decimal
    longitude: Decimal
    accuracy: Decimal
    validation_errors: List[str] = []

class DistanceCalculation(BaseModel):
    """Distance calculation result."""
    user_location: dict  # {lat, lng}
    target_location: dict  # {lat, lng}
    distance_meters: Decimal
    within_threshold: bool
    threshold_meters: Decimal