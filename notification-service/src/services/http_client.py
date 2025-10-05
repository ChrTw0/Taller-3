"""HTTP client for inter-service communication"""
from typing import Optional, Dict, Any
import httpx
from loguru import logger

from ..core.config import get_settings

settings = get_settings()


class HTTPClient:
    """HTTP client for calling other microservices"""

    @staticmethod
    async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information from User Service (internal endpoint with email)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.user_service_url}/api/v1/users/internal/{user_id}",
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"User service returned status {response.status_code} for user_id={user_id}")
                    return None

        except Exception as e:
            logger.error(f"Error calling user service: {str(e)}")
            return None

    @staticmethod
    async def get_course(course_id: int) -> Optional[Dict[str, Any]]:
        """Get course information from Course Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.course_service_url}/api/v1/courses/{course_id}",
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
                else:
                    logger.warning(f"Course service returned status {response.status_code} for course_id={course_id}")
                    return None

        except Exception as e:
            logger.error(f"Error calling course service: {str(e)}")
            return None

    @staticmethod
    async def get_attendance_record(attendance_id: int) -> Optional[Dict[str, Any]]:
        """Get attendance record from Attendance Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.attendance_service_url}/api/v1/attendance/records/{attendance_id}",
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
                else:
                    logger.warning(f"Attendance service returned status {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Error calling attendance service: {str(e)}")
            return None
