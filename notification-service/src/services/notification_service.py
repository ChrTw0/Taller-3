"""Notification business logic service"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from loguru import logger

from ..models.notification import (
    Notification, NotificationTemplate, UserNotificationPreference,
    NotificationType, NotificationStatus, NotificationPriority
)
from ..schemas.notification import (
    EmailNotificationRequest, PushNotificationRequest,
    NotificationTemplateCreate, UserNotificationPreferenceUpdate,
    DeviceTokenUpdate
)
from .email_service import EmailService
from .push_service import PushService
from .http_client import HTTPClient


class NotificationService:
    """Business logic for notifications"""

    @staticmethod
    async def send_email_notification(
        db: AsyncSession,
        request: EmailNotificationRequest
    ) -> Notification:
        """Send email notification"""

        # Get user info
        user_info = await HTTPClient.get_user(request.user_id)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {request.user_id} not found"
            )

        # Get recipient email
        recipient_email = request.recipient_email or user_info.get("email")
        if not recipient_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No recipient email provided and user has no email"
            )

        # Check user preferences
        preferences = await NotificationService.get_user_preferences(db, request.user_id)
        if preferences and not preferences.email_enabled:
            logger.info(f"📧 Email notifications disabled for user {request.user_id}")
            notification_status = NotificationStatus.FAILED
            error_msg = "User has disabled email notifications"
            sent_at = None
            email_sent = False
        else:
            # Send email
            subject = request.subject
            body = request.body

            # Use template if provided
            if request.template_id:
                template = await NotificationService.get_template(db, request.template_id)
                if template:
                    subject = template.subject_template or subject
                    body = template.body_template
                    # Replace variables (simple implementation)
                    if request.template_variables:
                        for key, value in request.template_variables.items():
                            body = body.replace(f"{{{key}}}", str(value))
                            subject = subject.replace(f"{{{key}}}", str(value)) if subject else subject

            email_sent = await EmailService.send_email(recipient_email, subject, body)
            notification_status = NotificationStatus.SENT if email_sent else NotificationStatus.FAILED
            error_msg = None if email_sent else "Failed to send email"
            sent_at = datetime.utcnow() if email_sent else None

        # Create notification record
        notification = Notification(
            user_id=request.user_id,
            type=NotificationType.EMAIL,
            status=notification_status,
            priority=request.priority,
            subject=request.subject,
            body=request.body,
            recipient_email=recipient_email,
            template_id=request.template_id,
            additional_data=request.additional_data,
            error_message=error_msg,
            related_course_id=request.related_course_id,
            related_attendance_id=request.related_attendance_id,
            sent_at=sent_at
        )

        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        return notification

    @staticmethod
    async def send_push_notification(
        db: AsyncSession,
        request: PushNotificationRequest
    ) -> Notification:
        """Send push notification"""

        # Get user info
        user_info = await HTTPClient.get_user(request.user_id)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {request.user_id} not found"
            )

        # Get device token
        device_token = request.device_token
        if not device_token:
            # Get from preferences
            preferences = await NotificationService.get_user_preferences(db, request.user_id)
            if preferences and preferences.device_tokens:
                # Try Android first, then iOS
                device_token = preferences.device_tokens.get("android") or preferences.device_tokens.get("ios")

        if not device_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No device token available for user"
            )

        # Check user preferences
        preferences = await NotificationService.get_user_preferences(db, request.user_id)
        if preferences and not preferences.push_enabled:
            logger.info(f"📱 Push notifications disabled for user {request.user_id}")
            notification_status = NotificationStatus.FAILED
            error_msg = "User has disabled push notifications"
            sent_at = None
        else:
            # Send push notification
            push_sent = await PushService.send_push_notification(
                device_token,
                request.title,
                request.body,
                request.data
            )

            notification_status = NotificationStatus.SENT if push_sent else NotificationStatus.FAILED
            error_msg = None if push_sent else "Failed to send push notification"
            sent_at = datetime.utcnow() if push_sent else None

        # Create notification record
        notification = Notification(
            user_id=request.user_id,
            type=NotificationType.PUSH,
            status=notification_status,
            priority=request.priority,
            subject=request.title,
            body=request.body,
            device_token=device_token,
            additional_data=request.data,
            error_message=error_msg,
            related_course_id=request.related_course_id,
            related_attendance_id=request.related_attendance_id,
            sent_at=sent_at
        )

        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        return notification

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get user notifications"""
        stmt = select(Notification).where(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).offset(offset)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_template(db: AsyncSession, template_id: int) -> Optional[NotificationTemplate]:
        """Get notification template by ID"""
        stmt = select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_template(
        db: AsyncSession,
        template_data: NotificationTemplateCreate
    ) -> NotificationTemplate:
        """Create notification template"""
        template = NotificationTemplate(**template_data.model_dump())
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return template

    @staticmethod
    async def get_user_preferences(
        db: AsyncSession,
        user_id: int
    ) -> Optional[UserNotificationPreference]:
        """Get user notification preferences"""
        stmt = select(UserNotificationPreference).where(
            UserNotificationPreference.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user_preferences(
        db: AsyncSession,
        user_id: int,
        preferences: UserNotificationPreferenceUpdate
    ) -> UserNotificationPreference:
        """Update user notification preferences"""

        # Get existing preferences
        existing = await NotificationService.get_user_preferences(db, user_id)

        if existing:
            # Update existing
            update_data = preferences.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(existing, key, value)
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # Create new
            new_pref = UserNotificationPreference(
                user_id=user_id,
                **preferences.model_dump(exclude_unset=True)
            )
            db.add(new_pref)
            await db.commit()
            await db.refresh(new_pref)
            return new_pref

    @staticmethod
    async def update_device_token(
        db: AsyncSession,
        token_update: DeviceTokenUpdate
    ) -> UserNotificationPreference:
        """Update device token for push notifications"""

        preferences = await NotificationService.get_user_preferences(db, token_update.user_id)

        if not preferences:
            # Create new preferences
            preferences = UserNotificationPreference(
                user_id=token_update.user_id,
                device_tokens={token_update.device_type: token_update.device_token}
            )
            db.add(preferences)
        else:
            # Update device tokens
            device_tokens = preferences.device_tokens or {}
            device_tokens[token_update.device_type] = token_update.device_token
            preferences.device_tokens = device_tokens

        await db.commit()
        await db.refresh(preferences)
        return preferences
