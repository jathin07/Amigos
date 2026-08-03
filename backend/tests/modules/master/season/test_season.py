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
            phone="9999999006", employee_code="TEST-SN01", role=role, is_active=True)
        db.session.add(tm)
        db.session.flush()
        user = UserAccount(team_member_id=tm.id, username="test@test.com",
            password_hash=bcrypt.generate_password_hash("pass").decode(), is_active=True)
        db.session.add(user)
        db.session.commit()
        return create_access_token(identity=str(user.id), additional_claims={"permissions": [
            "master.season.read", "master.season.create",
            "master.season.update", "master.season.delete"]})

@pytest.fixture
def no_perm_token(app):
    with app.app_context():
        return create_access_token(identity=str(uuid.uuid4()), additional_claims={"permissions": []})

def auth_headers(token): return {"Authorization": f"Bearer {token}"}

def test_create_season_success(client, auth_token):
    res = client.post("/api/v1/masters/seasons", json={"name": "Winter", "code": "WINTER"}, headers=auth_headers(auth_token))
    assert res.status_code == 201
    assert res.json["data"]["code"] == "WINTER"

def test_create_season_duplicate_code(client, auth_token):
    client.post("/api/v1/masters/seasons", json={"name": "Winter", "code": "WINTER"}, headers=auth_headers(auth_token))
    res = client.post("/api/v1/masters/seasons", json={"name": "Winter 2", "code": "WINTER"}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_DUPLICATE_CODE"

def test_create_season_validation_error(client, auth_token):
    res = client.post("/api/v1/masters/seasons", json={"name": ""}, headers=auth_headers(auth_token))
    assert res.status_code == 400
    assert res.json["code"] == "ERR_VALIDATION"

def test_get_season_by_id(client, auth_token):
    create_res = client.post("/api/v1/masters/seasons", json={"name": "Winter", "code": "WINTER"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.get(f"/api/v1/masters/seasons/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["id"] == s_id

def test_get_season_not_found(client, auth_token):
    res = client.get(f"/api/v1/masters/seasons/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_get_season_invalid_uuid(client, auth_token):
    res = client.get("/api/v1/masters/seasons/invalid-id", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_list_seasons_pagination(client, auth_token):
    for i in range(5):
        client.post("/api/v1/masters/seasons", json={"name": f"S{i}", "code": f"S{i}"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/seasons?page=1&page_size=2", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 2
    assert res.json["data"]["pagination"]["total_records"] >= 5

def test_list_seasons_search(client, auth_token):
    client.post("/api/v1/masters/seasons", json={"name": "Summer", "code": "SUMMER"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/seasons?search=SUMMER", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 1

def test_list_seasons_filter_is_active(client, auth_token):
    client.post("/api/v1/masters/seasons", json={"name": "Summer", "code": "SUMMER", "is_active": False}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/seasons?is_active=false", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) >= 1

def test_list_seasons_sort(client, auth_token):
    client.post("/api/v1/masters/seasons", json={"name": "A", "code": "A", "display_order": 2}, headers=auth_headers(auth_token))
    client.post("/api/v1/masters/seasons", json={"name": "B", "code": "B", "display_order": 1}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/seasons?sort_by=display_order&sort_order=asc", headers=auth_headers(auth_token))
    items = res.json["data"]["items"]
    assert items[0]["display_order"] <= items[1]["display_order"]

def test_list_seasons_empty(client, auth_token):
    res = client.get("/api/v1/masters/seasons?search=NONEXISTENT", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]["items"]) == 0

def test_update_season_success(client, auth_token):
    create_res = client.post("/api/v1/masters/seasons", json={"name": "Winter", "code": "WINTER"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/seasons/{s_id}", json={"name": "Winter Updated", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.json["data"]["name"] == "Winter Updated"
    assert res.json["data"]["version"] == 2

def test_update_season_version_conflict(client, auth_token):
    create_res = client.post("/api/v1/masters/seasons", json={"name": "Winter", "code": "WINTER"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.put(f"/api/v1/masters/seasons/{s_id}", json={"name": "Winter Updated", "version": 999}, headers=auth_headers(auth_token))
    assert res.status_code == 409
    assert res.json["code"] == "ERR_OPTIMISTIC_LOCK"

def test_update_season_not_found(client, auth_token):
    res = client.put(f"/api/v1/masters/seasons/{uuid.uuid4()}", json={"name": "X", "version": 1}, headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_delete_season_soft(client, auth_token):
    create_res = client.post("/api/v1/masters/seasons", json={"name": "Winter", "code": "WINTER"}, headers=auth_headers(auth_token))
    s_id = create_res.json["data"]["id"]
    res = client.delete(f"/api/v1/masters/seasons/{s_id}", headers=auth_headers(auth_token))
    assert res.status_code == 200
    get_res = client.get(f"/api/v1/masters/seasons/{s_id}", headers=auth_headers(auth_token))
    assert get_res.json["data"]["is_active"] is False

def test_delete_season_not_found(client, auth_token):
    res = client.delete(f"/api/v1/masters/seasons/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert res.status_code == 404

def test_lookup_seasons(client, auth_token):
    client.post("/api/v1/masters/seasons", json={"name": "Winter", "code": "WINTER"}, headers=auth_headers(auth_token))
    res = client.get("/api/v1/masters/seasons/lookup", headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert len(res.json["data"]) >= 1

def test_unauthorized(client):
    res = client.get("/api/v1/masters/seasons")
    assert res.status_code == 401

def test_forbidden(client, no_perm_token):
    res = client.get("/api/v1/masters/seasons", headers=auth_headers(no_perm_token))
    assert res.status_code == 403
