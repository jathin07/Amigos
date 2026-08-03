import os

BASE_DIR = r"C:\Users\jathi\workspace\amigos\backend"

def write_f(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

# =====================================================================
# CANCELLATION POLICY (Complex)
# =====================================================================

write_f("app/modules/master/cancellation_policy/__init__.py", """from flask import Blueprint\n\ncancellation_policy_bp = Blueprint("cancellation_policy", __name__, url_prefix="/api/v1/masters/cancellation-policies")\n\nfrom . import routes\n""")

write_f("app/modules/master/cancellation_policy/models.py", """
from app.core.extensions import db
from app.core.base_model import BaseModel

class CancellationPolicy(db.Model, BaseModel):
    __tablename__ = "cancellation_policies"
    code               = db.Column(db.String(20),  nullable=False)
    name               = db.Column(db.String(100), nullable=False)
    description        = db.Column(db.Text, nullable=True)
    display_order      = db.Column(db.Integer, default=0, nullable=False)
    refund_percentage  = db.Column(db.Numeric(5, 2), nullable=False)
    days_before_travel = db.Column(db.Integer, nullable=False)
    policy_type        = db.Column(db.String(20), nullable=False, default='PERCENTAGE')
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_cancellation_policies_code"),
        db.Index("ix_cancellation_policies_code", "code"),
    )
""")

write_f("app/modules/master/cancellation_policy/repository.py", """
import uuid
from sqlalchemy import select
from app.core.extensions import db
from app.infrastructure.persistence.base_repository import SQLAlchemyBaseRepository
from .models import CancellationPolicy

class CancellationPolicyRepository(SQLAlchemyBaseRepository[CancellationPolicy]):
    searchable_fields = ["name", "code"]
    filterable_fields = ["is_active"]

    def __init__(self):
        super().__init__(CancellationPolicy)

    def find_by_code(self, code: str) -> CancellationPolicy | None:
        return self.model_class.query.filter_by(code=code.strip().upper()).first()

    def find_by_code_excluding(self, code: str, exclude_id: uuid.UUID) -> CancellationPolicy | None:
        stmt = select(self.model_class).where(
            self.model_class.code == code.strip().upper(),
            self.model_class.id != exclude_id,
        )
        return db.session.scalars(stmt).first()

    def get(self, entity_id: uuid.UUID):
        return super().get(entity_id)
""")

write_f("app/modules/master/cancellation_policy/schemas.py", """
import re
from marshmallow import Schema, fields, validate, validates, ValidationError

class CreateCancellationPolicyRequestSchema(Schema):
    name               = fields.String(required=True, validate=validate.Length(min=1, max=100))
    code               = fields.String(required=True, validate=validate.Length(min=1, max=20))
    description        = fields.String(load_default=None, validate=validate.Length(max=2000))
    display_order      = fields.Integer(load_default=0, validate=validate.Range(min=0))
    is_active          = fields.Boolean(load_default=True)
    refund_percentage  = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0, max=100))
    days_before_travel = fields.Integer(required=True, validate=validate.Range(min=0))
    policy_type        = fields.String(load_default="PERCENTAGE", validate=validate.OneOf(["PERCENTAGE", "FLAT"]))

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class UpdateCancellationPolicyRequestSchema(Schema):
    name               = fields.String(validate=validate.Length(min=1, max=100))
    code               = fields.String(validate=validate.Length(min=1, max=20))
    description        = fields.String(allow_none=True, validate=validate.Length(max=2000))
    display_order      = fields.Integer(validate=validate.Range(min=0))
    is_active          = fields.Boolean()
    refund_percentage  = fields.Decimal(as_string=False, validate=validate.Range(min=0, max=100))
    days_before_travel = fields.Integer(validate=validate.Range(min=0))
    policy_type        = fields.String(validate=validate.OneOf(["PERCENTAGE", "FLAT"]))
    version            = fields.Integer(required=True)

    @validates("code")
    def validate_code(self, value, **kwargs):
        if not re.match(r"^[A-Z0-9_\-]+$", value.strip().upper()):
            raise ValidationError("Code must be uppercase letters, digits, underscores or hyphens.")
        return value.strip().upper()

class CancellationPolicyLookupResponseSchema(Schema):
    id   = fields.UUID()
    name = fields.String()
    code = fields.String()

class CancellationPolicySummaryResponseSchema(Schema):
    id                 = fields.UUID()
    name               = fields.String()
    code               = fields.String()
    is_active          = fields.Boolean()
    display_order      = fields.Integer()

class CancellationPolicyDetailResponseSchema(CancellationPolicySummaryResponseSchema):
    description        = fields.String()
    refund_percentage  = fields.Decimal(as_string=True)
    days_before_travel = fields.Integer()
    policy_type        = fields.String()
    version            = fields.Integer()
    audit_info         = fields.Method("get_audit_info")
    def get_audit_info(self, obj):
        return {
            "created_by": str(obj.created_by) if obj.created_by else None,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_by": str(obj.updated_by) if obj.updated_by else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
""")

write_f("app/modules/master/cancellation_policy/service.py", """
import uuid as _uuid_mod
from typing import Any
from flask_jwt_extended import get_jwt_identity
from app.core.base_service import BaseService
from app.domain.exceptions import BusinessException, NotFoundException
from .repository import CancellationPolicyRepository
from .models import CancellationPolicy

class CancellationPolicyService(BaseService):
    def __init__(self):
        self.repository = CancellationPolicyRepository()

    def _parse_uuid(self, raw_id):
        if isinstance(raw_id, _uuid_mod.UUID): return raw_id
        try: return _uuid_mod.UUID(str(raw_id))
        except (ValueError, AttributeError): raise NotFoundException("Cancellation policy not found.", code="ERR_NOT_FOUND")

    def create(self, data: dict) -> CancellationPolicy:
        code = data["code"].upper()
        if self.repository.find_by_code(code):
            raise BusinessException(f"Code '{code}' already exists.", code="ERR_DUPLICATE_CODE")
            
        entity = CancellationPolicy(
            code=code, name=data["name"], description=data.get("description"),
            display_order=data.get("display_order", 0), is_active=data.get("is_active", True),
            refund_percentage=data["refund_percentage"], days_before_travel=data["days_before_travel"],
            policy_type=data.get("policy_type", "PERCENTAGE"),
            created_by=get_jwt_identity(), updated_by=get_jwt_identity(),
        )
        self.repository.add(entity)
        self.commit()
        return entity

    def update(self, entity_id: str, data: dict) -> CancellationPolicy:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Cancellation policy not found.", code="ERR_NOT_FOUND")
        self.check_optimistic_lock(entity.version, data.get("version"))
        
        if "code" in data:
            new_code = data["code"].upper()
            if new_code != entity.code and self.repository.find_by_code_excluding(new_code, uid):
                raise BusinessException(f"Code '{new_code}' already exists.", code="ERR_DUPLICATE_CODE")
            entity.code = new_code
            
        for field in ("name", "description", "display_order", "is_active", "refund_percentage", "days_before_travel", "policy_type"):
            if field in data: setattr(entity, field, data[field])
            
        entity.version += 1
        entity.updated_by = get_jwt_identity()
        self.repository.add(entity)
        self.commit()
        return entity

    def delete(self, entity_id: str) -> None:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Cancellation policy not found.", code="ERR_NOT_FOUND")
        entity.is_active = False
        entity.version += 1
        entity.updated_by = get_jwt_identity()
        self.repository.add(entity)
        self.commit()

    def get(self, entity_id: str) -> CancellationPolicy:
        uid = self._parse_uuid(entity_id)
        entity = self.repository.get(uid)
        if not entity: raise NotFoundException("Cancellation policy not found.", code="ERR_NOT_FOUND")
        return entity

    def list(self, page=1, page_size=20, search=None, is_active=None, sort_by="display_order", sort_order="asc") -> Any:
        filters = {}
        if is_active is not None: filters["is_active"] = is_active
        return self.repository.paginate(page=page, page_size=page_size, search_query=search, sort_by=sort_by, sort_order=sort_order, **filters)
""")

write_f("app/modules/master/cancellation_policy/routes.py", """
from flask import Blueprint, request
from marshmallow import ValidationError
from app.modules.auth.permissions import permission_required
from app.domain.exceptions import BusinessException, NotFoundException, DomainException
from .schemas import (CreateCancellationPolicyRequestSchema, UpdateCancellationPolicyRequestSchema,
    CancellationPolicySummaryResponseSchema, CancellationPolicyDetailResponseSchema, CancellationPolicyLookupResponseSchema)
from .service import CancellationPolicyService
from . import cancellation_policy_bp

def _flatten_errors(messages):
    return [{"code": "ERR_VALIDATION", "field": f, "message": m}
            for f, msgs in messages.items() for m in (msgs if isinstance(msgs, list) else [msgs])]

@cancellation_policy_bp.route("", methods=["POST"])
@permission_required("master.cancellation_policy.create")
def create_cancellation_policy():
    service = CancellationPolicyService()
    try: data = CreateCancellationPolicyRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.create(data)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    resp, status = service.success(data=CancellationPolicyDetailResponseSchema().dump(entity), message="Cancellation policy created.", status_code=201)
    resp.headers["Location"] = f"/api/v1/masters/cancellation-policies/{entity.id}"
    return resp, status

@cancellation_policy_bp.route("", methods=["GET"])
@permission_required("master.cancellation_policy.read")
def list_cancellation_policies():
    service = CancellationPolicyService()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort_by", "display_order")
    sort_order = request.args.get("sort_order", "asc")
    is_active_raw = request.args.get("is_active")
    is_active = None if is_active_raw is None else is_active_raw.lower() == "true"
    result = service.list(page=page, page_size=page_size, search=search, is_active=is_active, sort_by=sort_by, sort_order=sort_order)
    return service.success(data={"items": CancellationPolicySummaryResponseSchema(many=True).dump(result.items), "pagination": {"page": result.page, "page_size": result.page_size, "total_records": result.total_records, "total_pages": result.total_pages}}, message="Cancellation policies retrieved.")

@cancellation_policy_bp.route("/lookup", methods=["GET"])
@permission_required("master.cancellation_policy.read")
def lookup_cancellation_policies():
    service = CancellationPolicyService()
    result = service.list(page=1, page_size=200, search=request.args.get("search"), is_active=True, sort_by="name", sort_order="asc")
    return service.success(data=CancellationPolicyLookupResponseSchema(many=True).dump(result.items), message="Cancellation policies lookup.")

@cancellation_policy_bp.route("/<id>", methods=["GET"])
@permission_required("master.cancellation_policy.read")
def get_cancellation_policy(id):
    service = CancellationPolicyService()
    try: entity = service.get(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    return service.success(data=CancellationPolicyDetailResponseSchema().dump(entity), message="Cancellation policy retrieved.")

@cancellation_policy_bp.route("/<id>", methods=["PUT"])
@permission_required("master.cancellation_policy.update")
def update_cancellation_policy(id):
    service = CancellationPolicyService()
    try: data = UpdateCancellationPolicyRequestSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err: return service.error("Validation failed.", code="ERR_VALIDATION", errors=_flatten_errors(err.messages), status_code=400)
    try: entity = service.update(id, data)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except (DomainException, BusinessException) as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(data=CancellationPolicyDetailResponseSchema().dump(entity), message="Cancellation policy updated.")

@cancellation_policy_bp.route("/<id>", methods=["DELETE"])
@permission_required("master.cancellation_policy.delete")
def delete_cancellation_policy(id):
    service = CancellationPolicyService()
    try: service.delete(id)
    except NotFoundException as err: return service.error(err.message, code=err.code, status_code=404)
    except BusinessException as err: return service.error(err.message, code=err.code, status_code=409)
    return service.success(message="Cancellation policy deactivated.")
""")

write_f("tests/modules/master/cancellation_policy/__init__.py", "")

write_f("tests/modules/master/cancellation_policy/test_cancellation_policy.py", """
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
            phone="9999999009", employee_code="TEST-CP01", role=role, is_active=True)
        db.session.add(tm)
        db.session.flush()
        user = UserAccount(team_member_id=tm.id, username="test@test.com",
            password_hash=bcrypt.generate_password_hash("pass").decode(), is_active=True)
        db.session.add(user)
        db.session.commit()
        return create_access_token(identity=str(user.id), additional_claims={"permissions": [
            "master.cancellation_policy.read", "master.cancellation_policy.create",
            "master.cancellation_policy.update", "master.cancellation_policy.delete"]})

@pytest.fixture
def no_perm_token(app):
    with app.app_context():
        return create_access_token(identity=str(uuid.uuid4()), additional_claims={"permissions": []})

def auth_headers(token): return {"Authorization": f"Bearer {token}"}

def test_create_cancellation_policy_success(client, auth_token):
    res = client.post("/api/v1/masters/cancellation-policies", json={"name": "No Refund", "code": "NO_REFUND", "refund_percentage": 0, "days_before_travel": 0}, headers=auth_headers(auth_token))
    assert res.status_code == 201
    assert res.json["data"]["code"] == "NO_REFUND"

def test_create_cancellation_policy_duplicate_code(client, auth_token):
    client.post("/api/v1/masters/cancellation-policies", json={"name": "No Refund", "code": "NO_REFUND", "refund_percentage": 0, "days_before_travel": 0}, headers=auth_headers(auth_token))
    res = client.post("/api/v1/masters/cancellation-policies", json={"name": "No Refund 2", "code": "NO_REFUND", "refund_percentage": 0, "days_before_travel": 0}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_DUPLICATE_CODE"

def test_create_invalid_refund_percentage(client, auth_token):
    res = client.post("/api/v1/masters/cancellation-policies", json={"name": "Invalid", "code": "INV", "refund_percentage": 150, "days_before_travel": 0}, headers=auth_headers(auth_token))
    assert res.status_code == 400
    assert res.json["code"] == "ERR_VALIDATION"
    assert any(e["field"] == "refund_percentage" for e in res.json["errors"])

def test_get_cancellation_policy_by_id(client, auth_token):
    create_res = client.post("/api/v1/masters/cancellation-policies", json={"name": "No Refund", "code": "NO_REFUND", "refund_percentage": 0, "days_before_travel": 0}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.get(f"/api/v1/masters/cancellation-policies/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["id"] == s_id

def test_get_cancellation_policy_not_found(client, auth_token):
    res = client.get(f"/api/v1/masters/cancellation-policies/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_get_cancellation_policy_invalid_uuid(client, auth_token):
    res = client.get("/api/v1/masters/cancellation-policies/invalid-id", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_list_cancellation_policies_pagination(client, auth_token):
    for i in range(5):
        client.post("/api/v1/masters/cancellation-policies", json={"name": f"P{i}", "code": f"P{i}", "refund_percentage": 10, "days_before_travel": 1}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/cancellation-policies?page=1&page_size=2", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 2
    assert res.json["data"]["pagination"]["total_records"] >= 5

def test_list_cancellation_policies_search(client, auth_token):
    client.post("/api/v1/masters/cancellation-policies", json={"name": "Half", "code": "HALF", "refund_percentage": 50, "days_before_travel": 5}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/cancellation-policies?search=HALF", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 1

def test_list_cancellation_policies_filter_is_active(client, auth_token):
    client.post("/api/v1/masters/cancellation-policies", json={"name": "Half", "code": "HALF", "refund_percentage": 50, "days_before_travel": 5, "is_active": False}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/cancellation-policies?is_active=false", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) >= 1

def test_list_cancellation_policies_sort(client, auth_token):
    client.post("/api/v1/masters/cancellation-policies", json={"name": "A", "code": "A", "refund_percentage": 10, "days_before_travel": 1, "display_order": 2}, headers=auth_headers(auth_token))
    client.post("/api/v1/masters/cancellation-policies", json={"name": "B", "code": "B", "refund_percentage": 10, "days_before_travel": 1, "display_order": 1}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/cancellation-policies?sort_by=display_order&sort_order=asc", headers=auth_headers(auth_token))
    items = res.json["data"]["items"]
    assert items[0]["display_order"] <= items[1]["display_order"]

def test_list_cancellation_policies_empty(client, auth_token):
    res = client.get("/api/v1/masters/cancellation-policies?search=NONEXISTENT", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 0

def test_update_cancellation_policy_success(client, auth_token):
    create_res = client.post("/api/v1/masters/cancellation-policies", json={"name": "Half", "code": "HALF", "refund_percentage": 50, "days_before_travel": 5}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/cancellation-policies/{s_id}", json={"name": "Half Updated", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["name"] == "Half Updated"
    assert res.json["data"]["version"] == 2

def test_update_cancellation_policy_version_conflict(client, auth_token):
    create_res = client.post("/api/v1/masters/cancellation-policies", json={"name": "Half", "code": "HALF", "refund_percentage": 50, "days_before_travel": 5}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/cancellation-policies/{s_id}", json={"name": "Half Updated", "version": 999}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_OPTIMISTIC_LOCK"

def test_update_cancellation_policy_not_found(client, auth_token):
    res = client.put(f"/api/v1/masters/cancellation-policies/{uuid.uuid4()}", json={"name": "X", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_delete_cancellation_policy_soft(client, auth_token):
    create_res = client.post("/api/v1/masters/cancellation-policies", json={"name": "Half", "code": "HALF", "refund_percentage": 50, "days_before_travel": 5}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.delete(f"/api/v1/masters/cancellation-policies/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    get_res = client.get(f"/api/v1/masters/cancellation-policies/{s_id}", headers=auth_headers(auth_token))
    assert get_res.json["data"]["is_active"] is False

def test_delete_cancellation_policy_not_found(client, auth_token):
    res = client.delete(f"/api/v1/masters/cancellation-policies/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_lookup_cancellation_policies(client, auth_token):
    client.post("/api/v1/masters/cancellation-policies", json={"name": "Half", "code": "HALF", "refund_percentage": 50, "days_before_travel": 5}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/cancellation-policies/lookup", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]) >= 1

def test_unauthorized(client):
    res = client.get("/api/v1/masters/cancellation-policies")
    assert res.status_code == 401

def test_forbidden(client, no_perm_token):
    res = client.get("/api/v1/masters/cancellation-policies", headers=auth_headers(no_perm_token))
    assert res.status_code == 403
""")

write_f("seeds/013_cancellation_policies.py", """
from app.core.extensions import db
from app.modules.master.cancellation_policy.models import CancellationPolicy
import uuid

def seed():
    data = [
        {'name':'No Refund','code':'NO_REFUND','refund_percentage':0,'days_before_travel':0,'description':'Cancelled on day of travel - no refund'},
        {'name':'25% Refund','code':'REFUND_25','refund_percentage':25,'days_before_travel':3,'description':'Cancelled 3-6 days before - 25% refund'},
        {'name':'50% Refund','code':'REFUND_50','refund_percentage':50,'days_before_travel':7,'description':'Cancelled 7-14 days before - 50% refund'},
        {'name':'75% Refund','code':'REFUND_75','refund_percentage':75,'days_before_travel':15,'description':'Cancelled 15-29 days before - 75% refund'},
        {'name':'Full Refund','code':'FULL_REFUND','refund_percentage':100,'days_before_travel':30,'description':'Cancelled 30+ days before - full refund'}
    ]
    for item in data:
        if not CancellationPolicy.query.filter_by(code=item['code']).first():
            entity = CancellationPolicy(
                id=uuid.uuid4(),
                **item,
                is_active=True,
                created_by=None,
                updated_by=None
            )
            db.session.add(entity)
    db.session.commit()
    print("Cancellation Policies seeded.")
""")
