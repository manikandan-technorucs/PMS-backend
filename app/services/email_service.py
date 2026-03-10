import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body_html: str, body_text: str = None) -> bool:
        """
        Sends an email using the configured provider (SendGrid or SMTP).
        """
        provider = settings.EMAIL_PROVIDER.lower()
        
        if provider == "sendgrid":
            if not settings.SENDGRID_API_KEY:
                logger.error("SendGrid API key is missing. Email skipped.")
                return False

            message = Mail(
                from_email=settings.EMAIL_FROM,
                to_emails=to_email,
                subject=subject,
                html_content=body_html,
                plain_text_content=body_text
            )
            try:
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                logger.info(f"Email successfully sent via SendGrid. Status: {response.status_code}")
                return response.status_code >= 200 and response.status_code < 300
            except Exception as e:
                logger.error(f"Failed to send email via SendGrid: {str(e)}")
                raise e 
        
        elif provider == "smtp":
            if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
                logger.error("SMTP configuration is incomplete. Email skipped.")
                return False
                
            try:
                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = settings.EMAIL_FROM
                message["To"] = to_email

                if body_text:
                    message.attach(MIMEText(body_text, "plain"))
                if body_html:
                    message.attach(MIMEText(body_html, "html"))

                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())
                
                logger.info(f"Email successfully sent via SMTP ({settings.SMTP_HOST})")
                return True
            except smtplib.SMTPAuthenticationError as e:
                error_msg = str(e)
                if "535" in error_msg:
                    logger.error(
                        f"SMTP Authentication Failed (535). "
                        "This is likely due to MFA being enabled (requires an App Password) "
                        "or SMTP AUTH being disabled for this account in Microsoft 365. "
                        f"Details: {error_msg}"
                    )
                else:
                    logger.error(f"SMTP Authentication Error: {error_msg}")
                raise e
            except Exception as e:
                logger.error(f"Failed to send email via SMTP: {str(e)}")
                raise e
        else:
            logger.error(f"Missing implementation for email provider: {settings.EMAIL_PROVIDER}")
            return False
