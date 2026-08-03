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
