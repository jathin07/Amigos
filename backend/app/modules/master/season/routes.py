from flask import request
from marshmallow import ValidationError
from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (CreateSeasonRequestSchema, UpdateSeasonRequestSchema,
    SeasonSummaryResponseSchema, SeasonDetailResponseSchema, SeasonLookupResponseSchema)
from .service import SeasonService
from flask import Blueprint

season_bp = Blueprint("season", __name__, url_prefix="/api/v1/masters/seasons")

def _flatten_errors(messages):
    return [{"code": "ERR_VALIDATION", "field": f, "message": m}
            for f, msgs in messages.items() for m in (msgs if isinstance(msgs, list) else [msgs])]

@season_bp.route("", methods=["POST"])
@permission_required("master.season.create")
def create_season():
    service = SeasonService()
    try: data = CreateSeasonRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.create(data)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    resp, status = service.success(data=SeasonDetailResponseSchema().dump(entity), message="Season created.", status_code=201)
    resp.headers["Location"] = f"/api/v1/masters/seasons/{entity.id}"
    return resp, status

@season_bp.route("", methods=["GET"])
@permission_required("master.season.read")
def list_seasons():
    service = SeasonService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "display_order")
    sort_order = request.args.get("sort_order", "asc")
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"
    result = service.list(page=page, page_size=page_size, search=search, is_active=is_active, sort_by=sort_by, sort_order=sort_order)
    return service.success(data={"items": SeasonSummaryResponseSchema(many=True).dump(result.items), "pagination": {"page": result.page, "page_size": result.page_size, "total_records": result.total_records, "total_pages": result.total_pages}}, message="Seasons retrieved.")

@season_bp.route("/lookup", methods=["GET"])
@permission_required("master.season.read")
def lookup_seasons():
    service = SeasonService()
    result = service.list(page=1, page_size=200, search=request.args.get("search"), is_active=True, sort_by="name", sort_order="asc")
    return service.success(data=SeasonLookupResponseSchema(many=True).dump(result.items), message="Seasons lookup.")

@season_bp.route("/<id>", methods=["GET"])
@permission_required("master.season.read")
def get_season(id):
    service = SeasonService()
    try: entity = service.get(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    return service.success(data=SeasonDetailResponseSchema().dump(entity), message="Season retrieved.")

@season_bp.route("/<id>", methods=["PUT"])
@permission_required("master.season.update")
def update_season(id):
    service = SeasonService()
    try: data = UpdateSeasonRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.update(id, data)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except (DomainException, BusinessException) as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(data=SeasonDetailResponseSchema().dump(entity), message="Season updated.")

@season_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.season.delete")
def delete_season(id):
    service = SeasonService()
    try: service.delete(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(message="Season deactivated.")
