"""Attendance Service - FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from .core.config import get_settings
from .core.database import create_tables
from .routers import gps_router, attendance_router, reports_router

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
    """Application lifespan events."""
    logger.info("🚀 Starting Attendance Service...")

    # Create database tables
    try:
        await create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise

    yield

    logger.info("🛑 Shutting down Attendance Service...")

# Create FastAPI application
app = FastAPI(
    title="GeoAttend Attendance Service",
    description="GPS-based attendance processing and management microservice",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(gps_router, prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "service": settings.service_name,
        "status": "healthy",
        "version": "1.0.0",
        "database": "attendance_db (independent)",
        "features": [
            "GPS event processing",
            "Distance calculation",
            "Attendance recording",
            "Statistics and reports"
        ]
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.service_name,
        "message": "Attendance Service is running",
        "description": "GPS-based attendance processing microservice",
        "core_endpoints": [
            "POST /api/v1/gps/event - Process GPS event (MAIN ENDPOINT)",
            "GET /api/v1/attendance/records - Get attendance records",
            "GET /api/v1/reports/attendance-summary - Generate reports"
        ],
        "docs": "/docs" if settings.debug else "Documentation disabled in production"
    }

# Main GPS processing endpoint (alias for discoverability)
@app.post("/gps-event")
async def process_gps_event_alias():
    """Alias endpoint that redirects to the main GPS processing endpoint."""
    return {
        "message": "Please use the main GPS endpoint",
        "endpoint": "POST /api/v1/gps/event",
        "documentation": "/docs"
    }

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "service": settings.service_name
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "service": settings.service_name
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=settings.debug
    )