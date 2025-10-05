"""HTTP client for inter-service communication."""

from typing import Optional, Dict, Any, List
import httpx
from loguru import logger
from ..core.config import get_settings

settings = get_settings()

class ServiceClient:
    """HTTP client for communicating with other microservices."""

    def __init__(self):
        self.timeout = settings.http_timeout
        self.max_retries = settings.max_retries

    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic."""

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP {e.response.status_code} error on attempt {attempt + 1}: {url}")
                if e.response.status_code < 500 or attempt == self.max_retries - 1:
                    # Don't retry for client errors (4xx) or on last attempt
                    raise

            except httpx.RequestError as e:
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise

        return None

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information from User Service."""
        url = f"{settings.user_service_url}/api/v1/users/{user_id}"

        try:
            return await self._make_request("GET", url)
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None

    async def get_user_by_code(self, user_code: str) -> Optional[Dict[str, Any]]:
        """Get user by code from User Service."""
        url = f"{settings.user_service_url}/api/v1/users/code/{user_code}"

        try:
            return await self._make_request("GET", url)
        except Exception as e:
            logger.error(f"Failed to get user by code {user_code}: {e}")
            return None

    async def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Get course information from Course Service."""
        url = f"{settings.course_service_url}/api/v1/courses/{course_id}"

        try:
            return await self._make_request("GET", url)
        except Exception as e:
            logger.error(f"Failed to get course {course_id}: {e}")
            return None

    async def get_course_coordinates(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Get course GPS coordinates from Course Service."""
        url = f"{settings.course_service_url}/api/v1/courses/{course_id}/coordinates"

        try:
            result = await self._make_request("GET", url)
            logger.info(f"Retrieved coordinates for course {course_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get course coordinates for {course_id}: {e}")
            return None

    async def get_course_enrollments(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get course enrollments from Course Service."""
        url = f"{settings.course_service_url}/api/v1/enrollments/course/{course_id}"

        try:
            return await self._make_request("GET", url)
        except Exception as e:
            logger.error(f"Failed to get course enrollments for {course_id}: {e}")
            return None

    async def send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Send notification via Notification Service."""
        url = f"{settings.notification_service_url}/api/v1/notifications/send"

        try:
            result = await self._make_request("POST", url, json=notification_data)
            logger.info(f"Notification sent successfully")
            return result is not None
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    async def validate_user_enrollment(self, user_id: int, course_id: int) -> bool:
        """Validate if user is enrolled in course."""
        try:
            # Get user enrollments
            enrollments = await self._make_request(
                "GET",
                f"{settings.course_service_url}/api/v1/enrollments/student/{user_id}"
            )

            if not enrollments:
                return False

            # Check if user is enrolled in the specific course
            for enrollment in enrollments:
                if enrollment.get("course_id") == course_id and enrollment.get("status") == "active":
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to validate user enrollment: {e}")
            return False

    async def get_current_schedule(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Get current active schedule for a course from Course Service."""
        url = f"{settings.course_service_url}/api/v1/schedules/course/{course_id}/current"

        try:
            result = await self._make_request("GET", url)
            if result and result.get("success") and result.get("data"):
                logger.info(f"✅ Active schedule found for course {course_id}")
                return result.get("data")
            else:
                logger.info(f"ℹ️ No active schedule at this time for course {course_id}")
                return None
        except Exception as e:
            logger.error(f"Failed to get current schedule for course {course_id}: {e}")
            return None