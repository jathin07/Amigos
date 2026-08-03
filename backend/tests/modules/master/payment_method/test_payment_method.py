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
