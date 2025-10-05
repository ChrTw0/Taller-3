"""Attendance Service Routers package."""

from .gps import router as gps_router
from .attendance import router as attendance_router
from .reports import router as reports_router

__all__ = ["gps_router", "attendance_router", "reports_router"]