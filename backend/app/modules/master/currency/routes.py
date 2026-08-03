from flask import request
from marshmallow import ValidationError
from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (CreateCurrencyRequestSchema, UpdateCurrencyRequestSchema,
    CurrencySummaryResponseSchema, CurrencyDetailResponseSchema, CurrencyLookupResponseSchema)
from .service import CurrencyService
from flask import Blueprint

currency_bp = Blueprint("currency", __name__, url_prefix="/api/v1/masters/currencies")

def _flatten_errors(messages):
    return [{"code": "ERR_VALIDATION", "field": f, "message": m}
            for f, msgs in messages.items() for m in (msgs if isinstance(msgs, list) else [msgs])]

@currency_bp.route("", methods=["POST"])
@permission_required("master.currency.create")
def create_currency():
    service = CurrencyService()
    try: data = CreateCurrencyRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.create(data)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    resp, status = service.success(data=CurrencyDetailResponseSchema().dump(entity), message="Currency created.", status_code=201)
    resp.headers["Location"] = f"/api/v1/masters/currencies/{entity.id}"
    return resp, status

@currency_bp.route("", methods=["GET"])
@permission_required("master.currency.read")
def list_currencies():
    service = CurrencyService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "display_order")
    sort_order = request.args.get("sort_order", "asc")
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"
    result = service.list(page=page, page_size=page_size, search=search, is_active=is_active, sort_by=sort_by, sort_order=sort_order)
    return service.success(data={"items": CurrencySummaryResponseSchema(many=True).dump(result.items), "pagination": {"page": result.page, "page_size": result.page_size, "total_records": result.total_records, "total_pages": result.total_pages}}, message="Currencies retrieved.")

@currency_bp.route("/lookup", methods=["GET"])
@permission_required("master.currency.read")
def lookup_currencies():
    service = CurrencyService()
    result = service.list(page=1, page_size=200, search=request.args.get("search"), is_active=True, sort_by="name", sort_order="asc")
    return service.success(data=CurrencyLookupResponseSchema(many=True).dump(result.items), message="Currencies lookup.")

@currency_bp.route("/<id>", methods=["GET"])
@permission_required("master.currency.read")
def get_currency(id):
    service = CurrencyService()
    try: entity = service.get(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    return service.success(data=CurrencyDetailResponseSchema().dump(entity), message="Currency retrieved.")

@currency_bp.route("/<id>", methods=["PUT"])
@permission_required("master.currency.update")
def update_currency(id):
    service = CurrencyService()
    try: data = UpdateCurrencyRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.update(id, data)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except (DomainException, BusinessException) as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(data=CurrencyDetailResponseSchema().dump(entity), message="Currency updated.")

@currency_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.currency.delete")
def delete_currency(id):
    service = CurrencyService()
    try: service.delete(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(message="Currency deactivated.")
