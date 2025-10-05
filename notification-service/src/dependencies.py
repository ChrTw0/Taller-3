"""Shared dependencies for Notification Service"""
from .core.database import get_db
from .core.config import get_settings

__all__ = ["get_db", "get_settings"]
