import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role
from app.core.extensions import bcrypt
from app.modules.master.district.models import District
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
    """Create a user with district permissions and return a valid JWT."""
    with app.app_context():
        role = Role(name="Master Admin", code="MASTER_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="District",
            display_name="District Admin",
            official_email="district@test.com",
            phone="9999999997",
            employee_code="DTEST01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="district@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "master.district.read",
                "master.district.create",
                "master.district.update",
                "master.district.delete",
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
def test_state(app):
    """Create country + state for FK references and return state.id."""
    with app.app_context():
        country = Country(name="India", code="IN", phone_code="+91", display_order=1, is_active=True)
        db.session.add(country)
        db.session.flush()

        state = State(name="Kerala", code="KL", country_id=country.id, is_active=True)
        db.session.add(state)
        db.session.commit()
        return state.id


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _create_district(client, token, state_id, payload=None):
    payload = payload or {
        "name": "Ernakulam",
        "code": "EKM",
        "state_id": str(state_id),
        "description": "Commercial Capital",
        "display_order": 1,
    }
    return client.post(
        "/api/v1/masters/districts",
        json=payload,
        headers=auth_headers(token),
    )


# ─────────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────────

def test_create_success(client, auth_token, test_state):
    resp = _create_district(client, auth_token, test_state)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["code"] == "EKM"
    assert "Location" in resp.headers


def test_duplicate_code(client, auth_token, test_state):
    _create_district(client, auth_token, test_state)
    resp = _create_district(client, auth_token, test_state)
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_DUPLICATE_CODE"


def test_create_validation_error(client, auth_token):
    resp = client.post(
        "/api/v1/masters/districts",
        json={"name": "Ernakulam"},  # Missing code and state_id
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 400


def test_invalid_state(client, auth_token):
    resp = _create_district(client, auth_token, uuid.uuid4())
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_INVALID_STATE"


# ─────────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────────

def test_get_by_id(client, auth_token, test_state):
    create_resp = _create_district(client, auth_token, test_state)
    district_id = create_resp.get_json()["data"]["id"]

    resp = client.get(f"/api/v1/masters/districts/{district_id}", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == district_id
    assert "audit_info" in data
    assert "state_id" in data


def test_get_not_found(client, auth_token):
    resp = client.get(f"/api/v1/masters/districts/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert resp.status_code == 404


def test_get_invalid_uuid(client, auth_token):
    resp = client.get("/api/v1/masters/districts/not-a-uuid", headers=auth_headers(auth_token))
    assert resp.status_code == 404  # service raises NotFoundException on bad UUID


# ─────────────────────────────────────────────────────────────────
# LIST
# ─────────────────────────────────────────────────────────────────

def test_list_pagination(client, auth_token, test_state):
    _create_district(client, auth_token, test_state, {"name": "Ernakulam",       "code": "EKM", "state_id": str(test_state)})
    _create_district(client, auth_token, test_state, {"name": "Thiruvananthapuram", "code": "TVM", "state_id": str(test_state)})
    _create_district(client, auth_token, test_state, {"name": "Kozhikode",       "code": "CCJ", "state_id": str(test_state)})

    resp = client.get("/api/v1/masters/districts?page=1&page_size=2", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data["items"]) == 2
    assert data["pagination"]["total_records"] == 3
    assert data["pagination"]["total_pages"] == 2


def test_list_search(client, auth_token, test_state):
    _create_district(client, auth_token, test_state, {"name": "Ernakulam",  "code": "EKM", "state_id": str(test_state)})
    _create_district(client, auth_token, test_state, {"name": "Kozhikode",  "code": "CCJ", "state_id": str(test_state)})

    resp = client.get("/api/v1/masters/districts?search=Kozhi", headers=auth_headers(auth_token))
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 1
    assert data["items"][0]["code"] == "CCJ"


def test_list_filter_is_active(client, auth_token, test_state):
    create_resp = _create_district(client, auth_token, test_state)
    district_id = create_resp.get_json()["data"]["id"]

    # Soft-delete it
    client.delete(f"/api/v1/masters/districts/{district_id}", headers=auth_headers(auth_token))

    # Filter active only
    resp = client.get("/api/v1/masters/districts?is_active=true", headers=auth_headers(auth_token))
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 0


def test_list_sort(client, auth_token, test_state):
    _create_district(client, auth_token, test_state, {"name": "Wayanad",    "code": "WYD", "state_id": str(test_state), "display_order": 2})
    _create_district(client, auth_token, test_state, {"name": "Alappuzha",  "code": "ALP", "state_id": str(test_state), "display_order": 1})

    resp = client.get("/api/v1/masters/districts?sort_by=display_order&sort_order=asc", headers=auth_headers(auth_token))
    items = resp.get_json()["data"]["items"]
    assert items[0]["code"] == "ALP"
    assert items[1]["code"] == "WYD"


def test_list_empty(client, auth_token):
    resp = client.get("/api/v1/masters/districts", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["items"] == []
    assert data["pagination"]["total_records"] == 0


def test_list_by_state_id(client, auth_token, test_state, app):
    with app.app_context():
        c = Country.query.first()
        s2 = State(name="Tamil Nadu", code="TN", country_id=c.id, is_active=True)
        db.session.add(s2)
        db.session.commit()
        tn_id = str(s2.id)

    _create_district(client, auth_token, test_state, {"name": "Ernakulam", "code": "EKM", "state_id": str(test_state)})
    _create_district(client, auth_token, tn_id, {"name": "Chennai", "code": "MAA", "state_id": tn_id})

    resp = client.get(f"/api/v1/masters/districts?state_id={tn_id}", headers=auth_headers(auth_token))
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 1
    assert data["items"][0]["code"] == "MAA"


# ─────────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────────

def test_update_success(client, auth_token, test_state):
    create_resp = _create_district(client, auth_token, test_state)
    district_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/districts/{district_id}",
        json={"name": "Kochi Metropolitan", "version": 1},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["name"] == "Kochi Metropolitan"


def test_update_version_conflict(client, auth_token, test_state):
    create_resp = _create_district(client, auth_token, test_state)
    district_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/districts/{district_id}",
        json={"name": "Conflict", "version": 99},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_CONCURRENT_MODIFICATION"


def test_update_not_found(client, auth_token):
    resp = client.put(
        f"/api/v1/masters/districts/{uuid.uuid4()}",
        json={"name": "Ghost", "version": 1},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────────────────────────

def test_delete_soft(client, auth_token, test_state, app):
    create_resp = _create_district(client, auth_token, test_state)
    district_id = create_resp.get_json()["data"]["id"]

    resp = client.delete(f"/api/v1/masters/districts/{district_id}", headers=auth_headers(auth_token))
    assert resp.status_code == 200

    with app.app_context():
        from app.modules.master.district.repository import DistrictRepository
        repo = DistrictRepository()
        district = repo.get(uuid.UUID(district_id))
        assert district is not None
        assert district.is_active is False


def test_delete_not_found(client, auth_token):
    resp = client.delete(f"/api/v1/masters/districts/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────
# LOOKUP
# ─────────────────────────────────────────────────────────────────

def test_lookup_endpoint(client, auth_token, test_state):
    _create_district(client, auth_token, test_state, {"name": "Ernakulam", "code": "EKM", "state_id": str(test_state)})
    _create_district(client, auth_token, test_state, {"name": "Kozhikode", "code": "CCJ", "state_id": str(test_state)})

    resp = client.get("/api/v1/masters/districts/lookup", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    items = resp.get_json()["data"]
    assert len(items) == 2
    assert all("id" in d and "name" in d and "code" in d for d in items)
    # Lookup only returns active — confirm no is_active or version in response
    assert "is_active" not in items[0]
    assert "version" not in items[0]


def test_lookup_filtered_by_state(client, auth_token, test_state, app):
    """Lookup respects state_id filter."""
    with app.app_context():
        c = Country.query.first()
        s2 = State(name="Goa", code="GA", country_id=c.id, is_active=True)
        db.session.add(s2)
        db.session.commit()
        goa_id = str(s2.id)

    _create_district(client, auth_token, test_state, {"name": "Ernakulam", "code": "EKM", "state_id": str(test_state)})
    _create_district(client, auth_token, goa_id, {"name": "North Goa", "code": "NGO", "state_id": goa_id})

    resp = client.get(f"/api/v1/masters/districts/lookup?state_id={goa_id}", headers=auth_headers(auth_token))
    items = resp.get_json()["data"]
    assert len(items) == 1
    assert items[0]["code"] == "NGO"


# ─────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────

def test_unauthorized(client):
    resp = client.get("/api/v1/masters/districts")
    assert resp.status_code == 401


def test_forbidden(client, no_perm_token):
    resp = client.get("/api/v1/masters/districts", headers=auth_headers(no_perm_token))
    assert resp.status_code == 403
