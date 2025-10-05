"""Notification models for Notification Service"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Integer, Boolean, Text, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class NotificationType(str, Enum):
    """Notification type enum"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class NotificationStatus(str, Enum):
    """Notification status enum"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


class NotificationPriority(str, Enum):
    """Notification priority enum"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Notification model - stores all notifications sent"""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[NotificationType] = mapped_column(String(20), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(String(20), nullable=False, default=NotificationStatus.PENDING)
    priority: Mapped[NotificationPriority] = mapped_column(String(20), nullable=False, default=NotificationPriority.NORMAL)

    # Content
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    template_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Recipient
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recipient_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    device_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Additional data
    additional_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Related entities
    related_course_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    related_attendance_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, status={self.status}, user_id={self.user_id})>"


class NotificationTemplate(Base):
    """Notification template model - reusable email/push templates"""
    __tablename__ = "notification_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[NotificationType] = mapped_column(String(20), nullable=False)

    # Template content
    subject_template: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)

    # Configuration
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    variables: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Expected variables in template

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<NotificationTemplate(id={self.id}, name={self.name}, type={self.type})>"


class UserNotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "user_notification_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)

    # Preferences
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    push_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Notification types
    attendance_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    course_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    system_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Device tokens for push notifications
    device_tokens: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {"android": "token", "ios": "token"}

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<UserNotificationPreference(user_id={self.user_id}, email={self.email_enabled}, push={self.push_enabled})>"
