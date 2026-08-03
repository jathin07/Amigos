import re
from app.domain.exceptions import ValidationException

def validate_code(code: str, max_length: int = 50) -> str:
    """
    Validates and formats a master code.
    Rules: Uppercase, unique, letters/numbers/underscore only, no spaces.
    """
    if not code:
        raise ValidationException("Code is required")
    
    code = code.strip().upper()
    
    if len(code) > max_length:
        raise ValidationException(f"Code cannot exceed {max_length} characters")
        
    if not re.match(r"^[A-Z0-9_]+$", code):
        raise ValidationException("Code can only contain letters, numbers, and underscores (no spaces)")
        
    return code

def validate_slug(slug: str, max_length: int = 100) -> str:
    """
    Validates a URL-friendly slug.
    Rules: Lowercase, letters/numbers/hyphens only, no spaces.
    """
    if not slug:
        raise ValidationException("Slug is required")
        
    slug = slug.strip().lower()
    
    if len(slug) > max_length:
        raise ValidationException(f"Slug cannot exceed {max_length} characters")
        
    if not re.match(r"^[a-z0-9-]+$", slug):
        raise ValidationException("Slug can only contain lowercase letters, numbers, and hyphens")
        
    return slug

def validate_fk(value: str, field_name: str) -> str:
    """
    Validates that a foreign key is provided and is a string (UUID format).
    Does not verify existence in the DB, only format.
    """
    if not value:
        raise ValidationException(f"{field_name} is required")
    # A simple length check or regex could be added here for strict UUID
    return str(value)

def validate_display_order(order: int) -> int:
    """
    Validates display order is >= 0
    """
    if order is None:
        return 0
    
    try:
        order = int(order)
        if order < 0:
            raise ValidationException("Display order must be greater than or equal to 0")
        return order
    except ValueError:
        raise ValidationException("Display order must be an integer")
