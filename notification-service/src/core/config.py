"""Configuration settings for Notification Service"""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class NotificationServiceSettings(BaseSettings):
    """Notification Service configuration settings"""

    # Service
    service_name: str = Field(default="notification-service", env="SERVICE_NAME")
    service_port: int = Field(default=8004, env="SERVICE_PORT")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:1234@localhost:5436/notification_db",
        env="DATABASE_URL"
    )

    # Security - JWT for inter-service authentication
    secret_key: str = Field(
        default="user-service-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")

    # SMTP Email
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="noreply@geoattend.com", env="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="GeoAttend", env="SMTP_FROM_NAME")

    # Firebase Cloud Messaging (Push Notifications)
    fcm_credentials_path: str = Field(default="", env="FCM_CREDENTIALS_PATH")
    fcm_enabled: bool = Field(default=False, env="FCM_ENABLED")

    # Service URLs (for inter-service communication)
    user_service_url: str = Field(default="http://localhost:8001", env="USER_SERVICE_URL")
    course_service_url: str = Field(default="http://localhost:8002", env="COURSE_SERVICE_URL")
    attendance_service_url: str = Field(default="http://localhost:8003", env="ATTENDANCE_SERVICE_URL")

    # Notification settings
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: int = Field(default=60, env="RETRY_DELAY")  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> NotificationServiceSettings:
    """Get cached settings instance"""
    return NotificationServiceSettings()
