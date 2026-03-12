"""
Email Service — DEPRECATED

Email notifications are now handled externally via Microsoft Power Automate.
This file is kept as a stub to avoid import errors from any legacy references.

See: .agents/workflows/power-automate-email-setup.md for setup instructions.
"""
import logging

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body_html: str, body_text: str = None) -> bool:
        """
        DEPRECATED: Email sending is now handled by Power Automate.
        This stub logs the call and returns False.
        """
        logger.warning(
            f"EmailService.send_email() called but email sending is disabled. "
            f"Use Power Automate instead. (to: {to_email}, subject: {subject})"
        )
        return False
