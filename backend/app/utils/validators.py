import re
from email_validator import validate_email as validate_email_lib, EmailNotValidError
from app.utils.errors import ValidationError

def validate_email(email: str) -> bool:
    """Validate email format and deliverability"""
    try:
        validate_email_lib(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        raise ValidationError(f"Invalid email: {str(e)}")

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character")

    return True

def validate_user_id(user_id: str) -> bool:
    """Validate user ID format"""
    if not user_id or len(user_id) < 3 or len(user_id) > 20:
        raise ValidationError("User ID must be between 3 and 20 characters")

    if not re.match(r'^[A-Za-z0-9_-]+$', user_id):
        raise ValidationError("User ID can only contain letters, numbers, underscores, and hyphens")

    return True

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional

    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)

    if len(digits_only) < 10 or len(digits_only) > 15:
        raise ValidationError("Phone number must be between 10 and 15 digits")

    return True

def validate_name(name: str) -> bool:
    """Validate name format"""
    if not name or len(name.strip()) < 2:
        raise ValidationError("Name must be at least 2 characters long")

    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        raise ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes")

    return True

def validate_department_id(dept_id: str) -> bool:
    """Validate department ID format"""
    if not dept_id or len(dept_id) < 2 or len(dept_id) > 50:
        raise ValidationError("Department ID must be between 2 and 50 characters")

    if not re.match(r'^[A-Za-z0-9_-]+$', dept_id):
        raise ValidationError("Department ID can only contain letters, numbers, underscores, and hyphens")

    return True
