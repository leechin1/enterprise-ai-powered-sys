"""
Email Service - EmailJS Integration for Enterprise System
Handles email sending with placebo mode for development/testing
All emails are sent to the configured recipient but store the intended recipient in subject
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Import centralized config
from services.config import EmailConfig

load_dotenv()

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service using EmailJS for sending emails.
    In placebo mode, all emails are sent to a single recipient (your email)
    with the original recipient stored in the subject line for tracking.
    """

    def __init__(self):
        # Use centralized config
        self.service_id = EmailConfig.SERVICE_ID
        self.template_id = EmailConfig.TEMPLATE_ID
        self.public_key = EmailConfig.PUBLIC_KEY
        self.private_key = EmailConfig.PRIVATE_KEY
        self.placebo_email = EmailConfig.PLACEBO_EMAIL
        self.placebo_mode = EmailConfig.PLACEBO_MODE
        self.api_url = EmailConfig.API_URL
        self.request_timeout = EmailConfig.REQUEST_TIMEOUT

        # Default external email - all external communications go here
        self.default_external_email = EmailConfig.DEFAULT_EXTERNAL_EMAIL

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate that required configuration is present"""
        missing = []
        if not self.service_id:
            missing.append('EMAILJS_SERVICE_ID')
        if not self.template_id:
            missing.append('EMAILJS_TEMPLATE_ID')
        if not self.public_key:
            missing.append('EMAILJS_PUBLIC_KEY')
        if self.placebo_mode and not self.placebo_email:
            missing.append('PLACEBO_EMAIL')

        if missing:
            logger.warning(f"Email service missing configuration: {', '.join(missing)}")

    def is_configured(self) -> bool:
        """Check if the email service is properly configured"""
        required = [self.service_id, self.template_id, self.public_key]
        if self.placebo_mode:
            required.append(self.placebo_email)
        return all(required)

    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body: str,
        email_type: str = "notification",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send an email using EmailJS.

        In placebo mode:
        - Email is sent to PLACEBO_EMAIL instead of to_email
        - Original recipient is stored in subject: "[PLACEBO: original@email.com] Original Subject"

        Args:
            to_email: Intended recipient email
            to_name: Recipient name
            subject: Email subject
            body: Email body content
            email_type: Type of email (customer_notification, inventory_alert, etc.)
            metadata: Optional additional metadata

        Returns:
            Result dict with success status and details
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Email service not configured. Please set EmailJS credentials in .env",
                "sent": False
            }

        try:
            # Route all external emails to the default external email address
            # This prevents AI from sending to invented/fake email addresses
            # In placebo mode, use placebo email; otherwise use default external email
            if self.placebo_mode:
                actual_to_email = self.placebo_email
                actual_subject = f"[PLACEBO: {to_email}] {subject}"
                actual_name = f"[Test] {to_name}"
            else:
                # Production: all emails go to default external email
                actual_to_email = self.default_external_email
                actual_subject = f"[To: {to_email}] {subject}"  # Subject stays dynamic, includes intended recipient
                actual_name = to_name

            # Prepare the request payload for EmailJS
            # Template variables must match your EmailJS template:
            # {{subject}}, {{name}}, {{time}}, {{message}}, {{email}}
            template_params = {
                "subject": actual_subject,
                "name": actual_name,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": body,
                "email": to_email,  # Original email for reply-to
            }

            # Add any additional metadata
            if metadata:
                template_params["metadata"] = str(metadata)

            payload = {
                "service_id": self.service_id,
                "template_id": self.template_id,
                "user_id": self.public_key,
                "template_params": template_params,
                "accessToken": self.private_key  # Required for server-side calls
            }

            # Headers for server-side API call
            headers = {
                "Content-Type": "application/json",
                "origin": EmailConfig.CORS_ORIGIN  # Required for CORS
            }

            # Send the request using centralized config
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.request_timeout
            )

            if response.status_code == 200:
                logger.info(f"Email sent successfully to {actual_to_email} (original: {to_email})")
                return {
                    "success": True,
                    "sent": True,
                    "placebo_mode": self.placebo_mode,
                    "actual_recipient": actual_to_email,
                    "original_recipient": to_email,
                    "subject": actual_subject,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = f"EmailJS returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "sent": False
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Email service timeout",
                "sent": False
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "sent": False
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return {
                "success": False,
                "error": str(e),
                "sent": False
            }

    def send_bulk_emails(
        self,
        emails: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send multiple emails.

        Args:
            emails: List of email dicts with keys: to_email, to_name, subject, body, email_type

        Returns:
            Result dict with overall success status and individual results
        """
        results = []
        success_count = 0
        failure_count = 0

        for email in emails:
            result = self.send_email(
                to_email=email.get("to_email", ""),
                to_name=email.get("to_name", "Customer"),
                subject=email.get("subject", "Notification from Misty Jazz Records"),
                body=email.get("body", ""),
                email_type=email.get("email_type", "notification"),
                metadata=email.get("metadata")
            )

            results.append({
                "to_email": email.get("to_email"),
                "result": result
            })

            if result["success"]:
                success_count += 1
            else:
                failure_count += 1

        return {
            "success": failure_count == 0,
            "total": len(emails),
            "sent": success_count,
            "failed": failure_count,
            "results": results,
            "placebo_mode": self.placebo_mode
        }

    def send_fix_emails(
        self,
        generated_emails: List[Dict[str, Any]],
        recipients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send all emails associated with a fix proposal.

        Args:
            generated_emails: List of pre-generated emails from the fix
            recipients: List of recipients with their details

        Returns:
            Result dict with sending status
        """
        # Create a mapping of emails to recipient details
        recipient_map = {r.get("email", ""): r for r in recipients}

        emails_to_send = []
        for email in generated_emails:
            recipient_emails = email.get("recipient_emails", [])
            for recipient_email in recipient_emails:
                recipient = recipient_map.get(recipient_email, {})
                emails_to_send.append({
                    "to_email": recipient_email,
                    "to_name": recipient.get("name", "Valued Customer"),
                    "subject": email.get("subject", "Notification from Misty Jazz Records"),
                    "body": email.get("body", ""),
                    "email_type": email.get("email_type", "notification"),
                    "metadata": {
                        "role": recipient.get("role", "customer"),
                        "reason": recipient.get("reason", "")
                    }
                })

        return self.send_bulk_emails(emails_to_send)

    def get_status(self) -> Dict[str, Any]:
        """Get the current status and configuration of the email service"""
        return {
            "configured": self.is_configured(),
            "placebo_mode": self.placebo_mode,
            "placebo_email": self.placebo_email if self.placebo_mode else None,
            "default_external_email": self.default_external_email,
            "service_id": self.service_id[:4] + "..." if self.service_id else None,
            "template_id": self.template_id[:4] + "..." if self.template_id else None,
        }


# Singleton instance
_email_service = None


def get_email_service() -> EmailService:
    """Get the singleton email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
