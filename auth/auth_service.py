"""
Authentication Service - Supabase Backend
Handles user authentication, token management, and user operations
"""

import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any, List
from argon2 import PasswordHasher
import requests
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SECRET_KEY = os.getenv('SUPABASE_SECRET_KEY')

ph = PasswordHasher()


class AuthService:
    """Authentication service using Supabase backend"""

    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

    # ==================== Core Authentication ====================

    def check_usr_pass(self, username: str, password: str) -> bool:
        """Authenticate user credentials against Supabase"""
        try:
            result = self.supabase.table('users').select('password_hash, is_active').eq('username', username).execute()

            if not result.data:
                return False

            user = result.data[0]
            if not user.get('is_active', False):
                return False

            return ph.verify(user['password_hash'], password)
        except Exception:
            return False

    def update_last_login(self, username: str) -> None:
        """Update the last login timestamp for a user"""
        try:
            self.supabase.table('users').update({
                'last_login': datetime.now(timezone.utc).isoformat()
            }).eq('username', username).execute()
        except Exception:
            pass

    # ==================== User Retrieval ====================

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            result = self.supabase.table('users').select('*').eq('username', username).execute()
            return result.data[0] if result.data else None
        except Exception:
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            result = self.supabase.table('users').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception:
            return None

    def is_user_admin(self, username: str) -> bool:
        """Check if user is an admin"""
        user = self.get_user_by_username(username)
        return user.get('is_admin', False) if user else False

    def get_all_users(self) -> List[Dict]:
        """Get all users (admin function)"""
        try:
            result = self.supabase.table('users').select('*').order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception:
            return []

    # ==================== Uniqueness Checks ====================

    def check_unique_usr(self, username: str) -> bool:
        """Check if username is unique (returns True if unique)"""
        try:
            result = self.supabase.table('users').select('user_id').eq('username', username).execute()
            return len(result.data) == 0
        except Exception:
            return False

    def check_unique_email(self, email: str) -> bool:
        """Check if email is unique (returns True if unique)"""
        try:
            result = self.supabase.table('users').select('user_id').eq('email', email).execute()
            return len(result.data) == 0
        except Exception:
            return False

    def check_email_exists(self, email: str) -> Tuple[bool, Optional[str]]:
        """Check if email exists and return username if found"""
        user = self.get_user_by_email(email)
        if user:
            return True, user.get('username')
        return False, None

    def check_username_exists(self, username: str) -> bool:
        """Check if username exists"""
        return self.get_user_by_username(username) is not None

    # ==================== Token Management ====================

    def generate_account_creation_token(self, email: str, name: str, username: str,
                                         created_by_user_id: Optional[str] = None,
                                         expiry_hours: int = 24) -> str:
        """Generate token for admin-initiated account creation"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)

        self.supabase.table('verification_tokens').insert({
            'email': email,
            'token': token,
            'token_type': 'account_creation',
            'name': name,
            'username': username,
            'expires_at': expires_at.isoformat(),
            'created_by': created_by_user_id
        }).execute()

        return token

    def generate_password_reset_token(self, email: str, expiry_hours: int = 1) -> str:
        """Generate token for password reset"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)

        self.supabase.table('verification_tokens').insert({
            'email': email,
            'token': token,
            'token_type': 'password_reset',
            'expires_at': expires_at.isoformat()
        }).execute()

        return token

    def validate_token(self, email: str, token: str, token_type: str) -> Tuple[bool, Optional[Dict]]:
        """Validate a verification token"""
        try:
            result = self.supabase.table('verification_tokens').select('*').eq('email', email).eq('token', token).eq('token_type', token_type).is_('used_at', 'null').execute()

            if not result.data:
                return False, None

            token_data = result.data[0]
            expires_at_str = token_data['expires_at']

            # Parse the timestamp
            if expires_at_str.endswith('Z'):
                expires_at_str = expires_at_str[:-1] + '+00:00'
            expires_at = datetime.fromisoformat(expires_at_str)

            now = datetime.now(timezone.utc)
            if now > expires_at:
                return False, None

            return True, token_data
        except Exception:
            return False, None

    def mark_token_used(self, token: str) -> bool:
        """Mark a token as used"""
        try:
            self.supabase.table('verification_tokens').update({
                'used_at': datetime.now(timezone.utc).isoformat()
            }).eq('token', token).execute()
            return True
        except Exception:
            return False

    def cleanup_expired_tokens(self) -> int:
        """Delete expired tokens (maintenance function)"""
        try:
            now = datetime.now(timezone.utc).isoformat()
            result = self.supabase.table('verification_tokens').delete().lt('expires_at', now).execute()
            return len(result.data) if result.data else 0
        except Exception:
            return 0

    # ==================== User Creation ====================

    def create_user_from_token(self, email: str, token: str, password: str) -> Tuple[bool, str]:
        """Create user after token validation"""
        is_valid, token_data = self.validate_token(email, token, 'account_creation')

        if not is_valid or not token_data:
            return False, "Invalid or expired token"

        # Check username and email uniqueness again
        if not self.check_unique_usr(token_data['username']):
            return False, "Username already taken"
        if not self.check_unique_email(email):
            return False, "Email already registered"

        try:
            # Create user
            self.supabase.table('users').insert({
                'username': token_data['username'],
                'name': token_data['name'],
                'email': email,
                'password_hash': ph.hash(password),
                'is_admin': False,
                'is_active': True
            }).execute()

            # Mark token as used
            self.mark_token_used(token)

            return True, "Account created successfully"
        except Exception as e:
            return False, f"Failed to create account: {str(e)}"

    def register_new_usr(self, name: str, email: str, username: str, password: str) -> Tuple[bool, str]:
        """Direct user registration (for migration or admin use)"""
        try:
            self.supabase.table('users').insert({
                'username': username,
                'name': name,
                'email': email,
                'password_hash': ph.hash(password),
                'is_admin': False,
                'is_active': True
            }).execute()
            return True, "User registered successfully"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"

    # ==================== Password Management ====================

    def change_password(self, email: str, new_password: str) -> bool:
        """Update user password"""
        try:
            self.supabase.table('users').update({
                'password_hash': ph.hash(new_password),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).eq('email', email).execute()
            return True
        except Exception:
            return False

    def check_current_passwd(self, email: str, current_password: str) -> bool:
        """Verify current password"""
        user = self.get_user_by_email(email)
        if not user:
            return False
        try:
            return ph.verify(user['password_hash'], current_password)
        except Exception:
            return False

    # ==================== Admin Functions ====================

    def set_user_admin_status(self, user_id: str, is_admin: bool) -> bool:
        """Set user admin status"""
        try:
            self.supabase.table('users').update({
                'is_admin': is_admin,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).eq('user_id', user_id).execute()
            return True
        except Exception:
            return False

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        try:
            self.supabase.table('users').update({
                'is_active': False,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).eq('user_id', user_id).execute()
            return True
        except Exception:
            return False


# ==================== Singleton Instance ====================

_auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """Get singleton auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


# ==================== Standalone Helper Functions ====================
# (for backward compatibility with existing code)

def check_usr_pass(username: str, password: str) -> bool:
    """Authenticates the username and password."""
    return get_auth_service().check_usr_pass(username, password)

def check_valid_name(name_sign_up: str) -> Optional[str]:
    """
    Validates the user's name during account creation.
    Returns None if valid, otherwise a string describing what is invalid.
    """
    name_regex = r'^[A-Za-z_][A-Za-z0-9_ ]*$'

    if not name_sign_up:
        return "Name cannot be empty."

    if not re.match(name_regex, name_sign_up):
        return (
            "Name must start with a letter or underscore and contain "
            "only letters, numbers, spaces, or underscores."
        )

    return None

def check_valid_email(email: str) -> Optional[str]:
    """
    Checks if the email is valid.
    Returns None if valid, otherwise returns a string explaining why it's invalid.
    """
    if not email or email.strip() == "":
        return "Email cannot be empty!"

    email = email.strip()

    regex = re.compile(r'([A-Za-z0-9]+[._-])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+')
    if not re.fullmatch(regex, email):
        return "Email format is invalid! It should have the structure: example@mail.com"

    return None

def check_unique_email(email_sign_up: str) -> bool:
    """Checks if the email already exists (returns True if unique)."""
    return get_auth_service().check_unique_email(email_sign_up)

def non_empty_str_check(username_sign_up: str) -> bool:
    """Checks for non-empty strings."""
    if not username_sign_up:
        return False
    return username_sign_up.strip() != ''

def check_unique_usr(username_sign_up: str) -> Optional[bool]:
    """
    Checks if the username already exists (since username needs to be unique),
    also checks for non-empty username.
    """
    if not non_empty_str_check(username_sign_up):
        return None
    return get_auth_service().check_unique_usr(username_sign_up)

def register_new_usr(name_sign_up: str, email_sign_up: str, username_sign_up: str, password_sign_up: str) -> None:
    """Saves the information of the new user."""
    get_auth_service().register_new_usr(name_sign_up, email_sign_up, username_sign_up, password_sign_up)

def check_username_exists(user_name: str) -> bool:
    """Checks if the username exists."""
    return get_auth_service().check_username_exists(user_name)

def check_email_exists(email_forgot_passwd: str) -> Tuple[bool, Optional[str]]:
    """Checks if the email entered is present in the database."""
    return get_auth_service().check_email_exists(email_forgot_passwd)

def generate_random_passwd() -> str:
    """Generates a random password to be sent in email."""
    return secrets.token_urlsafe(10)

def change_passwd(email_: str, random_password: str) -> None:
    """Replaces the old password with the newly generated password."""
    get_auth_service().change_password(email_, random_password)

def check_current_passwd(email_reset_passwd: str, current_passwd: str) -> bool:
    """Authenticates the password entered against the username when resetting the password."""
    return get_auth_service().check_current_passwd(email_reset_passwd, current_passwd)

def load_lottie(url: str) -> Optional[dict]:
    """Load Lottie animation from URL"""
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Lottie load failed: {e}")
        return None
