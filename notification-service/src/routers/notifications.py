"""Notification API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..schemas.notification import (
    EmailNotificationRequest, PushNotificationRequest,
    NotificationResponse, NotificationListResponse,
    NotificationTemplateCreate, NotificationTemplateResponse,
    UserNotificationPreferenceUpdate, UserNotificationPreferenceResponse,
    DeviceTokenUpdate, NotificationSendResponse
)
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.post("/email", response_model=NotificationSendResponse, status_code=status.HTTP_201_CREATED)
async def send_email_notification(
    request: EmailNotificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send email notification"""
    notification = await NotificationService.send_email_notification(db, request)

    return NotificationSendResponse(
        success=notification.status == "sent",
        notification_id=notification.id,
        message=f"Email notification {'sent successfully' if notification.status == 'sent' else 'failed'}",
        status=notification.status
    )


@router.post("/push", response_model=NotificationSendResponse, status_code=status.HTTP_201_CREATED)
async def send_push_notification(
    request: PushNotificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send push notification"""
    notification = await NotificationService.send_push_notification(db, request)

    return NotificationSendResponse(
        success=notification.status == "sent",
        notification_id=notification.id,
        message=f"Push notification {'sent successfully' if notification.status == 'sent' else 'failed'}",
        status=notification.status
    )


@router.get("/user/{user_id}", response_model=NotificationListResponse)
async def get_user_notifications(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications"""
    notifications = await NotificationService.get_user_notifications(db, user_id, limit, offset)

    return NotificationListResponse(
        total=len(notifications),
        notifications=[NotificationResponse.model_validate(n) for n in notifications]
    )


@router.post("/templates", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_template(
    template: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create notification template"""
    created_template = await NotificationService.create_template(db, template)
    return NotificationTemplateResponse.model_validate(created_template)


@router.get("/preferences/{user_id}", response_model=UserNotificationPreferenceResponse)
async def get_user_preferences(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user notification preferences"""
    preferences = await NotificationService.get_user_preferences(db, user_id)

    if not preferences:
        # Return defaults
        return UserNotificationPreferenceResponse(
            user_id=user_id,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False,
            attendance_notifications=True,
            course_notifications=True,
            system_notifications=True,
            created_at=None,
            updated_at=None
        )

    return UserNotificationPreferenceResponse.model_validate(preferences)


@router.put("/preferences/{user_id}", response_model=UserNotificationPreferenceResponse)
async def update_user_preferences(
    user_id: int,
    preferences: UserNotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user notification preferences"""
    updated = await NotificationService.update_user_preferences(db, user_id, preferences)
    return UserNotificationPreferenceResponse.model_validate(updated)


@router.post("/device-token", response_model=UserNotificationPreferenceResponse)
async def update_device_token(
    token_update: DeviceTokenUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update device token for push notifications"""
    updated = await NotificationService.update_device_token(db, token_update)
    return UserNotificationPreferenceResponse.model_validate(updated)
