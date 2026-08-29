from flask import Blueprint, request
from marshmallow import ValidationError, Schema
import uuid as _uuid_mod
from typing import Any, Type

from app.core.extensions import db
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from app.modules.auth.permissions import permission_required

# Import all consolidated models
from .models import (
    PackageCategory,
    HotelCategory,
    MealPlan,
    VehicleType,
    ActivityType,
    Season,
    PaymentMethod,
    Currency,
    CancellationPolicy,
    TaxConfiguration,
)
from app.models import PaymentType, VendorType, OrganizationType

# Import all schemas
from .schemas import (
    BaseMasterRequestSchema,
    BaseMasterUpdateSchema,
    BaseMasterSummaryResponseSchema,
    BaseMasterDetailResponseSchema,
    BaseMasterLookupResponseSchema,
    CreateCurrencyRequestSchema,
    UpdateCurrencyRequestSchema,
    CurrencySummaryResponseSchema,
    CurrencyDetailResponseSchema,
    CurrencyLookupResponseSchema,
    CreateCancellationPolicyRequestSchema,
    UpdateCancellationPolicyRequestSchema,
    CancellationPolicySummaryResponseSchema,
    CancellationPolicyDetailResponseSchema,
    CancellationPolicyLookupResponseSchema,
    CreateTaxConfigurationRequestSchema,
    UpdateTaxConfigurationRequestSchema,
    TaxConfigurationSummaryResponseSchema,
    TaxConfigurationDetailResponseSchema,
    TaxConfigurationLookupResponseSchema,
)

catalog_bp = Blueprint("catalog", __name__, url_prefix="/api/v1/masters")


class CatalogService(BaseService):
    def __init__(self, model_class: Type[db.Model]):
        self.model_class = model_class

    def _parse_uuid(self, raw_id: str | _uuid_mod.UUID) -> _uuid_mod.UUID:
        if isinstance(raw_id, _uuid_mod.UUID):
            return raw_id
        try:
            return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError):
            raise NotFoundException(f"Resource not found.", code="ERR_NOT_FOUND")

    def create(self, data: dict) -> db.Model:
        # Pre-save validations / hooks
        code = data["code"].upper()
        existing = self.model_class.query.filter_by(code=code).first()
        if existing:
            raise BusinessException(
                f"Resource with code '{code}' already exists.",
                code="ERR_DUPLICATE_CODE",
            )

        # Custom rules: Currency single default
        if self.model_class == Currency and data.get("is_default"):
            db.session.query(Currency).filter(Currency.is_default == True).update({"is_default": False})

        from flask_jwt_extended import get_jwt_identity
        actor = get_jwt_identity()

        # Build entity
        fields = {
            "name": data["name"],
            "code": code,
            "description": data.get("description"),
            "display_order": data.get("display_order", 0),
            "is_active": data.get("is_active", True),
            "created_by": actor,
            "updated_by": actor,
        }

        # Inject special fields
        if self.model_class == Currency:
            fields["symbol"] = data["symbol"]
            fields["is_default"] = data.get("is_default", False)
        elif self.model_class == CancellationPolicy:
            fields["refund_percentage"] = data["refund_percentage"]
            fields["days_before_travel"] = data["days_before_travel"]
        elif self.model_class == TaxConfiguration:
            fields["tax_rate"] = data["tax_rate"]
            fields["tax_type"] = data["tax_type"]

        entity = self.model_class(**fields)
        db.session.add(entity)
        self.commit()
        return entity

    def update(self, entity_id: str, data: dict) -> db.Model:
        uid = self._parse_uuid(entity_id)
        entity = self.model_class.query.get(uid)
        if not entity:
            raise NotFoundException("Resource not found.", code="ERR_NOT_FOUND")

        self.check_optimistic_lock(entity.version, data.get("version"))

        # Duplicate code check
        if "code" in data:
            new_code = data["code"].upper()
            if new_code != entity.code:
                existing = self.model_class.query.filter(
                    self.model_class.code == new_code,
                    self.model_class.id != uid
                ).first()
                if existing:
                    raise BusinessException(
                        f"Resource with code '{new_code}' already exists.",
                        code="ERR_DUPLICATE_CODE",
                    )
                entity.code = new_code

        # Custom rules: Currency single default
        if self.model_class == Currency and data.get("is_default"):
            db.session.query(Currency).filter(Currency.is_default == True, Currency.id != uid).update({"is_default": False})

        # Apply basic fields
        for field in ("name", "description", "display_order", "is_active"):
            if field in data:
                setattr(entity, field, data[field])

        # Apply special fields
        if self.model_class == Currency:
            if "symbol" in data:
                entity.symbol = data["symbol"]
            if "is_default" in data:
                entity.is_default = data["is_default"]
        elif self.model_class == CancellationPolicy:
            if "refund_percentage" in data:
                entity.refund_percentage = data["refund_percentage"]
            if "days_before_travel" in data:
                entity.days_before_travel = data["days_before_travel"]
        elif self.model_class == TaxConfiguration:
            if "tax_rate" in data:
                entity.tax_rate = data["tax_rate"]
            if "tax_type" in data:
                entity.tax_type = data["tax_type"]

        from flask_jwt_extended import get_jwt_identity
        entity.version += 1
        entity.updated_by = get_jwt_identity()

        db.session.add(entity)
        self.commit()
        return entity

    def delete(self, entity_id: str) -> None:
        uid = self._parse_uuid(entity_id)
        entity = self.model_class.query.get(uid)
        if not entity:
            raise NotFoundException("Resource not found.", code="ERR_NOT_FOUND")

        from flask_jwt_extended import get_jwt_identity
        entity.is_active = False
        entity.version += 1
        entity.updated_by = get_jwt_identity()

        db.session.add(entity)
        self.commit()

    def get(self, entity_id: str) -> db.Model:
        uid = self._parse_uuid(entity_id)
        entity = self.model_class.query.get(uid)
        if not entity:
            raise NotFoundException("Resource not found.", code="ERR_NOT_FOUND")
        return entity

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        sort_by: str = "display_order",
        sort_order: str = "asc"
    ) -> Any:
        from app.common.filters import apply_filters
        from app.common.search import apply_search
        from app.common.sorting import apply_sort
        from app.common.pagination import apply_pagination, PaginationResult
        from sqlalchemy import select, func

        stmt = select(self.model_class)

        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        stmt = apply_filters(stmt, self.model_class, filters, ["is_active"])

        searchable = ["name", "code"]
        stmt = apply_search(stmt, self.model_class, search, searchable)

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.session.scalar(total_stmt)

        stmt = apply_sort(
            stmt,
            self.model_class,
            sort_by,
            sort_order,
            sortable_fields=["name", "code", "display_order", "created_at", "updated_at"],
            default_sort=[("display_order", "asc"), ("name", "asc")]
        )

        stmt = apply_pagination(stmt, page, page_size)
        items = list(db.session.scalars(stmt))

        return PaginationResult(
            items=items,
            page=page,
            page_size=page_size,
            total_records=total
        )


def _flatten_errors(messages: dict) -> list[dict]:
    errors = []
    for field, msgs in messages.items():
        for msg in (msgs if isinstance(msgs, list) else [msgs]):
            errors.append({"code": "ERR_VALIDATION", "field": field, "message": msg})
    return errors


def register_catalog_routes(
    url_slug: str,
    model_class: Type[db.Model],
    create_schema_cls: Type[Schema],
    update_schema_cls: Type[Schema],
    summary_schema_cls: Type[Schema],
    detail_schema_cls: Type[Schema],
    lookup_schema_cls: Type[Schema],
    perm_prefix: str
):
    service = CatalogService(model_class)

    @catalog_bp.route(f"/{url_slug}", methods=["POST"], endpoint=f"create_{url_slug}")
    @permission_required(f"master.{perm_prefix}.create")
    def create():
        try:
            data = create_schema_cls().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

        try:
            entity = service.create(data)
        except BusinessException as err:
            return service.error(err.message, code=err.code, status_code=409)

        resp, status = service.success(
            data=detail_schema_cls().dump(entity),
            message="Created successfully.",
            status_code=201,
        )
        resp.headers["Location"] = f"/api/v1/masters/{url_slug}/{entity.id}"
        return resp, status

    @catalog_bp.route(f"/{url_slug}", methods=["GET"], endpoint=f"list_{url_slug}")
    @permission_required(f"master.{perm_prefix}.read")
    def list_all():
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        search = request.args.get("search", None)
        sort_by = request.args.get("sort_by", "display_order")
        sort_order = request.args.get("sort_order", "asc")

        is_active_raw = request.args.get("is_active")
        is_active = None
        if is_active_raw is not None:
            is_active = is_active_raw.lower() == "true"

        result = service.list(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return service.success(
            data={
                "items": summary_schema_cls(many=True).dump(result.items),
                "pagination": {
                    "page": result.page,
                    "page_size": result.page_size,
                    "total_records": result.total_records,
                    "total_pages": result.total_pages,
                },
            },
            message="Retrieved successfully.",
        )

    @catalog_bp.route(f"/{url_slug}/lookup", methods=["GET"], endpoint=f"lookup_{url_slug}")
    @permission_required(f"master.{perm_prefix}.read")
    def lookup():
        search = request.args.get("search", None)
        result = service.list(
            page=1,
            page_size=500,
            search=search,
            is_active=True,
            sort_by="name",
            sort_order="asc",
        )
        return service.success(
            data=lookup_schema_cls(many=True).dump(result.items),
            message="Lookup retrieved successfully.",
        )

    @catalog_bp.route(f"/{url_slug}/<id>", methods=["GET"], endpoint=f"get_{url_slug}")
    @permission_required(f"master.{perm_prefix}.read")
    def get_by_id(id):
        try:
            entity = service.get(id)
        except NotFoundException as err:
            return service.error(err.message, code=err.code, status_code=404)
        return service.success(
            data=detail_schema_cls().dump(entity),
            message="Retrieved successfully.",
        )

    @catalog_bp.route(f"/{url_slug}/<id>", methods=["PUT"], endpoint=f"update_{url_slug}")
    @permission_required(f"master.{perm_prefix}.update")
    def update(id):
        try:
            data = update_schema_cls().load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)

        try:
            entity = service.update(id, data)
        except NotFoundException as err:
            return service.error(err.message, code=err.code, status_code=404)
        except DomainException as err:
            code = "ERR_OPTIMISTIC_LOCK" if err.code == "ERR_CONCURRENT_MODIFICATION" else err.code
            return service.error(err.message, code=code, status_code=409)
        except BusinessException as err:
            return service.error(err.message, code=err.code, status_code=409)

        return service.success(
            data=detail_schema_cls().dump(entity),
            message="Updated successfully.",
        )

    @catalog_bp.route(f"/{url_slug}/<id>", methods=["DELETE"], endpoint=f"delete_{url_slug}")
    @permission_required(f"master.{perm_prefix}.delete")
    def delete(id):
        try:
            service.delete(id)
        except NotFoundException as err:
            return service.error(err.message, code=err.code, status_code=404)
        except BusinessException as err:
            return service.error(err.message, code=err.code, status_code=409)

        return service.success(message="Deactivated successfully.")


# ─────────────────────────────────────────────────────────────────
# Register Catalog Configurations dynamically
# ─────────────────────────────────────────────────────────────────

CONFIGS = [
    ("package-categories", PackageCategory, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "package_category"),
    ("hotel-categories", HotelCategory, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "hotel_category"),
    ("meal-plans", MealPlan, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "meal_plan"),
    ("vehicle-types", VehicleType, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "vehicle_type"),
    ("activity-types", ActivityType, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "activity_type"),
    ("seasons", Season, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "season"),
    ("payment-methods", PaymentMethod, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "payment_method"),
    ("payment-types", PaymentType, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "payment_type"),
    ("vendor-types", VendorType, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "vendor_type"),
    ("organization-types", OrganizationType, BaseMasterRequestSchema, BaseMasterUpdateSchema, BaseMasterSummaryResponseSchema, BaseMasterDetailResponseSchema, BaseMasterLookupResponseSchema, "organization_type"),
    ("currencies", Currency, CreateCurrencyRequestSchema, UpdateCurrencyRequestSchema, CurrencySummaryResponseSchema, CurrencyDetailResponseSchema, CurrencyLookupResponseSchema, "currency"),
    ("cancellation-policies", CancellationPolicy, CreateCancellationPolicyRequestSchema, UpdateCancellationPolicyRequestSchema, CancellationPolicySummaryResponseSchema, CancellationPolicyDetailResponseSchema, CancellationPolicyLookupResponseSchema, "cancellation_policy"),
    ("tax-configurations", TaxConfiguration, CreateTaxConfigurationRequestSchema, UpdateTaxConfigurationRequestSchema, TaxConfigurationSummaryResponseSchema, TaxConfigurationDetailResponseSchema, TaxConfigurationLookupResponseSchema, "tax_configuration"),
]

for cfg in CONFIGS:
    register_catalog_routes(*cfg)
