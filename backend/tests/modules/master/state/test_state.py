import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role
from app.core.extensions import bcrypt
from app.modules.master.state.models import State
from app.modules.master.country.models import Country


# ─────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_token(app):
    """Create a user with state permissions and return a valid JWT."""
    with app.app_context():
        role = Role(
            name="Master Admin",
            code="MASTER_ADMIN",
            is_system=True,
        )
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="State",
            display_name="State Admin",
            official_email="state@test.com",
            phone="9999999998",
            employee_code="STEST01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="state@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "master.state.read",
                "master.state.create",
                "master.state.update",
                "master.state.delete",
            ]},
        )
        return token


@pytest.fixture
def no_perm_token(app):
    """JWT with no permissions."""
    with app.app_context():
        token = create_access_token(
            identity=str(uuid.uuid4()),
            additional_claims={"permissions": []},
        )
        return token


@pytest.fixture
def test_country(app):
    """Create a country for foreign key references."""
    with app.app_context():
        country = Country(
            name="India",
            code="IN",
            phone_code="+91",
            display_order=1,
            is_active=True
        )
        db.session.add(country)
        db.session.commit()
        return country.id


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _create_state(client, token, country_id, payload=None):
    payload = payload or {
        "name": "Kerala",
        "code": "KL",
        "country_id": str(country_id),
        "description": "God's Own Country",
        "display_order": 1,
    }
    return client.post(
        "/api/v1/masters/states",
        json=payload,
        headers=auth_headers(token),
    )


# ─────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────

def test_create_success(client, auth_token, test_country):
    resp = _create_state(client, auth_token, test_country)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["code"] == "KL"
    assert "Location" in resp.headers


def test_duplicate_code(client, auth_token, test_country):
    _create_state(client, auth_token, test_country)
    resp = _create_state(client, auth_token, test_country)
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_DUPLICATE_CODE"


def test_invalid_country(client, auth_token):
    resp = _create_state(client, auth_token, uuid.uuid4())
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_INVALID_COUNTRY"


def test_create_validation_error(client, auth_token):
    resp = client.post(
        "/api/v1/masters/states",
        json={"name": "Kerala"},  # Missing code and country_id
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 400


def test_get_by_id(client, auth_token, test_country):
    create_resp = _create_state(client, auth_token, test_country)
    state_id = create_resp.get_json()["data"]["id"]

    resp = client.get(f"/api/v1/masters/states/{state_id}", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == state_id
    assert "audit_info" in data


def test_get_not_found(client, auth_token):
    resp = client.get(f"/api/v1/masters/states/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert resp.status_code == 404


def test_get_invalid_uuid(client, auth_token):
    resp = client.get(
        "/api/v1/masters/states/not-a-real-uuid",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 404


def test_list_pagination(client, auth_token, test_country):
    states = [
        {"name": "Kerala",      "code": "KL", "country_id": str(test_country)},
        {"name": "Tamil Nadu",  "code": "TN", "country_id": str(test_country)},
        {"name": "Karnataka",   "code": "KA", "country_id": str(test_country)},
        {"name": "Maharashtra", "code": "MH", "country_id": str(test_country)},
        {"name": "Goa",         "code": "GA", "country_id": str(test_country)},
    ]
    for s in states:
        _create_state(client, auth_token, test_country, s)

    resp = client.get(
        "/api/v1/masters/states?page=1&page_size=2",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 5
    assert data["pagination"]["total_pages"] == 3
    assert len(data["items"]) == 2


def test_list_search(client, auth_token, test_country):
    _create_state(client, auth_token, test_country, {"name": "Kerala",     "code": "KL", "country_id": str(test_country)})
    _create_state(client, auth_token, test_country, {"name": "Karnataka",  "code": "KA", "country_id": str(test_country)})
    _create_state(client, auth_token, test_country, {"name": "Tamil Nadu", "code": "TN", "country_id": str(test_country)})

    resp = client.get(
        "/api/v1/masters/states?search=na",
        headers=auth_headers(auth_token),
    )
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 2


def test_list_filter_is_active(client, auth_token, test_country):
    _create_state(client, auth_token, test_country, {"name": "Kerala", "code": "KL", "country_id": str(test_country)})
    _create_state(client, auth_token, test_country, {"name": "Goa", "code": "GA", "country_id": str(test_country), "is_active": False})

    resp = client.get(
        "/api/v1/masters/states?is_active=true",
        headers=auth_headers(auth_token),
    )
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 1
    assert data["items"][0]["code"] == "KL"


def test_list_sort(client, auth_token, test_country):
    _create_state(client, auth_token, test_country, {"name": "Zulu",  "code": "ZZ", "country_id": str(test_country)})
    _create_state(client, auth_token, test_country, {"name": "Alpha", "code": "AA", "country_id": str(test_country)})

    resp = client.get(
        "/api/v1/masters/states?sort_by=name&sort_order=asc",
        headers=auth_headers(auth_token),
    )
    items = resp.get_json()["data"]["items"]
    assert items[0]["name"] == "Alpha"
    assert items[1]["name"] == "Zulu"


def test_list_empty(client, auth_token):
    resp = client.get("/api/v1/masters/states", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 0
    assert data["items"] == []


def test_list_states(client, auth_token, test_country):
    _create_state(client, auth_token, test_country, {"name": "Kerala", "code": "KL", "country_id": str(test_country)})
    _create_state(client, auth_token, test_country, {"name": "Tamil Nadu", "code": "TN", "country_id": str(test_country)})

    resp = client.get(
        "/api/v1/masters/states?page=1&page_size=10",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 2


def test_list_by_country_id(client, auth_token, test_country, app):
    # Add second country
    with app.app_context():
        c2 = Country(name="USA", code="US", phone_code="+1", is_active=True)
        db.session.add(c2)
        db.session.commit()
        us_id = str(c2.id)

    _create_state(client, auth_token, test_country, {"name": "Kerala", "code": "KL", "country_id": str(test_country)})
    _create_state(client, auth_token, us_id, {"name": "California", "code": "CA", "country_id": us_id})

    resp = client.get(
        f"/api/v1/masters/states?country_id={us_id}",
        headers=auth_headers(auth_token),
    )
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 1
    assert data["items"][0]["code"] == "CA"


def test_update_success(client, auth_token, test_country):
    create_resp = _create_state(client, auth_token, test_country)
    state_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/states/{state_id}",
        json={"name": "Kerala Updated", "version": 1},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["name"] == "Kerala Updated"


def test_update_version_conflict(client, auth_token, test_country):
    create_resp = _create_state(client, auth_token, test_country)
    state_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/states/{state_id}",
        json={"name": "Conflict", "version": 99},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_CONCURRENT_MODIFICATION"


def test_update_not_found(client, auth_token):
    resp = client.put(
        f"/api/v1/masters/states/{uuid.uuid4()}",
        json={"name": "Missing", "version": 1},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 404


def test_delete_soft(client, auth_token, test_country, app):
    create_resp = _create_state(client, auth_token, test_country)
    state_id = create_resp.get_json()["data"]["id"]

    resp = client.delete(
        f"/api/v1/masters/states/{state_id}",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200

    with app.app_context():
        from app.modules.master.state.repository import StateRepository
        repo = StateRepository()
        state = repo.get_by_id(uuid.UUID(state_id))
        assert state is not None
        assert state.is_active is False


def test_delete_not_found(client, auth_token):
    resp = client.delete(
        f"/api/v1/masters/states/{uuid.uuid4()}",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 404


def test_delete_blocked_by_district(client, auth_token, test_country, app):
    """A state that has active districts should NOT be deactivatable."""
    from app.modules.master.district.models import District
    import uuid as _uuid

    create_resp = _create_state(client, auth_token, test_country)
    state_id = create_resp.get_json()["data"]["id"]

    # Insert an active district directly into the test DB session
    d = District(
        name="Test District",
        code="TDX",
        state_id=_uuid.UUID(state_id),
        is_active=True,
    )
    db.session.add(d)
    db.session.commit()

    resp = client.delete(
        f"/api/v1/masters/states/{state_id}",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_ENTITY_IN_USE"


def test_lookup_endpoint(client, auth_token, test_country):
    _create_state(client, auth_token, test_country, {"name": "Kerala", "code": "KL", "country_id": str(test_country)})
    _create_state(client, auth_token, test_country, {"name": "Goa", "code": "GA", "country_id": str(test_country), "is_active": False})

    resp = client.get("/api/v1/masters/states/lookup", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    items = resp.get_json()["data"]["items"]
    assert len(items) == 1
    assert set(items[0].keys()) == {"id", "name", "code"}


def test_lookup_by_country(client, auth_token, test_country, app):
    with app.app_context():
        us = Country(name="USA", code="US", phone_code="+1", is_active=True)
        db.session.add(us)
        db.session.commit()
        us_id = str(us.id)

    _create_state(client, auth_token, test_country, {"name": "Kerala", "code": "KL", "country_id": str(test_country)})
    _create_state(client, auth_token, us_id, {"name": "California", "code": "CA", "country_id": us_id})

    resp = client.get(
        f"/api/v1/masters/states/lookup?country_id={us_id}",
        headers=auth_headers(auth_token),
    )
    items = resp.get_json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["code"] == "CA"


def test_same_code_different_countries(client, auth_token, test_country, app):
    with app.app_context():
        us = Country(name="USA", code="US", phone_code="+1", is_active=True)
        db.session.add(us)
        db.session.commit()
        us_id = str(us.id)

    resp1 = _create_state(client, auth_token, test_country, {"name": "California India", "code": "CA", "country_id": str(test_country)})
    resp2 = _create_state(client, auth_token, us_id, {"name": "California", "code": "CA", "country_id": us_id})

    assert resp1.status_code == 201
    assert resp2.status_code == 201


def test_unauthorized(client):
    resp = client.get("/api/v1/masters/states")
    assert resp.status_code == 401


def test_forbidden(client, no_perm_token):
    resp = client.get("/api/v1/masters/states", headers=auth_headers(no_perm_token))
    assert resp.status_code == 403
