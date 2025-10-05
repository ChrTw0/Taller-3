"""Pydantic schemas for Notification Service"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

from ..models.notification import NotificationType, NotificationStatus, NotificationPriority


# Email schemas
class EmailNotificationRequest(BaseModel):
    """Request to send email notification"""
    user_id: int = Field(..., description="User ID to send notification to")
    subject: str = Field(..., min_length=1, max_length=255, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body (HTML or plain text)")
    recipient_email: Optional[EmailStr] = Field(None, description="Override user email")
    template_id: Optional[int] = Field(None, description="Use template ID")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="Variables for template")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)
    related_course_id: Optional[int] = None
    related_attendance_id: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None


# Push notification schemas
class PushNotificationRequest(BaseModel):
    """Request to send push notification"""
    user_id: int = Field(..., description="User ID to send notification to")
    title: str = Field(..., min_length=1, max_length=255, description="Notification title")
    body: str = Field(..., min_length=1, description="Notification body")
    device_token: Optional[str] = Field(None, description="Override device token")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data payload")
    related_course_id: Optional[int] = None
    related_attendance_id: Optional[int] = None


# Notification response schemas
class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    user_id: int
    type: NotificationType
    status: NotificationStatus
    priority: NotificationPriority
    subject: Optional[str]
    body: str
    recipient_email: Optional[str]
    device_token: Optional[str]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List of notifications"""
    total: int
    notifications: list[NotificationResponse]


# Template schemas
class NotificationTemplateCreate(BaseModel):
    """Create notification template"""
    name: str = Field(..., min_length=1, max_length=100)
    type: NotificationType
    subject_template: Optional[str] = Field(None, max_length=255)
    body_template: str = Field(..., min_length=1)
    variables: Optional[Dict[str, str]] = Field(None, description="Expected variables: {name: description}")


class NotificationTemplateResponse(BaseModel):
    """Notification template response"""
    id: int
    name: str
    type: NotificationType
    subject_template: Optional[str]
    body_template: str
    is_active: bool
    variables: Optional[Dict[str, str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Preference schemas
class UserNotificationPreferenceUpdate(BaseModel):
    """Update user notification preferences"""
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    attendance_notifications: Optional[bool] = None
    course_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None


class UserNotificationPreferenceResponse(BaseModel):
    """User notification preferences response"""
    user_id: int
    email_enabled: bool
    push_enabled: bool
    sms_enabled: bool
    attendance_notifications: bool
    course_notifications: bool
    system_notifications: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Device token schema
class DeviceTokenUpdate(BaseModel):
    """Update device token for push notifications"""
    user_id: int
    device_type: str = Field(..., pattern="^(android|ios)$", description="Device type: android or ios")
    device_token: str = Field(..., min_length=1, description="FCM device token")


# Generic response
class NotificationSendResponse(BaseModel):
    """Response after sending notification"""
    success: bool
    notification_id: Optional[int]
    message: str
    status: NotificationStatus
