from marshmallow import Schema, fields, validate, ValidationError

# Supported Upload Folders and Rules
UPLOAD_RULES = {
    # Public folders
    "public/team": {
        "max_size_mb": 5,
        "allowed_mimes": {"image/jpeg", "image/png", "image/webp", "image/gif"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    },
    "public/customers": {
        "max_size_mb": 5,
        "allowed_mimes": {"image/jpeg", "image/png", "image/webp", "image/gif"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    },
    "public/places": {
        "max_size_mb": 10,
        "allowed_mimes": {"image/jpeg", "image/png", "image/webp"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp"}
    },
    "public/trip": {
        "max_size_mb": 20,
        "allowed_mimes": {"image/jpeg", "image/png", "image/webp", "application/pdf"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
    },
    "public/packages": {
        "max_size_mb": 10,
        "allowed_mimes": {"image/jpeg", "image/png", "image/webp"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp"}
    },
    # Private folders
    "private/passports": {
        "max_size_mb": 10,
        "allowed_mimes": {"image/jpeg", "image/png", "application/pdf"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".pdf"}
    },
    "private/invoices": {
        "max_size_mb": 15,
        "allowed_mimes": {"image/jpeg", "image/png", "application/pdf"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".pdf"}
    },
    "private/contracts": {
        "max_size_mb": 25,
        "allowed_mimes": {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        "allowed_extensions": {".pdf", ".docx"}
    },
    "private/kyc": {
        "max_size_mb": 10,
        "allowed_mimes": {"image/jpeg", "image/png", "application/pdf"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".pdf"}
    },
    "private/documents": {
        "max_size_mb": 25,
        "allowed_mimes": {"image/jpeg", "image/png", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".pdf", ".docx"}
    }
}

class PresignedUrlRequestSchema(Schema):
    folder = fields.String(required=True, validate=validate.OneOf(list(UPLOAD_RULES.keys())))
    filename = fields.String(required=True, validate=validate.Length(min=1, max=255))
    content_type = fields.String(required=True, validate=validate.Length(min=3, max=100))
    file_size = fields.Integer(required=True, validate=validate.Range(min=1))

    # Helper method to validate folder rules
    @staticmethod
    def validate_rules(data):
        folder = data["folder"]
        filename = data["filename"]
        content_type = data["content_type"]
        file_size = data["file_size"]

        rules = UPLOAD_RULES.get(folder)
        if not rules:
            raise ValidationError({"folder": "Disallowed upload folder."})

        # Extract extension securely
        import os
        _, ext = os.path.splitext(filename.lower())
        if not ext or ext not in rules["allowed_extensions"]:
            raise ValidationError(
                {"filename": f"File extension '{ext}' is not allowed for folder '{folder}'. Allowed: {sorted(list(rules['allowed_extensions']))}"}
            )

        # Validate MIME Content-Type
        if content_type.lower() not in rules["allowed_mimes"]:
            raise ValidationError(
                {"content_type": f"Content type '{content_type}' is not allowed for folder '{folder}'. Allowed: {sorted(list(rules['allowed_mimes']))}"}
            )

        # Validate file size (convert rules MB to bytes)
        max_bytes = rules["max_size_mb"] * 1024 * 1024
        if file_size > max_bytes:
            raise ValidationError(
                {"file_size": f"File size exceeds limit of {rules['max_size_mb']}MB for folder '{folder}'."}
            )


class DeleteObjectRequestSchema(Schema):
    object_key = fields.String(required=True, validate=validate.Length(min=1, max=1000))
