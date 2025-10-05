"""Main gateway router for proxying requests to microservices"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Depends
from loguru import logger

from ..services.proxy_service import ProxyService
from ..core.security import get_current_user_optional

router = APIRouter(prefix="/api/v1", tags=["gateway"])


async def get_request_body(request: Request) -> Optional[Dict[str, Any]]:
    """Safely get request body as JSON"""
    if request.method not in ["POST", "PUT", "PATCH"]:
        return None

    try:
        body = await request.body()
        if not body:
            return None
        return await request.json()
    except Exception as e:
        logger.warning(f"Failed to parse request body: {e}")
        return None


# User Service routes
@router.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_user_service(
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to User Service"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.user_service_request(
        path=f"/api/v1/users/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_auth_service(
    path: str,
    request: Request
):
    """Proxy authentication requests to User Service"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.user_service_request(
        path=f"/api/v1/auth/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


# Course Service routes
@router.api_route("/courses/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@router.api_route("/courses", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_course_service_root(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Course Service root"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.course_service_request(
        path="/api/v1/courses/",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/courses/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_course_service(
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Course Service"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.course_service_request(
        path=f"/api/v1/courses/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/classrooms/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@router.api_route("/classrooms", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_classroom_service_root(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Course Service - Classrooms root"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.course_service_request(
        path="/api/v1/classrooms/",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/classrooms/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_classroom_service(
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Course Service - Classrooms"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.course_service_request(
        path=f"/api/v1/classrooms/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/enrollments/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@router.api_route("/enrollments", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_enrollment_service_root(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Course Service - Enrollments root"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.course_service_request(
        path="/api/v1/enrollments/",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/enrollments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_enrollment_service(
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Course Service - Enrollments"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.course_service_request(
        path=f"/api/v1/enrollments/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/schedules/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@router.api_route("/schedules", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_schedule_service_root(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Course Service - Schedules root"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.course_service_request(
        path="/api/v1/schedules/",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/schedules/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_schedule_service(
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Course Service - Schedules"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.course_service_request(
        path=f"/api/v1/schedules/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


# Attendance Service routes
@router.api_route("/attendance/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_attendance_service(
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Attendance Service"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.attendance_service_request(
        path=f"/api/v1/attendance/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


@router.api_route("/gps/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_gps_service(
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Attendance Service - GPS"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.attendance_service_request(
        path=f"/api/v1/gps/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )


# Notification Service routes
@router.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_notification_service(
    path: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Proxy requests to Notification Service"""
    body = await get_request_body(request)
    query_params = dict(request.query_params)
    headers = dict(request.headers)

    return await ProxyService.notification_service_request(
        path=f"/api/v1/notifications/{path}",
        method=request.method,
        headers=headers,
        json_data=body,
        query_params=query_params
    )
