"""User Service Configuration using Pydantic BaseSettings."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings

class UserServiceSettings(BaseSettings):
    """User Service specific settings."""

    # Service Info
    service_name: str = Field(default="user-service", env="SERVICE_NAME")
    service_port: int = Field(default=8001, env="SERVICE_PORT")
    debug: bool = Field(default=True, env="DEBUG")

    # Database - User Service has independent database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:1234@localhost:5433/user_db",
        env="DATABASE_URL"
    )

    # Security - User Service handles authentication
    secret_key: str = Field(
        default="user-service-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Password Policy
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_special: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")

    # Inter-service Communication
    course_service_url: str = Field(default="http://localhost:8002", env="COURSE_SERVICE_URL")
    attendance_service_url: str = Field(default="http://localhost:8003", env="ATTENDANCE_SERVICE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> UserServiceSettings:
    """Get cached settings instance."""
    return UserServiceSettings()