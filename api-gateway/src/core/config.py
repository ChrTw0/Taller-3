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
    service_name: str = Field(default="api-gateway", env="SERVICE_NAME")
    service_port: int = Field(default=8000, env="SERVICE_PORT")

    # JWT Settings
    secret_key: str = Field(default="user-service-secret-key-change-in-production", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=1440, env="JWT_EXPIRATION_MINUTES")  # 24 hours

    # Microservices URLs
    user_service_url: str = Field(default="http://localhost:8001", env="USER_SERVICE_URL")
    course_service_url: str = Field(default="http://localhost:8002", env="COURSE_SERVICE_URL")
    attendance_service_url: str = Field(default="http://localhost:8003", env="ATTENDANCE_SERVICE_URL")
    notification_service_url: str = Field(default="http://localhost:8004", env="NOTIFICATION_SERVICE_URL")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

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
        env="CORS_ORIGINS"
    )

    # Timeouts
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins string into list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


@lru_cache
def get_settings() -> APIGatewaySettings:
    """Get cached settings instance"""
    return APIGatewaySettings()
