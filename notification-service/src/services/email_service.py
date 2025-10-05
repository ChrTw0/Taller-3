"""Email service using SMTP"""
from typing import Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger

from ..core.config import get_settings

settings = get_settings()


class EmailService:
    """Service for sending emails via SMTP"""

    @staticmethod
    async def send_email(
        recipient_email: str,
        subject: str,
        body: str,
        body_html: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""

        # Check if SMTP is configured
        if not settings.smtp_username or not settings.smtp_password:
            logger.warning("📧 SMTP not configured - email sending skipped")
            return False

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
            message["To"] = recipient_email

            # Add plain text body
            part1 = MIMEText(body, "plain")
            message.attach(part1)

            # Add HTML body if provided
            if body_html:
                part2 = MIMEText(body_html, "html")
                message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                start_tls=True,
                timeout=30
            )

            logger.info(f"✅ Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending email to {recipient_email}: {str(e)}")
            return False

    @staticmethod
    async def send_attendance_confirmation(
        recipient_email: str,
        user_name: str,
        course_name: str,
        attendance_date: str
    ) -> bool:
        """Send attendance confirmation email"""

        subject = f"Asistencia Registrada - {course_name}"

        body = f"""
Hola {user_name},

Tu asistencia ha sido registrada exitosamente.

Curso: {course_name}
Fecha: {attendance_date}

¡Gracias por usar GeoAttend!

---
GeoAttend - Sistema de Asistencia por GPS
        """

        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✅ Asistencia Registrada</h2>
        </div>
        <div class="content">
            <p>Hola <strong>{user_name}</strong>,</p>
            <p>Tu asistencia ha sido registrada exitosamente.</p>
            <p><strong>Curso:</strong> {course_name}</p>
            <p><strong>Fecha:</strong> {attendance_date}</p>
            <p>¡Gracias por usar GeoAttend!</p>
        </div>
        <div class="footer">
            GeoAttend - Sistema de Asistencia por GPS
        </div>
    </div>
</body>
</html>
        """

        return await EmailService.send_email(recipient_email, subject, body, body_html)
