"""Proxy service for routing requests to microservices"""
from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException, status
from loguru import logger

from ..core.config import get_settings

settings = get_settings()


class ProxyService:
    """Service for proxying requests to microservices"""

    @staticmethod
    async def forward_request(
        service_url: str,
        path: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Forward request to microservice"""

        url = f"{service_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                # Prepare headers
                request_headers = headers or {}

                # Make request based on method
                if method == "GET":
                    response = await client.get(url, headers=request_headers, params=query_params)
                elif method == "POST":
                    response = await client.post(url, headers=request_headers, json=json_data, params=query_params)
                elif method == "PUT":
                    response = await client.put(url, headers=request_headers, json=json_data, params=query_params)
                elif method == "DELETE":
                    response = await client.delete(url, headers=request_headers, params=query_params)
                elif method == "PATCH":
                    response = await client.patch(url, headers=request_headers, json=json_data, params=query_params)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported HTTP method: {method}"
                    )

                # Return response
                if response.status_code >= 400:
                    logger.warning(f"Microservice error: {service_url}{path} - Status: {response.status_code}")
                    try:
                        error_data = response.json()
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=error_data.get("detail", "Microservice error")
                        )
                    except ValueError:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=response.text or "Microservice error"
                        )

                return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout calling {service_url}{path}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Request to microservice timed out"
            )
        except httpx.ConnectError:
            logger.error(f"Connection error to {service_url}{path}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Could not connect to microservice"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error forwarding request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal gateway error"
            )

    @staticmethod
    async def user_service_request(path: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Forward request to User Service"""
        return await ProxyService.forward_request(settings.user_service_url, path, method, **kwargs)

    @staticmethod
    async def course_service_request(path: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Forward request to Course Service"""
        return await ProxyService.forward_request(settings.course_service_url, path, method, **kwargs)

    @staticmethod
    async def attendance_service_request(path: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Forward request to Attendance Service"""
        return await ProxyService.forward_request(settings.attendance_service_url, path, method, **kwargs)

    @staticmethod
    async def notification_service_request(path: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Forward request to Notification Service"""
        return await ProxyService.forward_request(settings.notification_service_url, path, method, **kwargs)
