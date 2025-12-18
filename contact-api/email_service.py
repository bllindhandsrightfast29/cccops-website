"""
Email service for sending notifications
Uses SMTP with HTML email templates
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for contact form notifications"""

    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.owner_email = os.getenv("OWNER_EMAIL", "consultingbytriplec@gmail.com")

        # Load email templates
        self.templates_dir = Path(__file__).parent / "templates"
        self.owner_template = self._load_template("owner_notification.html")
        self.customer_template = self._load_template("customer_confirmation.html")

    def _load_template(self, filename: str) -> str:
        """Load email template from file"""
        try:
            template_path = self.templates_dir / filename
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading template {filename}: {e}")
            return ""

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ):
        """Send an email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add text version if provided
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            raise

    async def send_owner_notification(
        self,
        submission_id: int,
        name: str,
        email: str,
        organization: Optional[str],
        message: str
    ):
        """Send notification email to owner about new submission"""
        try:
            # Format the HTML template
            html_content = self.owner_template.format(
                submission_id=submission_id,
                name=name,
                email=email,
                organization=organization or "Not provided",
                message=message.replace('\n', '<br>')
            )

            # Create text version
            text_content = f"""
New Contact Form Submission #{submission_id}

From: {name} ({email})
Organization: {organization or "Not provided"}

Message:
{message}

---
View all submissions: [Your admin dashboard URL]
            """.strip()

            subject = f"New Contact Form Submission #{submission_id} - {name}"

            self._send_email(
                to_email=self.owner_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

        except Exception as e:
            logger.error(f"Error sending owner notification: {e}")
            raise

    async def send_customer_confirmation(
        self,
        name: str,
        email: str
    ):
        """Send confirmation email to customer"""
        try:
            # Format the HTML template
            html_content = self.customer_template.format(
                name=name
            )

            # Create text version
            text_content = f"""
Dear {name},

Thank you for contacting Triple C Consulting. We've received your message and will respond within 24 hours.

If you need immediate assistance, please call us at (509) 903-6285.

Best regards,
Triple C Consulting Team

---
Triple C Consulting
Defense Technology Integration
consultingbytriplec@gmail.com
(509) 903-6285
https://cccops.com
            """.strip()

            subject = "Thank you for contacting Triple C Consulting"

            self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

        except Exception as e:
            logger.error(f"Error sending customer confirmation: {e}")
            raise


# For testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    async def test():
        service = EmailService()

        # Test owner notification
        await service.send_owner_notification(
            submission_id=1,
            name="Test User",
            email="test@example.com",
            organization="Test Corp",
            message="This is a test message\nWith multiple lines"
        )

        # Test customer confirmation
        await service.send_customer_confirmation(
            name="Test User",
            email="test@example.com"
        )

        print("Test emails sent!")

    asyncio.run(test())
