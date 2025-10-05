"""Notification Service - FastAPI Application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from .core.config import get_settings
from .core.database import init_db, close_db
from .routers import notifications

settings = get_settings()

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("Starting Notification Service...")
    await init_db()
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down Notification Service...")
    await close_db()


app = FastAPI(
    title="GeoAttend Notification Service",
    description="Microservicio de notificaciones para GeoAttend - Email & Push Notifications",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notifications.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": "1.0.0",
        "port": settings.service_port,
        "database": "notification_db (independent)",
        "smtp_configured": bool(settings.smtp_username),
        "fcm_enabled": settings.fcm_enabled
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "notification-service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True
    )
