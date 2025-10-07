"""Configuration settings for API Gateway"""
from functools import lru_cache
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class APIGatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_parse_none_str='null'
    )
    """API Gateway configuration settings"""

    # Service
    service_name: str = Field(default="api-gateway", alias="SERVICE_NAME")
    service_port: int = Field(default=8000, alias="SERVICE_PORT")

    # JWT Settings
    secret_key: str = Field(default="user-service-secret-key-change-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=1440, alias="JWT_EXPIRATION_MINUTES")  # 24 hours

    # Microservices URLs
    user_service_url: str = Field(default="http://localhost:8001", alias="USER_SERVICE_URL")
    course_service_url: str = Field(default="http://localhost:8002", alias="COURSE_SERVICE_URL")
    attendance_service_url: str = Field(default="http://localhost:8003", alias="ATTENDANCE_SERVICE_URL")
    notification_service_url: str = Field(default="http://localhost:8004", alias="NOTIFICATION_SERVICE_URL")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # CORS - Incluye Expo mobile app
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://localhost:8081",  # Expo web
            "exp://localhost:8081",   # Expo mobile
            "*"                       # Permitir todos los orígenes en desarrollo
        ],
        alias="CORS_ORIGINS"
    )

    # Timeouts
    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")

@lru_cache
def get_settings() -> APIGatewaySettings:
    """Get cached settings instance"""
    return APIGatewaySettings()
