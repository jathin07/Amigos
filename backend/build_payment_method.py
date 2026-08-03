import os

BASE_DIR = r"C:\Users\jathi\workspace\amigos\backend"

def write_f(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# =====================================================================
# PAYMENT METHOD (Standard)
# =====================================================================

write_f("app/modules/master/payment_method/__init__.py", """from flask import Blueprint\n\npayment_method_bp = Blueprint("payment_method", __name__, url_prefix="/api/v1/masters/payment-methods")\n\nfrom . import routes\n""")

write_f("app/modules/master/payment_method/models.py", """
from app.core.extensions import db
from app.core.base_model import BaseModel

class PaymentMethod(db.Model, BaseModel):
    __tablename__ = "payment_methods"
    code          = db.Column(db.String(20),  nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_payment_methods_code"),
        db.Index("ix_payment_methods_code", "code"),
    )
""")

write_f("app/modules/master/payment_method/repository.py", """
import uuid
from sqlalchemy import select
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import PaymentMethod

class PaymentMethodRepository(SQLAlchemyBaseRepository[PaymentMethod]):
    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active"]

    def __init__(self):
        super().__init__(PaymentMethod)

    def find_by_code(self, code: str) -> PaymentMethod | None:
        return self.model_class.query.filter_by(code=code.strip().upper()).first()

    def find_by_code_excluding(self, code: str, exclude_id: uuid.UUID) -> PaymentMethod | None:
        stmt = select(self.model_class).where(
            self.model_class.code == code.strip().upper(),
            self.model_class.id != exclude_id,
        )
        return db.session.scalars(stmt).first()

    def get(self, entity_id: uuid.UUID):
        return super().get(entity_id)
""")

write_f("app/modules/master/payment_method/schemas.py", """
import re
from marshmallow import Schema, fields, validate, validates, ValidationError

class CreatePaymentMethodRequestSchema(Schema):
    name          = fields.String(required=True, validate=validate.Length(min=1, max=100))
    code          = fields.String(required=True, validate=validate.Length(min=1, max=20))
    description   = fields.String(load_default=None, validate=validate.Length(max=2000))
    display_order = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active     = fields.Boolean(load_default=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class UpdatePaymentMethodRequestSchema(Schema):
    name          = fields.String(validate=validate.Length(min=1, max=100))
    code          = fields.String(validate=validate.Length(min=1, max=20))
    description   = fields.String(allow_none=True, validate=validate.Length(max=2000))
    display_order = fields.Integer(validate=validate.Range(min=0))
    is_active     = fields.Boolean()
    version       = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class PaymentMethodLookupResponseSchema(Schema):
    id   = fields.UUID()
    name = fields.String()
    code = fields.String()

class PaymentMethodSummaryResponseSchema(Schema):
    id            = fields.UUID()
    name          = fields.String()
    code          = fields.String()
    is_active     = fields.Boolean()
    display_order = fields.Integer()

class PaymentMethodDetailResponseSchema(PaymentMethodSummaryResponseSchema):
    description = fields.String()
    version     = fields.Integer()
    audit_info  = fields.Method("get_audit_info")
    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
""")

write_f("app/modules/master/payment_method/service.py", """
import uuid as _uuid_mod
from typing import Any
from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException
from .repository import PaymentMethodRepository
from .models import PaymentMethod

class PaymentMethodService(BaseService):
    def __init__(self):
        self.repository = PaymentMethodRepository()

    def _parse_uuid(self, raw_id):
        if isinstance(raw_id, _uuid_mod.UUID): return raw_id
        try: return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError): raise NotFoundException("PaymentMethod not found.", code="ERR_NOT_FOUND")

    def create(self, data: dict) -> PaymentMethod:
        code = data["code"].upper()
        if self.repository.find_by_code(code):
            raise BusinessException(f"Code '{code}' already exists.", code="ERR_DUPLICATE_CODE")
        entity = PaymentMethod(
            code=code, name=data["name"], description=data.get("description"),
            display_order=data.get("display_order", 0), is_active=data.get("is_active", True),
            created_by=get_jwt_identity(), updated_by=get_jwt_identity(),
        )
        self.repository.add(entity)
        self.commit()
        return entity

    def update(self, entity_id: str, data: dict) -> PaymentMethod:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("PaymentMethod not found.", code="ERR_NOT_FOUND")
        self.check_optimistic_lock(entity.version, data.get("version"))
        
        if "code" in data:
            new_code = data["code"].upper()
            if new_code != entity.code and self.repository.find_by_code_excluding(new_code, uid):
                raise BusinessException(f"Code '{new_code}' already exists.", code="ERR_DUPLICATE_CODE")
            entity.code = new_code
        for field in ("name", "description", "display_order", "is_active"):
            if field in data: setattr(entity, field, data[field])
            
        entity.version += 1
        entity.updated_by = get_jwt_identity()
        self.repository.add(entity)
        self.commit()
        return entity

    def delete(self, entity_id: str) -> None:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("PaymentMethod not found.", code="ERR_NOT_FOUND")
        entity.is_active = False
        entity.version += 1
        entity.updated_by = get_jwt_identity()
        self.repository.add(entity)
        self.commit()

    def get(self, entity_id: str) -> PaymentMethod:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("PaymentMethod not found.", code="ERR_NOT_FOUND")
        return entity

    def list(self, page=1, page_size=20, search=None, is_active=None, sort_by="display_order", sort_order="asc") -> Any:
        filters = {}
        if is_active is not None: filters["is_active"] = is_active
        return self.repository.paginate(page=page, page_size=page_size, search_query=search, sort_by=sort_by, sort_order=sort_order, **filters)
""")

write_f("app/modules/master/payment_method/routes.py", """
from flask import Blueprint, request
from marshmallow import ValidationError
from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (CreatePaymentMethodRequestSchema, UpdatePaymentMethodRequestSchema,
    PaymentMethodSummaryResponseSchema, PaymentMethodDetailResponseSchema, PaymentMethodLookupResponseSchema)
from .service import PaymentMethodService
from . import payment_method_bp

def _flatten_errors(messages):
    return [{"code": "ERR_VALIDATION", "field": f, "message": m}
            for f, msgs in messages.items() for m in (msgs if isinstance(msgs, list) else [msgs])]

@payment_method_bp.route("", methods=["POST"])
@permission_required("master.payment_method.create")
def create_payment_method():
    service = PaymentMethodService()
    try: data = CreatePaymentMethodRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.create(data)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    resp, status = service.success(data=PaymentMethodDetailResponseSchema().dump(entity), message="Payment method created.", status_code=201)
    resp.headers["Location"] = f"/api/v1/masters/payment-methods/{entity.id}"
    return resp, status

@payment_method_bp.route("", methods=["GET"])
@permission_required("master.payment_method.read")
def list_payment_methods():
    service = PaymentMethodService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "display_order")
    sort_order = request.args.get("sort_order", "asc")
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"
    result = service.list(page=page, page_size=page_size, search=search, is_active=is_active, sort_by=sort_by, sort_order=sort_order)
    return service.success(data={"items": PaymentMethodSummaryResponseSchema(many=True).dump(result.items), "pagination": {"page": result.page, "page_size": result.page_size, "total_records": result.total_records, "total_pages": result.total_pages}}, message="Payment methods retrieved.")

@payment_method_bp.route("/lookup", methods=["GET"])
@permission_required("master.payment_method.read")
def lookup_payment_methods():
    service = PaymentMethodService()
    result = service.list(page=1, page_size=200, search=request.args.get("search"), is_active=True, sort_by="name", sort_order="asc")
    return service.success(data=PaymentMethodLookupResponseSchema(many=True).dump(result.items), message="Payment methods lookup.")

@payment_method_bp.route("/<id>", methods=["GET"])
@permission_required("master.payment_method.read")
def get_payment_method(id):
    service = PaymentMethodService()
    try: entity = service.get(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    return service.success(data=PaymentMethodDetailResponseSchema().dump(entity), message="Payment method retrieved.")

@payment_method_bp.route("/<id>", methods=["PUT"])
@permission_required("master.payment_method.update")
def update_payment_method(id):
    service = PaymentMethodService()
    try: data = UpdatePaymentMethodRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.update(id, data)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except (DomainException, BusinessException) as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(data=PaymentMethodDetailResponseSchema().dump(entity), message="Payment method updated.")

@payment_method_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.payment_method.delete")
def delete_payment_method(id):
    service = PaymentMethodService()
    try: service.delete(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(message="Payment method deactivated.")
""")

write_f("tests/modules/master/payment_method/__init__.py", "")

write_f("tests/modules/master/payment_method/test_payment_method.py", """
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
            phone="9999999007", employee_code="TEST-PM01", role=role, is_active=True)
        db.session.add(tm)
        db.session.flush()
        user = UserAccount(team_member_id=tm.id, username="test@test.com",
            password_hash=bcrypt.generate_password_hash("pass").decode(), is_active=True)
        db.session.add(user)
        db.session.commit()
        return create_access_token(identity=str(user.id), additional_claims={"permissions": [
            "master.payment_method.read", "master.payment_method.create",
            "master.payment_method.update", "master.payment_method.delete"]})

@pytest.fixture
def no_perm_token(app):
    with app.app_context():
        return create_access_token(identity=str(uuid.uuid4()), additional_claims={"permissions": []})

def auth_headers(token): return {"Authorization": f"Bearer {token}"}

def test_create_payment_method_success(client, auth_token):
    res = client.post("/api/v1/masters/payment-methods", json={"name": "TestPM", "code": "TESTPM"}, headers=auth_headers(auth_token))
    assert res.status_code == 201
    assert res.json["data"]["code"] == "TESTPM"

def test_create_payment_method_duplicate_code(client, auth_token):
    client.post("/api/v1/masters/payment-methods", json={"name": "TestPM", "code": "TESTPM"}, headers=auth_headers(auth_token))
    res = client.post("/api/v1/masters/payment-methods", json={"name": "TestPM 2", "code": "TESTPM"}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_DUPLICATE_CODE"

def test_create_payment_method_validation_error(client, auth_token):
    res = client.post("/api/v1/masters/payment-methods", json={"name": ""}, headers=auth_headers(auth_token))
    assert res.status_code == 400
    assert res.json["code"] == "ERR_VALIDATION"

def test_get_payment_method_by_id(client, auth_token):
    create_res = client.post("/api/v1/masters/payment-methods", json={"name": "TestPM", "code": "TESTPM"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.get(f"/api/v1/masters/payment-methods/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["id"] == s_id

def test_get_payment_method_not_found(client, auth_token):
    res = client.get(f"/api/v1/masters/payment-methods/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_get_payment_method_invalid_uuid(client, auth_token):
    res = client.get("/api/v1/masters/payment-methods/invalid-id", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_list_payment_methods_pagination(client, auth_token):
    for i in range(5):
        client.post("/api/v1/masters/payment-methods", json={"name": f"P{i}", "code": f"P{i}"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/payment-methods?page=1&page_size=2", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 2
    assert res.json["data"]["pagination"]["total_records"] >= 5

def test_list_payment_methods_search(client, auth_token):
    client.post("/api/v1/masters/payment-methods", json={"name": "Wallet", "code": "WALLET"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/payment-methods?search=WALLET", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 1

def test_list_payment_methods_filter_is_active(client, auth_token):
    client.post("/api/v1/masters/payment-methods", json={"name": "Wallet", "code": "WALLET", "is_active": False}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/payment-methods?is_active=false", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) >= 1

def test_list_payment_methods_sort(client, auth_token):
    client.post("/api/v1/masters/payment-methods", json={"name": "A", "code": "A", "display_order": 2}, headers=auth_headers(auth_token))
    client.post("/api/v1/masters/payment-methods", json={"name": "B", "code": "B", "display_order": 1}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/payment-methods?sort_by=display_order&sort_order=asc", headers=auth_headers(auth_token))
    items = res.json["data"]["items"]
    assert items[0]["display_order"] <= items[1]["display_order"]

def test_list_payment_methods_empty(client, auth_token):
    res = client.get("/api/v1/masters/payment-methods?search=NONEXISTENT", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 0

def test_update_payment_method_success(client, auth_token):
    create_res = client.post("/api/v1/masters/payment-methods", json={"name": "Wallet", "code": "WALLET"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/payment-methods/{s_id}", json={"name": "Wallet Updated", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["name"] == "Wallet Updated"
    assert res.json["data"]["version"] == 2

def test_update_payment_method_version_conflict(client, auth_token):
    create_res = client.post("/api/v1/masters/payment-methods", json={"name": "Wallet", "code": "WALLET"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/payment-methods/{s_id}", json={"name": "Wallet Updated", "version": 999}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_OPTIMISTIC_LOCK"

def test_update_payment_method_not_found(client, auth_token):
    res = client.put(f"/api/v1/masters/payment-methods/{uuid.uuid4()}", json={"name": "X", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_delete_payment_method_soft(client, auth_token):
    create_res = client.post("/api/v1/masters/payment-methods", json={"name": "Wallet", "code": "WALLET"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.delete(f"/api/v1/masters/payment-methods/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    get_res = client.get(f"/api/v1/masters/payment-methods/{s_id}", headers=auth_headers(auth_token))
    assert get_res.json["data"]["is_active"] is False

def test_delete_payment_method_not_found(client, auth_token):
    res = client.delete(f"/api/v1/masters/payment-methods/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_lookup_payment_methods(client, auth_token):
    client.post("/api/v1/masters/payment-methods", json={"name": "Wallet", "code": "WALLET"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/payment-methods/lookup", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]) >= 1

def test_unauthorized(client):
    res = client.get("/api/v1/masters/payment-methods")
    assert res.status_code == 401

def test_forbidden(client, no_perm_token):
    res = client.get("/api/v1/masters/payment-methods", headers=auth_headers(no_perm_token))
    assert res.status_code == 403
""")

write_f("seeds/011_payment_methods.py", """
from app.core.extensions import db
from app.modules.master.payment_method.models import PaymentMethod
import uuid

def seed():
    data = [
        {'name':'Cash','code':'CASH','display_order':1},
        {'name':'UPI','code':'UPI','display_order':2},
        {'name':'Credit Card','code':'CREDIT_CARD','display_order':3},
        {'name':'Debit Card','code':'DEBIT_CARD','display_order':4},
        {'name':'Bank Transfer','code':'BANK_TRANSFER','display_order':5},
        {'name':'Cheque','code':'CHEQUE','display_order':6},
        {'name':'Wallet','code':'WALLET','display_order':7}
    ]
    for item in data:
        if not PaymentMethod.query.filter_by(code=item['code']).first():
            entity = PaymentMethod(
                id=uuid.uuid4(),
                **item,
                is_active=True,
                created_by=None,
                updated_by=None
            )
            db.session.add(entity)
    db.session.commit()
    print("Payment Methods seeded.")
""")
