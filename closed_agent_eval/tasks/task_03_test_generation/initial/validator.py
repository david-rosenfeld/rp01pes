"""Input validation utilities."""

import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate US phone number format (XXX-XXX-XXXX)."""
    pattern = r'^\d{3}-\d{3}-\d{4}$'
    return bool(re.match(pattern, phone))


def validate_password(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain an uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain a lowercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain a digit")

    return len(errors) == 0, errors
