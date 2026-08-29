import uuid
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity, get_jwt, verify_jwt_in_request

from app.core.extensions import db
from app.modules.auth.permissions import login_required, role_required
from app.domain.exceptions import ValidationException, AuthorizationException, NotFoundException
from .schemas import PresignedUrlRequestSchema, DeleteObjectRequestSchema
from .service import R2StorageService

storage_bp = Blueprint("storage", __name__)

def _flatten_errors(messages) -> list[dict]:
    if isinstance(messages, str):
        return [{"code": "ERR_VALIDATION", "message": messages}]
    if isinstance(messages, list):
        return [{"code": "ERR_VALIDATION", "message": str(msg)} for msg in messages]
    errors = []
    for field, msgs in messages.items():
        if isinstance(msgs, dict):
            for subfield, submsgs in msgs.items():
                for submsg in (submsgs if isinstance(submsgs, list) else [submsgs]):
                    errors.append({"code": "ERR_VALIDATION", "field": f"{field}.{subfield}", "message": str(submsg)})
        elif isinstance(msgs, list):
            for item in msgs:
                if isinstance(item, dict):
                    for subfield, submsgs in item.items():
                        for submsg in (submsgs if isinstance(submsgs, list) else [submsgs]):
                            errors.append({"code": "ERR_VALIDATION", "field": f"{field}.{subfield}", "message": str(submsg)})
                else:
                    errors.append({"code": "ERR_VALIDATION", "field": field, "message": str(item)})
        else:
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": str(msgs)})
    return errors

def _get_context_team_member_id() -> uuid.UUID | None:
    """Safely retrieves current user team_member_id context."""
    try:
        identity = get_jwt_identity()
    except RuntimeError:
        identity = None
    if not identity:
        return None
    try:
        from app.models import UserAccount
        user = db.session.get(UserAccount, uuid.UUID(str(identity)))
        return user.team_member_id if user else None
    except Exception:
        return None

@storage_bp.route("/presign", methods=["POST"])
@login_required()
def generate_presigned_url():
    payload = request.get_json(silent=True) or {}
    try:
        data = PresignedUrlRequestSchema().load(payload)
        PresignedUrlRequestSchema.validate_rules(data)
    except ValidationError as err:
        return jsonify({
            "status": "error",
            "message": "Request validation failed.",
            "code": "VALIDATION_ERROR",
            "errors": _flatten_errors(err.messages)
        }), 422
    except ValidationException as err:
        return jsonify({
            "status": "error",
            "message": err.message,
            "code": "VALIDATION_ERROR"
        }), 400

    actor_id = _get_context_team_member_id()
    service = R2StorageService()
    try:
        result = service.generate_presigned_url(
            folder=data["folder"],
            filename=data["filename"],
            content_type=data["content_type"],
            file_size=data["file_size"],
            actor_id=actor_id
        )
        return jsonify({
            "status": "success",
            "message": "Presigned upload URL generated successfully.",
            "data": result
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": "INTERNAL_SERVER_ERROR"
        }), 500

@storage_bp.route("/complete", methods=["POST"])
@login_required()
def complete_upload():
    payload = request.get_json(silent=True) or {}
    object_key = payload.get("object_key")
    if not object_key:
        return jsonify({
            "status": "error",
            "message": "object_key is required.",
            "code": "VALIDATION_ERROR"
        }), 422

    actor_id = _get_context_team_member_id()
    service = R2StorageService()
    try:
        file_record = service.complete_upload(object_key, actor_id)
        return jsonify({
            "status": "success",
            "message": "Storage object upload marked completed.",
            "data": {
                "object_key": file_record.object_key,
                "original_filename": file_record.original_filename,
                "file_size": file_record.file_size,
                "content_type": file_record.content_type,
                "namespace": file_record.namespace,
                "is_completed": file_record.is_completed,
                "completed_at": file_record.completed_at.isoformat() if file_record.completed_at else None
            }
        }), 200
    except NotFoundException as err:
        return jsonify({
            "status": "error",
            "message": err.message,
            "code": "NOT_FOUND"
        }), 404
    except ValidationException as err:
        return jsonify({
            "status": "error",
            "message": err.message,
            "code": "VALIDATION_ERROR"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": "INTERNAL_SERVER_ERROR"
        }), 500

@storage_bp.route("/object", methods=["DELETE"])
@login_required()
def delete_object():
    payload = request.get_json(silent=True) or {}
    try:
        data = DeleteObjectRequestSchema().load(payload)
    except ValidationError as err:
        return jsonify({
            "status": "error",
            "message": "Request validation failed.",
            "code": "VALIDATION_ERROR",
            "errors": _flatten_errors(err.messages)
        }), 422

    actor_id = _get_context_team_member_id()
    claims = get_jwt()
    user_permissions = set(claims.get("permissions", []))
    user_role = claims.get("role")

    service = R2StorageService()
    try:
        service.delete_object(
            object_key=data["object_key"],
            actor_id=actor_id,
            user_permissions=user_permissions,
            user_role=user_role
        )
        return jsonify({
            "status": "success",
            "message": "Storage object deleted successfully."
        }), 200
    except NotFoundException as err:
        return jsonify({
            "status": "error",
            "message": err.message,
            "code": "NOT_FOUND"
        }), 404
    except AuthorizationException as err:
        return jsonify({
            "status": "error",
            "message": err.message,
            "code": "UNAUTHORIZED"
        }), 403
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": "INTERNAL_SERVER_ERROR"
        }), 500

@storage_bp.route("/download", methods=["GET"])
@login_required()
def generate_download_url():
    object_key = request.args.get("object_key")
    if not object_key:
        return jsonify({
            "status": "error",
            "message": "object_key query parameter is required.",
            "code": "VALIDATION_ERROR"
        }), 400

    actor_id = _get_context_team_member_id()
    service = R2StorageService()
    try:
        result = service.generate_download_url(object_key, actor_id)
        return jsonify({
            "status": "success",
            "message": "Download URL generated successfully.",
            "data": result
        }), 200
    except NotFoundException as err:
        return jsonify({
            "status": "error",
            "message": err.message,
            "code": "NOT_FOUND"
        }), 404
    except ValidationException as err:
        return jsonify({
            "status": "error",
            "message": err.message,
            "code": "VALIDATION_ERROR"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": "INTERNAL_SERVER_ERROR"
        }), 500

@storage_bp.route("/cleanup", methods=["POST"])
@role_required("Admin")
def cleanup_orphans():
    hours = request.args.get("hours", 24, type=int)
    service = R2StorageService()
    try:
        deleted_count = service.cleanup_orphans(hours)
        return jsonify({
            "status": "success",
            "message": f"Orphan storage objects cleanup completed.",
            "data": {
                "deleted_count": deleted_count
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": "INTERNAL_SERVER_ERROR"
        }), 500
