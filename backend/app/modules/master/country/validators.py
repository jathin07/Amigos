from app.validators.common import validate_code, validate_display_order
from app.domain.exceptions import ValidationException

def validate_country_data(data: dict):
    if "code" in data:
        data["code"] = validate_code(data["code"], max_length=50)
    if "display_order" in data:
        data["display_order"] = validate_display_order(data["display_order"])
    return data
