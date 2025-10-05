"""Attendance Service Configuration using Pydantic BaseSettings."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings

class AttendanceServiceSettings(BaseSettings):
    """Attendance Service specific settings."""

    # Service Info
    service_name: str = Field(default="attendance-service", env="SERVICE_NAME")
    service_port: int = Field(default=8003, env="SERVICE_PORT")
    debug: bool = Field(default=True, env="DEBUG")

    # Database - Attendance Service has independent database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:1234@localhost:5435/attendance_db",
        env="DATABASE_URL"
    )

    # Security - JWT for inter-service authentication
    secret_key: str = Field(
        default="user-service-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")

    # GPS Configuration
    max_distance_meters: float = Field(default=2.0, env="MAX_DISTANCE_METERS")
    gps_accuracy_threshold: float = Field(default=10.0, env="GPS_ACCURACY_THRESHOLD")  # meters
    earth_radius_km: float = Field(default=6371.0, env="EARTH_RADIUS_KM")  # Earth radius in km

    # Attendance Rules
    min_time_between_records: int = Field(default=300, env="MIN_TIME_BETWEEN_RECORDS")  # seconds (5 min)
    max_early_arrival: int = Field(default=1800, env="MAX_EARLY_ARRIVAL")  # seconds (30 min)
    max_late_arrival: int = Field(default=900, env="MAX_LATE_ARRIVAL")  # seconds (15 min)

    # Redis Configuration (for caching and background tasks)
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    cache_expiration: int = Field(default=3600, env="CACHE_EXPIRATION")  # seconds

    # Inter-service Communication
    user_service_url: str = Field(default="http://localhost:8001", env="USER_SERVICE_URL")
    course_service_url: str = Field(default="http://localhost:8002", env="COURSE_SERVICE_URL")
    notification_service_url: str = Field(default="http://localhost:8004", env="NOTIFICATION_SERVICE_URL")

    # HTTP Client Configuration
    http_timeout: float = Field(default=10.0, env="HTTP_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> AttendanceServiceSettings:
    """Get cached settings instance."""
    return AttendanceServiceSettings()