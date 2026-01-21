"""
Security Utilities

Provides security-related utility functions.
"""

import secrets
import hashlib
import hmac
import re
from typing import Optional, Tuple
from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password validation regex
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def generate_api_key(prefix: str = "saiad") -> Tuple[str, str]:
    """
    Generate an API key with a prefix.

    Returns:
        Tuple of (api_key, hashed_key)
    """
    raw_key = secrets.token_urlsafe(32)
    api_key = f"{prefix}_{raw_key}"
    hashed_key = hash_api_key(api_key)
    return api_key, hashed_key


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return hmac.compare_digest(
        hash_api_key(api_key),
        hashed_key
    )


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[@$!%*?&]", password):
        return False, "Password must contain at least one special character (@$!%*?&)"

    return True, None


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.

    Returns:
        Token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Removes or escapes potentially dangerous characters.
    """
    if not input_string:
        return ""

    # Remove null bytes
    sanitized = input_string.replace("\x00", "")

    # Escape HTML entities
    sanitized = (
        sanitized
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )

    return sanitized


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    return bool(pattern.match(email))


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data, keeping only first and last few characters visible.

    Example: "1234567890" -> "1234****7890"
    """
    if len(data) <= visible_chars * 2:
        return "*" * len(data)

    return f"{data[:visible_chars]}****{data[-visible_chars:]}"


def generate_csrf_token() -> str:
    """Generate a CSRF token."""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected_token: str) -> bool:
    """Verify a CSRF token using constant-time comparison."""
    return hmac.compare_digest(token, expected_token)


class PasswordValidator:
    """Password validation with configurable rules."""

    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        special_chars: str = "@$!%*?&",
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.special_chars = special_chars

    def validate(self, password: str) -> Tuple[bool, list]:
        """
        Validate password and return list of failures.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if len(password) < self.min_length:
            errors.append(f"Must be at least {self.min_length} characters")

        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Must contain an uppercase letter")

        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Must contain a lowercase letter")

        if self.require_digit and not re.search(r"\d", password):
            errors.append("Must contain a digit")

        if self.require_special:
            special_pattern = f"[{re.escape(self.special_chars)}]"
            if not re.search(special_pattern, password):
                errors.append(f"Must contain a special character ({self.special_chars})")

        return len(errors) == 0, errors


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    """
    return hmac.compare_digest(a.encode(), b.encode())
