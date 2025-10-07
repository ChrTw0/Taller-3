"""Course Service Configuration using Pydantic BaseSettings."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings

class CourseServiceSettings(BaseSettings):
    """Course Service specific settings."""

    # Service Info
    service_name: str = Field(default="course-service", alias="SERVICE_NAME")
    service_port: int = Field(default=8002, alias="SERVICE_PORT")
    debug: bool = Field(default=True, alias="DEBUG")

    # Database - Course Service has independent database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:1234@localhost:5434/course_db",
        alias="DATABASE_URL"
    )

    # Security - JWT for inter-service authentication
    secret_key: str = Field(
        default="user-service-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    # GPS Configuration
    default_detection_radius: float = Field(default=2.0, alias="DEFAULT_DETECTION_RADIUS")  # meters
    max_detection_radius: float = Field(default=10.0, alias="MAX_DETECTION_RADIUS")  # meters
    min_detection_radius: float = Field(default=1.0, alias="MIN_DETECTION_RADIUS")  # meters

    # Academic Configuration
    max_students_per_course: int = Field(default=50, alias="MAX_STUDENTS_PER_COURSE")
    academic_year: str = Field(default="2024", alias="ACADEMIC_YEAR")

    # Inter-service Communication
    user_service_url: str = Field(default="http://localhost:8001", alias="USER_SERVICE_URL")
    attendance_service_url: str = Field(default="http://localhost:8003", alias="ATTENDANCE_SERVICE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> CourseServiceSettings:
    """Get cached settings instance."""
    return CourseServiceSettings()