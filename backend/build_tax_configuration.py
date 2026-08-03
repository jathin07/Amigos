import os

BASE_DIR = r"C:\Users\jathi\workspace\amigos\backend"

def write_f(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# =====================================================================
# TAX CONFIGURATION (Complex)
# =====================================================================

write_f("app/modules/master/tax_configuration/__init__.py", """from flask import Blueprint\n\ntax_configuration_bp = Blueprint("tax_configuration", __name__, url_prefix="/api/v1/masters/tax-configurations")\n\nfrom . import routes\n""")

write_f("app/modules/master/tax_configuration/models.py", """
from app.core.extensions import db
from app.core.base_model import BaseModel

class TaxConfiguration(db.Model, BaseModel):
    __tablename__ = "tax_configurations"
    code          = db.Column(db.String(20),  nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    tax_rate      = db.Column(db.Numeric(5, 2), nullable=False)
    tax_type      = db.Column(db.String(20), nullable=False)
    is_inclusive  = db.Column(db.Boolean, default=False, nullable=False)
    is_default    = db.Column(db.Boolean, default=False, nullable=False, index=True)
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_tax_configurations_code"),
        db.Index("ix_tax_configurations_code", "code"),
    )
""")

write_f("app/modules/master/tax_configuration/repository.py", """
import uuid
from sqlalchemy import select
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import TaxConfiguration

class TaxConfigurationRepository(SQLAlchemyBaseRepository[TaxConfiguration]):
    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active"]

    def __init__(self):
        super().__init__(TaxConfiguration)

    def find_by_code(self, code: str) -> TaxConfiguration | None:
        return self.model_class.query.filter_by(code=code.strip().upper()).first()

    def find_by_code_excluding(self, code: str, exclude_id: uuid.UUID) -> TaxConfiguration | None:
        stmt = select(self.model_class).where(
            self.model_class.code == code.strip().upper(),
            self.model_class.id != exclude_id,
        )
        return db.session.scalars(stmt).first()

    def get(self, entity_id: uuid.UUID):
        return super().get(entity_id)
        
    def get_defaults_by_type(self, tax_type: str):
        return self.model_class.query.filter_by(tax_type=tax_type, is_default=True).all()
""")

write_f("app/modules/master/tax_configuration/schemas.py", """
import re
from marshmallow import Schema, fields, validate, validates, ValidationError

class CreateTaxConfigurationRequestSchema(Schema):
    name          = fields.String(required=True, validate=validate.Length(min=1, max=100))
    code          = fields.String(required=True, validate=validate.Length(min=1, max=20))
    description   = fields.String(load_default=None, validate=validate.Length(max=2000))
    display_order = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active     = fields.Boolean(load_default=True)
    tax_rate      = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0, max=100))
    tax_type      = fields.String(required=True, validate=validate.OneOf(["GST", "VAT", "SERVICE_TAX", "CESS"]))
    is_inclusive  = fields.Boolean(load_default=False)
    is_default    = fields.Boolean(load_default=False)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class UpdateTaxConfigurationRequestSchema(Schema):
    name          = fields.String(validate=validate.Length(min=1, max=100))
    code          = fields.String(validate=validate.Length(min=1, max=20))
    description   = fields.String(allow_none=True, validate=validate.Length(max=2000))
    display_order = fields.Integer(validate=validate.Range(min=0))
    is_active     = fields.Boolean()
    tax_rate      = fields.Decimal(as_string=False, validate=validate.Range(min=0, max=100))
    tax_type      = fields.String(validate=validate.OneOf(["GST", "VAT", "SERVICE_TAX", "CESS"]))
    is_inclusive  = fields.Boolean()
    is_default    = fields.Boolean()
    version       = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class TaxConfigurationLookupResponseSchema(Schema):
    id   = fields.UUID()
    name = fields.String()
    code = fields.String()

class TaxConfigurationSummaryResponseSchema(Schema):
    id            = fields.UUID()
    name          = fields.String()
    code          = fields.String()
    is_active     = fields.Boolean()
    display_order = fields.Integer()
    tax_rate      = fields.Decimal(as_string=True)
    tax_type      = fields.String()

class TaxConfigurationDetailResponseSchema(TaxConfigurationSummaryResponseSchema):
    description   = fields.String()
    is_inclusive  = fields.Boolean()
    is_default    = fields.Boolean()
    version       = fields.Integer()
    audit_info    = fields.Method("get_audit_info")
    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
""")

write_f("app/modules/master/tax_configuration/service.py", """
import uuid as _uuid_mod
from typing import Any
from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException
from .repository import TaxConfigurationRepository
from .models import TaxConfiguration

class TaxConfigurationService(BaseService):
    def __init__(self):
        self.repository = TaxConfigurationRepository()

    def _parse_uuid(self, raw_id):
        if isinstance(raw_id, _uuid_mod.UUID): return raw_id
        try: return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError): raise NotFoundException("Tax configuration not found.", code="ERR_NOT_FOUND")

    def _handle_is_default(self, tax_type: str, entity_id: str | None = None):
        defaults = self.repository.get_defaults_by_type(tax_type)
        for d in defaults:
            if entity_id is None or str(d.id) != entity_id:
                d.is_default = False
                self.repository.add(d)

    def create(self, data: dict) -> TaxConfiguration:
        code = data["code"].upper()
        if self.repository.find_by_code(code):
            raise BusinessException(f"Code '{code}' already exists.", code="ERR_DUPLICATE_CODE")
            
        entity = TaxConfiguration(
            code=code, name=data["name"], description=data.get("description"),
            display_order=data.get("display_order", 0), is_active=data.get("is_active", True),
            tax_rate=data["tax_rate"], tax_type=data["tax_type"],
            is_inclusive=data.get("is_inclusive", False), is_default=data.get("is_default", False),
            created_by=get_jwt_identity(), updated_by=get_jwt_identity(),
        )
        self.repository.add(entity)
        if entity.is_default:
            self.commit()
            self._handle_is_default(entity.tax_type, str(entity.id))
            
        self.commit()
        return entity

    def update(self, entity_id: str, data: dict) -> TaxConfiguration:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Tax configuration not found.", code="ERR_NOT_FOUND")
        self.check_optimistic_lock(entity.version, data.get("version"))
        
        if "code" in data:
            new_code = data["code"].upper()
            if new_code != entity.code and self.repository.find_by_code_excluding(new_code, uid):
                raise BusinessException(f"Code '{new_code}' already exists.", code="ERR_DUPLICATE_CODE")
            entity.code = new_code
            
        for field in ("name", "description", "display_order", "is_active", "tax_rate", "tax_type", "is_inclusive", "is_default"):
            if field in data: setattr(entity, field, data[field])
            
        entity.version += 1
        entity.updated_by = get_jwt_identity()
        self.repository.add(entity)
        
        if data.get("is_default") is True or (data.get("tax_type") and entity.is_default):
            self._handle_is_default(entity.tax_type, str(entity.id))
            
        self.commit()
        return entity

    def delete(self, entity_id: str) -> None:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Tax configuration not found.", code="ERR_NOT_FOUND")
        entity.is_active = False
        entity.version += 1
        entity.updated_by = get_jwt_identity()
        self.repository.add(entity)
        self.commit()

    def get(self, entity_id: str) -> TaxConfiguration:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Tax configuration not found.", code="ERR_NOT_FOUND")
        return entity

    def list(self, page=1, page_size=20, search=None, is_active=None, sort_by="display_order", sort_order="asc") -> Any:
        filters = {}
        if is_active is not None: filters["is_active"] = is_active
        return self.repository.paginate(page=page, page_size=page_size, search_query=search, sort_by=sort_by, sort_order=sort_order, **filters)
""")

write_f("app/modules/master/tax_configuration/routes.py", """
from flask import Blueprint, request
from marshmallow import ValidationError
from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (CreateTaxConfigurationRequestSchema, UpdateTaxConfigurationRequestSchema,
    TaxConfigurationSummaryResponseSchema, TaxConfigurationDetailResponseSchema, TaxConfigurationLookupResponseSchema)
from .service import TaxConfigurationService
from . import tax_configuration_bp

def _flatten_errors(messages):
    return [{"code": "ERR_VALIDATION", "field": f, "message": m}
            for f, msgs in messages.items() for m in (msgs if isinstance(msgs, list) else [msgs])]

@tax_configuration_bp.route("", methods=["POST"])
@permission_required("master.tax_configuration.create")
def create_tax_configuration():
    service = TaxConfigurationService()
    try: data = CreateTaxConfigurationRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.create(data)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    resp, status = service.success(data=TaxConfigurationDetailResponseSchema().dump(entity), message="Tax configuration created.", status_code=201)
    resp.headers["Location"] = f"/api/v1/masters/tax-configurations/{entity.id}"
    return resp, status

@tax_configuration_bp.route("", methods=["GET"])
@permission_required("master.tax_configuration.read")
def list_tax_configurations():
    service = TaxConfigurationService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "display_order")
    sort_order = request.args.get("sort_order", "asc")
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"
    result = service.list(page=page, page_size=page_size, search=search, is_active=is_active, sort_by=sort_by, sort_order=sort_order)
    return service.success(data={"items": TaxConfigurationSummaryResponseSchema(many=True).dump(result.items), "pagination": {"page": result.page, "page_size": result.page_size, "total_records": result.total_records, "total_pages": result.total_pages}}, message="Tax configurations retrieved.")

@tax_configuration_bp.route("/lookup", methods=["GET"])
@permission_required("master.tax_configuration.read")
def lookup_tax_configurations():
    service = TaxConfigurationService()
    result = service.list(page=1, page_size=200, search=request.args.get("search"), is_active=True, sort_by="name", sort_order="asc")
    return service.success(data=TaxConfigurationLookupResponseSchema(many=True).dump(result.items), message="Tax configurations lookup.")

@tax_configuration_bp.route("/<id>", methods=["GET"])
@permission_required("master.tax_configuration.read")
def get_tax_configuration(id):
    service = TaxConfigurationService()
    try: entity = service.get(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    return service.success(data=TaxConfigurationDetailResponseSchema().dump(entity), message="Tax configuration retrieved.")

@tax_configuration_bp.route("/<id>", methods=["PUT"])
@permission_required("master.tax_configuration.update")
def update_tax_configuration(id):
    service = TaxConfigurationService()
    try: data = UpdateTaxConfigurationRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.update(id, data)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except (DomainException, BusinessException) as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(data=TaxConfigurationDetailResponseSchema().dump(entity), message="Tax configuration updated.")

@tax_configuration_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.tax_configuration.delete")
def delete_tax_configuration(id):
    service = TaxConfigurationService()
    try: service.delete(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(message="Tax configuration deactivated.")
""")

write_f("tests/modules/master/tax_configuration/__init__.py", "")

write_f("tests/modules/master/tax_configuration/test_tax_configuration.py", """
import pytest, uuid
from flask_jwt_extended import create_access_token
from app.core.startup import create_app
from app.core.extensions import db, bcrypt
from app.models import UserAccount, TeamMember, Role

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app): return app.test_client()

@pytest.fixture
def auth_token(app):
    with app.app_context():
        role = Role(name="Admin", code="ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()
        tm = TeamMember(first_name="Test", display_name="Test User", official_email="test@test.com",
            phone="9999999010", employee_code="TEST-TC01", role=role, is_active=True)
        db.session.add(tm)
        db.session.flush()
        user = UserAccount(team_member_id=tm.id, username="test@test.com",
            password_hash=bcrypt.generate_password_hash("pass").decode(), is_active=True)
        db.session.add(user)
        db.session.commit()
        return create_access_token(identity=str(user.id), additional_claims={"permissions": [
            "master.tax_configuration.read", "master.tax_configuration.create",
            "master.tax_configuration.update", "master.tax_configuration.delete"]})

@pytest.fixture
def no_perm_token(app):
    with app.app_context():
        return create_access_token(identity=str(uuid.uuid4()), additional_claims={"permissions": []})

def auth_headers(token): return {"Authorization": f"Bearer {token}"}

def test_create_tax_configuration_success(client, auth_token):
    res = client.post("/api/v1/masters/tax-configurations", json={"name": "GST 5%", "code": "GST_5", "tax_rate": 5, "tax_type": "GST"}, headers=auth_headers(auth_token))
    assert res.status_code == 201
    assert res.json["data"]["code"] == "GST_5"

def test_create_tax_configuration_duplicate_code(client, auth_token):
    client.post("/api/v1/masters/tax-configurations", json={"name": "GST 5%", "code": "GST_5", "tax_rate": 5, "tax_type": "GST"}, headers=auth_headers(auth_token))
    res = client.post("/api/v1/masters/tax-configurations", json={"name": "GST 5% 2", "code": "GST_5", "tax_rate": 5, "tax_type": "GST"}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_DUPLICATE_CODE"

def test_create_invalid_tax_rate(client, auth_token):
    res = client.post("/api/v1/masters/tax-configurations", json={"name": "GST", "code": "GST", "tax_rate": 150, "tax_type": "GST"}, headers=auth_headers(auth_token))
    assert res.status_code == 400
    assert res.json["code"] == "ERR_VALIDATION"
    assert any(e["field"] == "tax_rate" for e in res.json["errors"])

def test_get_tax_configuration_by_id(client, auth_token):
    create_res = client.post("/api/v1/masters/tax-configurations", json={"name": "GST 5%", "code": "GST_5", "tax_rate": 5, "tax_type": "GST"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.get(f"/api/v1/masters/tax-configurations/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["id"] == s_id

def test_get_tax_configuration_not_found(client, auth_token):
    res = client.get(f"/api/v1/masters/tax-configurations/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_get_tax_configuration_invalid_uuid(client, auth_token):
    res = client.get("/api/v1/masters/tax-configurations/invalid-id", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_list_tax_configurations_pagination(client, auth_token):
    for i in range(5):
        client.post("/api/v1/masters/tax-configurations", json={"name": f"T{i}", "code": f"T{i}", "tax_rate": 5, "tax_type": "GST"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/tax-configurations?page=1&page_size=2", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 2
    assert res.json["data"]["pagination"]["total_records"] >= 5

def test_list_tax_configurations_search(client, auth_token):
    client.post("/api/v1/masters/tax-configurations", json={"name": "VAT", "code": "VAT", "tax_rate": 5, "tax_type": "VAT"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/tax-configurations?search=VAT", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 1

def test_list_tax_configurations_filter_is_active(client, auth_token):
    client.post("/api/v1/masters/tax-configurations", json={"name": "VAT", "code": "VAT", "tax_rate": 5, "tax_type": "VAT", "is_active": False}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/tax-configurations?is_active=false", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) >= 1

def test_list_tax_configurations_sort(client, auth_token):
    client.post("/api/v1/masters/tax-configurations", json={"name": "A", "code": "A", "tax_rate": 5, "tax_type": "GST", "display_order": 2}, headers=auth_headers(auth_token))
    client.post("/api/v1/masters/tax-configurations", json={"name": "B", "code": "B", "tax_rate": 5, "tax_type": "GST", "display_order": 1}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/tax-configurations?sort_by=display_order&sort_order=asc", headers=auth_headers(auth_token))
    items = res.json["data"]["items"]
    assert items[0]["display_order"] <= items[1]["display_order"]

def test_list_tax_configurations_empty(client, auth_token):
    res = client.get("/api/v1/masters/tax-configurations?search=NONEXISTENT", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 0

def test_update_tax_configuration_success(client, auth_token):
    create_res = client.post("/api/v1/masters/tax-configurations", json={"name": "VAT", "code": "VAT", "tax_rate": 5, "tax_type": "VAT"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/tax-configurations/{s_id}", json={"name": "VAT Updated", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["name"] == "VAT Updated"
    assert res.json["data"]["version"] == 2

def test_update_tax_configuration_version_conflict(client, auth_token):
    create_res = client.post("/api/v1/masters/tax-configurations", json={"name": "VAT", "code": "VAT", "tax_rate": 5, "tax_type": "VAT"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/tax-configurations/{s_id}", json={"name": "VAT Updated", "version": 999}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_OPTIMISTIC_LOCK"

def test_update_tax_configuration_not_found(client, auth_token):
    res = client.put(f"/api/v1/masters/tax-configurations/{uuid.uuid4()}", json={"name": "X", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_delete_tax_configuration_soft(client, auth_token):
    create_res = client.post("/api/v1/masters/tax-configurations", json={"name": "VAT", "code": "VAT", "tax_rate": 5, "tax_type": "VAT"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.delete(f"/api/v1/masters/tax-configurations/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    get_res = client.get(f"/api/v1/masters/tax-configurations/{s_id}", headers=auth_headers(auth_token))
    assert get_res.json["data"]["is_active"] is False

def test_delete_tax_configuration_not_found(client, auth_token):
    res = client.delete(f"/api/v1/masters/tax-configurations/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_lookup_tax_configurations(client, auth_token):
    client.post("/api/v1/masters/tax-configurations", json={"name": "VAT", "code": "VAT", "tax_rate": 5, "tax_type": "VAT"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/tax-configurations/lookup", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]) >= 1

def test_unauthorized(client):
    res = client.get("/api/v1/masters/tax-configurations")
    assert res.status_code == 401

def test_forbidden(client, no_perm_token):
    res = client.get("/api/v1/masters/tax-configurations", headers=auth_headers(no_perm_token))
    assert res.status_code == 403
""")

write_f("seeds/014_tax_configurations.py", """
from app.core.extensions import db
from app.modules.master.tax_configuration.models import TaxConfiguration
import uuid

def seed():
    data = [
        {'name':'GST 5%','code':'GST_5','tax_rate':5.00,'tax_type':'GST','is_inclusive':False},
        {'name':'GST 12%','code':'GST_12','tax_rate':12.00,'tax_type':'GST','is_inclusive':False},
        {'name':'GST 18%','code':'GST_18','tax_rate':18.00,'tax_type':'GST','is_inclusive':False,'is_default':True},
        {'name':'GST 28%','code':'GST_28','tax_rate':28.00,'tax_type':'GST'},
        {'name':'VAT 5%','code':'VAT_5','tax_rate':5.00,'tax_type':'VAT'},
        {'name':'Service Tax 15%','code':'SVC_TAX','tax_rate':15.00,'tax_type':'SERVICE_TAX'}
    ]
    for item in data:
        if not TaxConfiguration.query.filter_by(code=item['code']).first():
            entity = TaxConfiguration(
                id=uuid.uuid4(),
                **item,
                is_active=True,
                created_by=None,
                updated_by=None
            )
            db.session.add(entity)
    db.session.commit()
    print("Tax Configurations seeded.")
""")
