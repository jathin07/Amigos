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
            phone="9999999008", employee_code="TEST-CU01", role=role, is_active=True)
        db.session.add(tm)
        db.session.flush()
        user = UserAccount(team_member_id=tm.id, username="test@test.com",
            password_hash=bcrypt.generate_password_hash("pass").decode(), is_active=True)
        db.session.add(user)
        db.session.commit()
        return create_access_token(identity=str(user.id), additional_claims={"permissions": [
            "master.currency.read", "master.currency.create",
            "master.currency.update", "master.currency.delete"]})

@pytest.fixture
def no_perm_token(app):
    with app.app_context():
        return create_access_token(identity=str(uuid.uuid4()), additional_claims={"permissions": []})

def auth_headers(token): return {"Authorization": f"Bearer {token}"}

def test_create_currency_success(client, auth_token):
    res = client.post("/api/v1/masters/currencies", json={"name": "Dollar", "code": "USD", "symbol": "$"}, headers=auth_headers(auth_token))
    assert res.status_code == 201
    assert res.json["data"]["code"] == "USD"
    assert res.json["data"]["symbol"] == "$"

def test_create_currency_duplicate_code(client, auth_token):
    client.post("/api/v1/masters/currencies", json={"name": "Dollar", "code": "USD", "symbol": "$"}, headers=auth_headers(auth_token))
    res = client.post("/api/v1/masters/currencies", json={"name": "Dollar 2", "code": "USD", "symbol": "$"}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_DUPLICATE_CODE"

def test_create_currency_validation_error(client, auth_token):
    res = client.post("/api/v1/masters/currencies", json={"name": ""}, headers=auth_headers(auth_token))
    assert res.status_code == 400
    assert res.json["code"] == "ERR_VALIDATION"

def test_get_currency_by_id(client, auth_token):
    create_res = client.post("/api/v1/masters/currencies", json={"name": "Dollar", "code": "USD", "symbol": "$"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.get(f"/api/v1/masters/currencies/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["id"] == s_id

def test_get_currency_not_found(client, auth_token):
    res = client.get(f"/api/v1/masters/currencies/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_get_currency_invalid_uuid(client, auth_token):
    res = client.get("/api/v1/masters/currencies/invalid-id", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_list_currencies_pagination(client, auth_token):
    for i in range(5):
        client.post("/api/v1/masters/currencies", json={"name": f"C{i}", "code": f"C{i}", "symbol": "$"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/currencies?page=1&page_size=2", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 2
    assert res.json["data"]["pagination"]["total_records"] >= 5

def test_list_currencies_search(client, auth_token):
    client.post("/api/v1/masters/currencies", json={"name": "Rupee", "code": "INR", "symbol": "₹"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/currencies?search=INR", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 1

def test_list_currencies_filter_is_active(client, auth_token):
    client.post("/api/v1/masters/currencies", json={"name": "Rupee", "code": "INR", "symbol": "₹", "is_active": False}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/currencies?is_active=false", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) >= 1

def test_list_currencies_sort(client, auth_token):
    client.post("/api/v1/masters/currencies", json={"name": "A", "code": "A", "symbol": "$", "display_order": 2}, headers=auth_headers(auth_token))
    client.post("/api/v1/masters/currencies", json={"name": "B", "code": "B", "symbol": "$", "display_order": 1}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/currencies?sort_by=display_order&sort_order=asc", headers=auth_headers(auth_token))
    items = res.json["data"]["items"]
    assert items[0]["display_order"] <= items[1]["display_order"]

def test_list_currencies_empty(client, auth_token):
    res = client.get("/api/v1/masters/currencies?search=NONEXISTENT", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 0

def test_update_currency_success(client, auth_token):
    create_res = client.post("/api/v1/masters/currencies", json={"name": "Rupee", "code": "INR", "symbol": "₹"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/currencies/{s_id}", json={"name": "Indian Rupee", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["name"] == "Indian Rupee"
    assert res.json["data"]["version"] == 2

def test_update_currency_version_conflict(client, auth_token):
    create_res = client.post("/api/v1/masters/currencies", json={"name": "Rupee", "code": "INR", "symbol": "₹"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/currencies/{s_id}", json={"name": "Indian Rupee", "version": 999}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_OPTIMISTIC_LOCK"

def test_update_currency_not_found(client, auth_token):
    res = client.put(f"/api/v1/masters/currencies/{uuid.uuid4()}", json={"name": "X", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_delete_currency_soft(client, auth_token):
    create_res = client.post("/api/v1/masters/currencies", json={"name": "Rupee", "code": "INR", "symbol": "₹"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.delete(f"/api/v1/masters/currencies/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    get_res = client.get(f"/api/v1/masters/currencies/{s_id}", headers=auth_headers(auth_token))
    assert get_res.json["data"]["is_active"] is False

def test_delete_currency_not_found(client, auth_token):
    res = client.delete(f"/api/v1/masters/currencies/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_lookup_currencies(client, auth_token):
    client.post("/api/v1/masters/currencies", json={"name": "Rupee", "code": "INR", "symbol": "₹"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/currencies/lookup", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]) >= 1

def test_only_one_default(client, auth_token):
    r1 = client.post("/api/v1/masters/currencies", json={"name": "Rupee", "code": "INR", "symbol": "₹", "is_default": True}, headers=auth_headers(auth_token))
    assert r1.json["data"]["is_default"] is True
    id1 = r1.json["data"]["id"]
    
    r2 = client.post("/api/v1/masters/currencies", json={"name": "Dollar", "code": "USD", "symbol": "$", "is_default": True}, headers=auth_headers(auth_token))
    assert r2.json["data"]["is_default"] is True
    id2 = r2.json["data"]["id"]
    
    get1 = client.get(f"/api/v1/masters/currencies/{id1}", headers=auth_headers(auth_token))
    assert get1.json["data"]["is_default"] is False

def test_unauthorized(client):
    res = client.get("/api/v1/masters/currencies")
    assert res.status_code == 401

def test_forbidden(client, no_perm_token):
    res = client.get("/api/v1/masters/currencies", headers=auth_headers(no_perm_token))
    assert res.status_code == 403
