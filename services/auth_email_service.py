"""
Auth Email Service - Email sending for authentication workflows
Uses the existing EmailJS integration from email_service.py
"""

from typing import Dict, Any
from services.email_service import get_email_service, EmailService


class AuthEmailService:
    """Email service for authentication-related emails"""

    def __init__(self):
        self.email_service: EmailService = get_email_service()

    def send_account_invitation(
        self,
        to_email: str,
        to_name: str,
        token: str,
        username: str,
        invited_by: str,
        company_name: str = "Misty Jazz"
    ) -> Dict[str, Any]:
        """
        Send account creation invitation with token.

        Args:
            to_email: Email address to send invitation to
            to_name: Name of the invited user
            token: Verification token
            username: Assigned username for the new user
            invited_by: Name of the admin who created the invitation
            company_name: Company name for branding

        Returns:
            Result dict with success status and details
        """
        subject = f"{company_name}: You've Been Invited to Create an Account"
        body = f"""Hello {to_name},

You have been invited by {invited_by} to create an account on {company_name} Enterprise System.

Your account details:
- Username: {username}
- Email: {to_email}

Your verification token is:

{token}

To complete your registration:
1. Go to the login page
2. Click "Create Account"
3. Enter your email address and the verification token above
4. Choose your password

This token will expire in 24 hours.

If you did not expect this invitation, please ignore this email.

Best regards,
{company_name} Team"""

        return self.email_service.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body=body,
            email_type="account_invitation",
            metadata={
                "username": username,
                "invited_by": invited_by
            }
        )

    def send_password_reset_token(
        self,
        to_email: str,
        to_name: str,
        token: str,
        company_name: str = "Misty Jazz"
    ) -> Dict[str, Any]:
        """
        Send password reset verification token.

        Args:
            to_email: Email address to send token to
            to_name: Name of the user
            token: Verification token
            company_name: Company name for branding

        Returns:
            Result dict with success status and details
        """
        subject = f"{company_name}: Password Reset Verification"
        body = f"""Hello {to_name},

You requested to reset your password on {company_name} Enterprise System.

Your verification token is:

{token}

To reset your password:
1. Go to the Configure tab in your account settings
2. Enter your new password
3. Enter this verification token
4. Click "Confirm Password Change"

This token will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email and ensure your account is secure.

Best regards,
{company_name} Team"""

        return self.email_service.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body=body,
            email_type="password_reset"
        )

    def send_password_change_confirmation(
        self,
        to_email: str,
        to_name: str,
        company_name: str = "Misty Jazz"
    ) -> Dict[str, Any]:
        """
        Send confirmation that password was changed.

        Args:
            to_email: Email address to send confirmation to
            to_name: Name of the user
            company_name: Company name for branding

        Returns:
            Result dict with success status and details
        """
        subject = f"{company_name}: Password Changed Successfully"
        body = f"""Hello {to_name},

Your password for {company_name} Enterprise System has been successfully changed.

If you did not make this change, please contact your administrator immediately.

Best regards,
{company_name} Team"""

        return self.email_service.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body=body,
            email_type="password_change_confirmation"
        )

    def send_account_created_confirmation(
        self,
        to_email: str,
        to_name: str,
        username: str,
        company_name: str = "Misty Jazz"
    ) -> Dict[str, Any]:
        """
        Send confirmation that account was created.

        Args:
            to_email: Email address to send confirmation to
            to_name: Name of the new user
            username: The user's username
            company_name: Company name for branding

        Returns:
            Result dict with success status and details
        """
        subject = f"{company_name}: Welcome! Your Account Has Been Created"
        body = f"""Hello {to_name},

Welcome to {company_name} Enterprise System!

Your account has been created successfully with the following details:
- Username: {username}
- Email: {to_email}

You can now log in and start using the system.

Best regards,
{company_name} Team"""

        return self.email_service.send_email(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body=body,
            email_type="account_created",
            metadata={
                "username": username
            }
        )


# Singleton instance
_auth_email_service = None


def get_auth_email_service() -> AuthEmailService:
    """Get the singleton auth email service instance"""
    global _auth_email_service
    if _auth_email_service is None:
        _auth_email_service = AuthEmailService()
    return _auth_email_service
