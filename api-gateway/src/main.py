"""API Gateway - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from loguru import logger

from .core.config import get_settings
from .middleware.rate_limit import limiter
from .routers import gateway

settings = get_settings()

# Configure loguru
logger.add(
    "logs/api_gateway_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

app = FastAPI(
    title="GeoAttend API Gateway",
    description="API Gateway centralizado para todos los microservicios de GeoAttend",
    version="1.0.0"
)

# Add rate limiter state
app.state.limiter = limiter

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Permisivo para desarrollo (incluye Expo mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(gateway.router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Starting API Gateway...")
    logger.info(f"📍 User Service: {settings.user_service_url}")
    logger.info(f"📍 Course Service: {settings.course_service_url}")
    logger.info(f"📍 Attendance Service: {settings.attendance_service_url}")
    logger.info(f"📍 Notification Service: {settings.notification_service_url}")
    logger.info(f"🔒 Rate Limiting: {'Enabled' if settings.rate_limit_enabled else 'Disabled'}")
    logger.info(f"✅ API Gateway running on port {settings.service_port}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "port": settings.service_port,
        "services": {
            "user_service": settings.user_service_url,
            "course_service": settings.course_service_url,
            "attendance_service": settings.attendance_service_url,
            "notification_service": settings.notification_service_url
        },
        "rate_limiting": settings.rate_limit_enabled
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "description": "GeoAttend API Gateway - Central entry point for all microservices",
        "docs": "/docs",
        "health": "/health",
        "services": [
            "/api/v1/users",
            "/api/v1/auth",
            "/api/v1/courses",
            "/api/v1/attendance",
            "/api/v1/gps",
            "/api/v1/notifications"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True
    )
