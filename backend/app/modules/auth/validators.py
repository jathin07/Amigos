from pydantic import ValidationError
from app.domain.exceptions import ValidationException

def validate_request(dto_class, data):
    try:
        return dto_class(**data)
    except ValidationError as e:
        errors = []
        for err in e.errors():
            loc = ".".join([str(l) for l in err["loc"]])
            msg = err["msg"]
            errors.append({"field": loc, "message": msg})
            
        raise ValidationException(
            message="Invalid request payload",
            validation_errors=errors
        )
