"""Push notification service using Firebase Cloud Messaging"""
from typing import Optional, Dict, Any
from loguru import logger

from ..core.config import get_settings

settings = get_settings()

# Firebase will be initialized only if credentials are provided
firebase_app = None
if settings.fcm_enabled and settings.fcm_credentials_path:
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging

        cred = credentials.Certificate(settings.fcm_credentials_path)
        firebase_app = firebase_admin.initialize_app(cred)
        logger.info("🔥 Firebase initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Firebase initialization failed: {str(e)}")


class PushService:
    """Service for sending push notifications via Firebase Cloud Messaging"""

    @staticmethod
    async def send_push_notification(
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send push notification via FCM"""

        # Check if FCM is enabled and initialized
        if not settings.fcm_enabled or not firebase_app:
            logger.warning("📱 FCM not configured - push notification skipped")
            return False

        try:
            from firebase_admin import messaging

            # Build message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=device_token,
            )

            # Send message
            response = messaging.send(message)
            logger.info(f"✅ Push notification sent successfully: {response}")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending push notification: {str(e)}")
            return False

    @staticmethod
    async def send_attendance_push(
        device_token: str,
        user_name: str,
        course_name: str,
        status: str
    ) -> bool:
        """Send attendance confirmation push notification"""

        title = "Asistencia Registrada ✅"
        body = f"Tu asistencia en {course_name} ha sido registrada como {status.upper()}"

        data = {
            "type": "attendance_confirmation",
            "course_name": course_name,
            "status": status
        }

        return await PushService.send_push_notification(device_token, title, body, data)

    @staticmethod
    async def send_course_reminder(
        device_token: str,
        course_name: str,
        start_time: str
    ) -> bool:
        """Send course reminder push notification"""

        title = f"Recordatorio: {course_name}"
        body = f"Tu clase comienza en 15 minutos ({start_time})"

        data = {
            "type": "course_reminder",
            "course_name": course_name,
            "start_time": start_time
        }

        return await PushService.send_push_notification(device_token, title, body, data)
