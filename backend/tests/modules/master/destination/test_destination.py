import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role
from app.core.extensions import bcrypt
from app.modules.master.destination.models import Destination
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
    """Create a user with destination permissions and return a valid JWT."""
    with app.app_context():
        role = Role(name="Master Admin", code="MASTER_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Destination",
            display_name="Destination Admin",
            official_email="destination@test.com",
            phone="9999999996",
            employee_code="DEST01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="destination@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "master.destination.read",
                "master.destination.create",
                "master.destination.update",
                "master.destination.delete",
            ]},
        )
        return token


@pytest.fixture
def no_perm_token(app):
    with app.app_context():
        return create_access_token(
            identity=str(uuid.uuid4()),
            additional_claims={"permissions": []},
        )


@pytest.fixture
def hierarchy(app):
    """
    Build Country → State → District and return their IDs.
    Returns dict: {country_id, state_id, district_id} — all UUID objects.
    """
    with app.app_context():
        country = Country(name="India", code="IN", phone_code="+91", is_active=True)
        db.session.add(country)
        db.session.flush()

        state = State(name="Kerala", code="KL", country_id=country.id, is_active=True)
        db.session.add(state)
        db.session.flush()

        district = District(name="Idukki", code="IDK", state_id=state.id, is_active=True)
        db.session.add(district)
        db.session.commit()

        return {
            "country_id":  country.id,
            "state_id":    state.id,
            "district_id": district.id,
        }


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _create_destination(client, token, hierarchy, payload=None):
    payload = payload or {
        "name":        "Munnar",
        "code":        "MUN",
        "slug":        "munnar",
        "country_id":  str(hierarchy["country_id"]),
        "state_id":    str(hierarchy["state_id"]),
        "district_id": str(hierarchy["district_id"]),
        "description": "Hill station in Idukki",
        "display_order": 1,
    }
    return client.post(
        "/api/v1/masters/destinations",
        json=payload,
        headers=auth_headers(token),
    )


# ─────────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────────

def test_create_success(client, auth_token, hierarchy):
    resp = _create_destination(client, auth_token, hierarchy)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["code"] == "MUN"
    assert data["data"]["slug"] == "munnar"
    assert "Location" in resp.headers


def test_duplicate_code(client, auth_token, hierarchy):
    _create_destination(client, auth_token, hierarchy)
    resp = _create_destination(client, auth_token, hierarchy)
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_DUPLICATE_CODE"


def test_duplicate_slug(client, auth_token, hierarchy):
    _create_destination(client, auth_token, hierarchy)
    # Same slug, different code
    resp = _create_destination(client, auth_token, hierarchy, {
        "name": "Munnar 2", "code": "MUN2", "slug": "munnar",
        "country_id": str(hierarchy["country_id"]),
        "state_id":   str(hierarchy["state_id"]),
        "district_id": str(hierarchy["district_id"]),
    })
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_DUPLICATE_SLUG"


def test_create_validation_error(client, auth_token):
    resp = client.post(
        "/api/v1/masters/destinations",
        json={"name": "Munnar"},  # missing required fields
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 400


def test_invalid_hierarchy_wrong_state(client, auth_token, hierarchy, app):
    """State doesn't belong to country → ERR_HIERARCHY_MISMATCH."""
    with app.app_context():
        other = Country(name="USA", code="US", phone_code="+1", is_active=True)
        db.session.add(other)
        db.session.commit()
        other_id = str(other.id)

    resp = _create_destination(client, auth_token, hierarchy, {
        "name": "Test", "code": "TST", "slug": "test",
        "country_id":  other_id,  # wrong country
        "state_id":    str(hierarchy["state_id"]),
        "district_id": str(hierarchy["district_id"]),
    })
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_HIERARCHY_MISMATCH"


def test_invalid_hierarchy_wrong_district(client, auth_token, hierarchy, app):
    """District doesn't belong to state → ERR_HIERARCHY_MISMATCH."""
    with app.app_context():
        country2 = Country(name="Sri Lanka", code="LK", phone_code="+94", is_active=True)
        db.session.add(country2)
        db.session.flush()
        state2 = State(name="Western Province", code="WP", country_id=country2.id, is_active=True)
        db.session.add(state2)
        db.session.flush()
        district2 = District(name="Colombo", code="CMB", state_id=state2.id, is_active=True)
        db.session.add(district2)
        db.session.commit()
        d2_id = str(district2.id)

    resp = _create_destination(client, auth_token, hierarchy, {
        "name": "Test", "code": "TST", "slug": "test",
        "country_id":  str(hierarchy["country_id"]),
        "state_id":    str(hierarchy["state_id"]),
        "district_id": d2_id,  # district from a different state
    })
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_HIERARCHY_MISMATCH"


def test_invalid_country(client, auth_token, hierarchy):
    """Non-existent country_id → ERR_INVALID_COUNTRY."""
    resp = _create_destination(client, auth_token, hierarchy, {
        "name": "Test", "code": "TST", "slug": "test",
        "country_id":  str(uuid.uuid4()),
        "state_id":    str(hierarchy["state_id"]),
        "district_id": str(hierarchy["district_id"]),
    })
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_INVALID_COUNTRY"


# ─────────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────────

def test_get_by_id(client, auth_token, hierarchy):
    create_resp = _create_destination(client, auth_token, hierarchy)
    dest_id = create_resp.get_json()["data"]["id"]

    resp = client.get(f"/api/v1/masters/destinations/{dest_id}", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == dest_id
    assert "audit_info" in data
    assert "country_id" in data
    assert "state_id" in data
    assert "district_id" in data


def test_get_not_found(client, auth_token):
    resp = client.get(f"/api/v1/masters/destinations/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert resp.status_code == 404


def test_get_invalid_uuid(client, auth_token):
    resp = client.get("/api/v1/masters/destinations/not-a-uuid", headers=auth_headers(auth_token))
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────
# LIST
# ─────────────────────────────────────────────────────────────────

def test_list_pagination(client, auth_token, hierarchy):
    _create_destination(client, auth_token, hierarchy, {
        "name": "Munnar",   "code": "MUN", "slug": "munnar",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })
    _create_destination(client, auth_token, hierarchy, {
        "name": "Thekkady", "code": "THK", "slug": "thekkady",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })
    _create_destination(client, auth_token, hierarchy, {
        "name": "Vagamon",  "code": "VGM", "slug": "vagamon",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })

    resp = client.get("/api/v1/masters/destinations?page=1&page_size=2", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data["items"]) == 2
    assert data["pagination"]["total_records"] == 3
    assert data["pagination"]["total_pages"] == 2


def test_list_search(client, auth_token, hierarchy):
    _create_destination(client, auth_token, hierarchy, {
        "name": "Munnar", "code": "MUN", "slug": "munnar",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })
    _create_destination(client, auth_token, hierarchy, {
        "name": "Thekkady", "code": "THK", "slug": "thekkady",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })

    resp = client.get("/api/v1/masters/destinations?search=Thekk", headers=auth_headers(auth_token))
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 1
    assert data["items"][0]["code"] == "THK"


def test_list_filter_is_active(client, auth_token, hierarchy):
    create_resp = _create_destination(client, auth_token, hierarchy)
    dest_id = create_resp.get_json()["data"]["id"]
    client.delete(f"/api/v1/masters/destinations/{dest_id}", headers=auth_headers(auth_token))

    resp = client.get("/api/v1/masters/destinations?is_active=true", headers=auth_headers(auth_token))
    assert resp.get_json()["data"]["pagination"]["total_records"] == 0


def test_list_sort(client, auth_token, hierarchy):
    _create_destination(client, auth_token, hierarchy, {
        "name": "Vagamon",  "code": "VGM", "slug": "vagamon",  "display_order": 2,
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })
    _create_destination(client, auth_token, hierarchy, {
        "name": "Munnar",   "code": "MUN", "slug": "munnar",   "display_order": 1,
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })

    resp = client.get("/api/v1/masters/destinations?sort_by=display_order&sort_order=asc", headers=auth_headers(auth_token))
    items = resp.get_json()["data"]["items"]
    assert items[0]["code"] == "MUN"
    assert items[1]["code"] == "VGM"


def test_list_empty(client, auth_token):
    resp = client.get("/api/v1/masters/destinations", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["items"] == []
    assert data["pagination"]["total_records"] == 0


def test_list_filter_by_district(client, auth_token, hierarchy, app):
    """Filter destinations by district_id."""
    with app.app_context():
        # Second district in same state
        d2 = District(name="Alappuzha", code="ALP", state_id=hierarchy["state_id"], is_active=True)
        db.session.add(d2)
        db.session.commit()
        alp_id = str(d2.id)

    _create_destination(client, auth_token, hierarchy, {
        "name": "Munnar",   "code": "MUN", "slug": "munnar",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })
    _create_destination(client, auth_token, hierarchy, {
        "name": "Alleppey", "code": "ALP-D", "slug": "alleppey",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": alp_id,
    })

    resp = client.get(f"/api/v1/masters/destinations?district_id={alp_id}", headers=auth_headers(auth_token))
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 1
    assert data["items"][0]["code"] == "ALP-D"


# ─────────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────────

def test_update_success(client, auth_token, hierarchy):
    create_resp = _create_destination(client, auth_token, hierarchy)
    dest_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/destinations/{dest_id}",
        json={"name": "Munnar Updated", "version": 1},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["name"] == "Munnar Updated"
    assert resp.get_json()["data"]["version"] == 2


def test_update_version_conflict(client, auth_token, hierarchy):
    create_resp = _create_destination(client, auth_token, hierarchy)
    dest_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/destinations/{dest_id}",
        json={"name": "Conflict", "version": 99},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_CONCURRENT_MODIFICATION"


def test_update_not_found(client, auth_token):
    resp = client.put(
        f"/api/v1/masters/destinations/{uuid.uuid4()}",
        json={"name": "Ghost", "version": 1},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────────────────────────

def test_delete_soft(client, auth_token, hierarchy, app):
    create_resp = _create_destination(client, auth_token, hierarchy)
    dest_id = create_resp.get_json()["data"]["id"]

    resp = client.delete(f"/api/v1/masters/destinations/{dest_id}", headers=auth_headers(auth_token))
    assert resp.status_code == 200

    with app.app_context():
        from app.modules.master.destination.repository import DestinationRepository
        repo = DestinationRepository()
        dest = repo.get(uuid.UUID(dest_id))
        assert dest is not None
        assert dest.is_active is False


def test_delete_not_found(client, auth_token):
    resp = client.delete(f"/api/v1/masters/destinations/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────
# LOOKUP
# ─────────────────────────────────────────────────────────────────

def test_lookup_endpoint(client, auth_token, hierarchy):
    _create_destination(client, auth_token, hierarchy, {
        "name": "Munnar",   "code": "MUN", "slug": "munnar",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })
    _create_destination(client, auth_token, hierarchy, {
        "name": "Thekkady", "code": "THK", "slug": "thekkady",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })

    resp = client.get("/api/v1/masters/destinations/lookup", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    items = resp.get_json()["data"]
    assert len(items) == 2
    assert all("id" in d and "name" in d and "code" in d and "slug" in d for d in items)
    # Lookup must NOT expose version or audit fields
    assert "version" not in items[0]
    assert "is_active" not in items[0]


def test_lookup_filtered_by_district(client, auth_token, hierarchy, app):
    with app.app_context():
        d2 = District(name="Ernakulam", code="EKM", state_id=hierarchy["state_id"], is_active=True)
        db.session.add(d2)
        db.session.commit()
        ekm_id = str(d2.id)

    _create_destination(client, auth_token, hierarchy, {
        "name": "Munnar",   "code": "MUN", "slug": "munnar",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": str(hierarchy["district_id"]),
    })
    _create_destination(client, auth_token, hierarchy, {
        "name": "Kochi", "code": "KOCHI", "slug": "kochi",
        "country_id": str(hierarchy["country_id"]), "state_id": str(hierarchy["state_id"]), "district_id": ekm_id,
    })

    resp = client.get(f"/api/v1/masters/destinations/lookup?district_id={ekm_id}", headers=auth_headers(auth_token))
    items = resp.get_json()["data"]
    assert len(items) == 1
    assert items[0]["code"] == "KOCHI"


# ─────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────

def test_unauthorized(client):
    resp = client.get("/api/v1/masters/destinations")
    assert resp.status_code == 401


def test_forbidden(client, no_perm_token):
    resp = client.get("/api/v1/masters/destinations", headers=auth_headers(no_perm_token))
    assert resp.status_code == 403
