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
            phone="9999999003", employee_code="TEST-MP01", role=role, is_active=True)
        db.session.add(tm)
        db.session.flush()
        user = UserAccount(team_member_id=tm.id, username="test@test.com",
            password_hash=bcrypt.generate_password_hash("pass").decode(), is_active=True)
        db.session.add(user)
        db.session.commit()
        return create_access_token(identity=str(user.id), additional_claims={"permissions": [
            "master.meal_plan.read", "master.meal_plan.create",
            "master.meal_plan.update", "master.meal_plan.delete"]})

@pytest.fixture
def no_perm_token(app):
    with app.app_context():
        return create_access_token(identity=str(uuid.uuid4()), additional_claims={"permissions": []})

def auth_headers(token): return {"Authorization": f"Bearer {token}"}

def test_create_success(client, auth_token):
    res = client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1", "description": "desc"}, headers=auth_headers(auth_token))
    assert res.status_code == 201
    assert res.json["data"]["name"] == "Test1"

def test_duplicate_code(client, auth_token):
    client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    res = client.post("/api/v1/masters/meal-plans", json={"name": "Test2", "code": "TEST1"}, headers=auth_headers(auth_token))
    assert res.status_code == 409

def test_create_validation_error(client, auth_token):
    res = client.post("/api/v1/masters/meal-plans", json={"name": ""}, headers=auth_headers(auth_token))
    assert res.status_code == 400

def test_get_by_id(client, auth_token):
    post_res = client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    uid = post_res.json["data"]["id"]
    res = client.get(f"/api/v1/masters/meal-plans/{uid}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["id"] == uid

def test_get_not_found(client, auth_token):
    res = client.get(f"/api/v1/masters/meal-plans/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_get_invalid_uuid(client, auth_token):
    res = client.get(f"/api/v1/masters/meal-plans/invalid", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_list_pagination(client, auth_token):
    client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    client.post("/api/v1/masters/meal-plans", json={"name": "Test2", "code": "TEST2"}, headers=auth_headers(auth_token))
    res = client.get(f"/api/v1/masters/meal-plans?page=1&page_size=1", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 1

def test_list_search(client, auth_token):
    client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    client.post("/api/v1/masters/meal-plans", json={"name": "Other", "code": "OTHER"}, headers=auth_headers(auth_token))
    res = client.get(f"/api/v1/masters/meal-plans?search=Test1", headers=auth_headers(auth_token))
    assert len(res.json["data"]["items"]) == 1

def test_list_filter_is_active(client, auth_token):
    post_res = client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    uid = post_res.json["data"]["id"]
    client.delete(f"/api/v1/masters/meal-plans/{uid}", headers=auth_headers(auth_token))
    res = client.get(f"/api/v1/masters/meal-plans?is_active=true", headers=auth_headers(auth_token))
    assert len(res.json["data"]["items"]) == 0

def test_list_sort(client, auth_token):
    client.post("/api/v1/masters/meal-plans", json={"name": "B", "code": "B", "display_order": 2}, headers=auth_headers(auth_token))
    client.post("/api/v1/masters/meal-plans", json={"name": "A", "code": "A", "display_order": 1}, headers=auth_headers(auth_token))
    res = client.get(f"/api/v1/masters/meal-plans?sort_by=display_order&sort_order=asc", headers=auth_headers(auth_token))
    assert res.json["data"]["items"][0]["code"] == "A"

def test_list_empty(client, auth_token):
    res = client.get("/api/v1/masters/meal-plans", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 0

def test_update_success(client, auth_token):
    post_res = client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    uid = post_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/meal-plans/{uid}", json={"name": "Test2", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["name"] == "Test2"

def test_update_version_conflict(client, auth_token):
    post_res = client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    uid = post_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/meal-plans/{uid}", json={"name": "Test2", "version": 0}, headers=auth_headers(auth_token))
    assert res.status_code == 409

def test_update_not_found(client, auth_token):
    res = client.put(f"/api/v1/masters/meal-plans/{uuid.uuid4()}", json={"name": "Test2", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_delete_soft(client, auth_token):
    post_res = client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    uid = post_res.json["data"]["id"]
    res = client.delete(f"/api/v1/masters/meal-plans/{uid}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    get_res = client.get(f"/api/v1/masters/meal-plans/{uid}", headers=auth_headers(auth_token))
    assert get_res.json["data"]["is_active"] is False

def test_delete_not_found(client, auth_token):
    res = client.delete(f"/api/v1/masters/meal-plans/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_lookup_endpoint(client, auth_token):
    client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(auth_token))
    res = client.get(f"/api/v1/masters/meal-plans/lookup", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]) > 0

def test_unauthorized(client):
    res = client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"})
    assert res.status_code == 401

def test_forbidden(client, no_perm_token):
    res = client.post("/api/v1/masters/meal-plans", json={"name": "Test1", "code": "TEST1"}, headers=auth_headers(no_perm_token))
    assert res.status_code == 403
