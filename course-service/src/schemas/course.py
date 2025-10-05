"""Course Service Pydantic Schemas."""

from datetime import datetime, time
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, validator

# Base schemas
class CourseBase(BaseModel):
    """Base course schema with common fields."""
    code: str = Field(..., min_length=3, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    credits: int = Field(default=3, ge=1, le=10)
    academic_year: str = Field(..., pattern=r"^\d{4}$")
    semester: str = Field(..., pattern="^(A|B|Summer)$")
    max_students: int = Field(default=50, ge=1, le=200)
    detection_radius: Decimal = Field(default=Decimal('2.0'), ge=Decimal('1.0'), le=Decimal('10.0'))

class ClassroomBase(BaseModel):
    """Base classroom schema."""
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    building: str = Field(..., min_length=1, max_length=100)
    room_number: str = Field(..., min_length=1, max_length=20)
    floor: Optional[int] = Field(None, ge=-5, le=50)
    latitude: Decimal = Field(..., ge=Decimal('-90'), le=Decimal('90'))
    longitude: Decimal = Field(..., ge=Decimal('-180'), le=Decimal('180'))
    altitude: Optional[Decimal] = None
    gps_radius: Decimal = Field(default=Decimal('50.0'), ge=Decimal('10.0'), le=Decimal('200.0'))
    capacity: int = Field(default=30, ge=1, le=500)
    equipment: Optional[str] = None

class ScheduleBase(BaseModel):
    """Base schedule schema."""
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    classroom_id: Optional[int] = None

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class EnrollmentBase(BaseModel):
    """Base enrollment schema."""
    student_id: int = Field(..., gt=0)
    student_code: str = Field(..., min_length=3, max_length=20)

# Request schemas
class CourseCreate(CourseBase):
    """Schema for creating a new course."""
    teacher_id: int = Field(..., gt=0)
    teacher_code: str = Field(..., min_length=3, max_length=20)

class CourseUpdate(BaseModel):
    """Schema for updating course."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=10)
    max_students: Optional[int] = Field(None, ge=1, le=200)
    detection_radius: Optional[Decimal] = Field(None, ge=Decimal('1.0'), le=Decimal('10.0'))
    is_active: Optional[bool] = None

class ClassroomCreate(ClassroomBase):
    """Schema for creating a classroom."""
    pass

class ClassroomUpdate(BaseModel):
    """Schema for updating classroom."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    building: Optional[str] = Field(None, min_length=1, max_length=100)
    room_number: Optional[str] = Field(None, min_length=1, max_length=20)
    floor: Optional[int] = Field(None, ge=-5, le=50)
    latitude: Optional[Decimal] = Field(None, ge=Decimal('-90'), le=Decimal('90'))
    longitude: Optional[Decimal] = Field(None, ge=Decimal('-180'), le=Decimal('180'))
    altitude: Optional[Decimal] = None
    gps_radius: Optional[Decimal] = Field(None, ge=Decimal('10.0'), le=Decimal('200.0'))
    capacity: Optional[int] = Field(None, ge=1, le=500)
    equipment: Optional[str] = None
    is_active: Optional[bool] = None

class CourseClassroomBase(BaseModel):
    """Base schema for course-classroom assignment."""
    classroom_id: int = Field(..., gt=0)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_primary: bool = Field(default=False)

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class CourseClassroomCreate(CourseClassroomBase):
    """Schema for creating course-classroom assignment."""
    pass

class CourseClassroomUpdate(BaseModel):
    """Schema for updating course-classroom assignment."""
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None

class ScheduleCreate(ScheduleBase):
    """Schema for creating a schedule."""
    pass

class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule."""
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    classroom_id: Optional[int] = None
    is_active: Optional[bool] = None

class EnrollmentCreate(EnrollmentBase):
    """Schema for creating enrollment."""
    pass

# Response schemas
class ClassroomResponse(ClassroomBase):
    """Schema for classroom response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CourseClassroomResponse(BaseModel):
    """Schema for course-classroom assignment response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    classroom_id: int
    classroom: Optional[ClassroomResponse] = None  # Populated when needed
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_primary: bool
    is_active: bool
    created_at: datetime

class ScheduleResponse(ScheduleBase):
    """Schema for schedule response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    is_active: bool
    created_at: datetime

class EnrollmentResponse(EnrollmentBase):
    """Schema for enrollment response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    status: str
    enrollment_date: datetime
    drop_date: Optional[datetime] = None
    created_at: datetime

class CourseResponse(CourseBase):
    """Schema for course response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: int
    teacher_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CourseDetailResponse(CourseResponse):
    """Schema for detailed course response with relationships."""
    classroom_assignments: List[CourseClassroomResponse] = []
    schedules: List[ScheduleResponse] = []
    enrollment_count: int = 0

# Coordinate-specific schemas (for Attendance Service)
class CourseCoordinates(BaseModel):
    """Simplified schema for GPS coordinates (used by Attendance Service)."""
    model_config = ConfigDict(from_attributes=True)

    course_id: int
    course_code: str
    detection_radius: Decimal
    classrooms: List[dict] = []  # [{id, latitude, longitude, building, room_number}]

# API Response schemas
class BaseResponse(BaseModel):
    """Base API response."""
    success: bool = True
    message: str = "Operation completed successfully"

class CourseCreateResponse(BaseResponse):
    """Course creation response."""
    data: CourseResponse

class CourseListResponse(BaseResponse):
    """Course list response."""
    data: List[CourseResponse]
    total: int
    page: int
    per_page: int

class ScheduleCreateResponse(BaseResponse):
    """Schedule creation response."""
    data: ScheduleResponse

class ScheduleListResponse(BaseResponse):
    """Schedule list response."""
    data: List[ScheduleResponse]

class ScheduleOptionalResponse(BaseResponse):
    """Schedule optional response (for current schedule)."""
    data: Optional[ScheduleResponse] = None

class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None