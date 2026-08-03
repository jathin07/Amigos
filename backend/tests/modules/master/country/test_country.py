import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role, RefreshToken
from app.core.extensions import bcrypt
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
    """Create a user with country permissions and return a valid JWT."""
    with app.app_context():
        role = Role(
            name="Master Admin",
            code="MASTER_ADMIN",
            is_system=True,
        )
        # Attach all master.country permissions via a custom attribute
        # (using the existing permission_required decorator which reads role/permissions)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Country",
            display_name="Country Admin",
            official_email="country@test.com",
            phone="9999999999",
            employee_code="CTEST01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="country@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "master.country.read",
                "master.country.create",
                "master.country.update",
                "master.country.delete",
            ]},
        )
        return token


@pytest.fixture
def no_perm_token(app):
    """JWT with no permissions — for forbidden test."""
    with app.app_context():
        token = create_access_token(
            identity=str(uuid.uuid4()),
            additional_claims={"permissions": []},
        )
        return token


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _create_country(client, token, payload=None):
    payload = payload or {
        "name": "India",
        "code": "IN",
        "phone_code": "+91",
        "description": "Republic of India",
        "display_order": 1,
    }
    return client.post(
        "/api/v1/masters/countries",
        json=payload,
        headers=auth_headers(token),
    )


# ─────────────────────────────────────────────────────────────────
# 1. test_create_success
# ─────────────────────────────────────────────────────────────────
def test_create_success(client, auth_token):
    resp = _create_country(client, auth_token)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["code"] == "IN"
    assert data["data"]["phone_code"] == "+91"
    assert "Location" in resp.headers
    assert "/api/v1/masters/countries/" in resp.headers["Location"]


# ─────────────────────────────────────────────────────────────────
# 2. test_duplicate_code
# ─────────────────────────────────────────────────────────────────
def test_duplicate_code(client, auth_token):
    _create_country(client, auth_token)
    resp = _create_country(client, auth_token)
    assert resp.status_code == 409
    data = resp.get_json()
    assert data["success"] is False
    assert data["errors"][0]["code"] == "ERR_DUPLICATE_CODE"


# ─────────────────────────────────────────────────────────────────
# 3. test_create_validation_error — missing required fields
# ─────────────────────────────────────────────────────────────────
def test_create_validation_error(client, auth_token):
    resp = client.post(
        "/api/v1/masters/countries",
        json={"description": "No name or code"},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert data["errors"] is not None


# ─────────────────────────────────────────────────────────────────
# 4. test_create_invalid_phone_code
# ─────────────────────────────────────────────────────────────────
def test_create_invalid_phone_code(client, auth_token):
    resp = _create_country(client, auth_token, {
        "name": "India", "code": "IN", "phone_code": "91"  # missing +
    })
    assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────
# 5. test_get_by_id
# ─────────────────────────────────────────────────────────────────
def test_get_by_id(client, auth_token):
    create_resp = _create_country(client, auth_token)
    country_id = create_resp.get_json()["data"]["id"]

    resp = client.get(f"/api/v1/masters/countries/{country_id}", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["id"] == country_id
    assert "audit_info" in data["data"]
    assert data["data"]["version"] == 1


# ─────────────────────────────────────────────────────────────────
# 6. test_get_not_found
# ─────────────────────────────────────────────────────────────────
def test_get_not_found(client, auth_token):
    resp = client.get(
        f"/api/v1/masters/countries/{uuid.uuid4()}",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 404
    assert resp.get_json()["success"] is False


# ─────────────────────────────────────────────────────────────────
# 7. test_get_invalid_uuid
# ─────────────────────────────────────────────────────────────────
def test_get_invalid_uuid(client, auth_token):
    resp = client.get(
        "/api/v1/masters/countries/not-a-real-uuid",
        headers=auth_headers(auth_token),
    )
    # SQLAlchemy will return None for a bad UUID, so the service raises NotFoundException
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────
# 8. test_list_pagination
# ─────────────────────────────────────────────────────────────────
def test_list_pagination(client, auth_token):
    countries = [
        {"name": "India",     "code": "IN",  "phone_code": "+91"},
        {"name": "USA",       "code": "US",  "phone_code": "+1"},
        {"name": "UK",        "code": "GB",  "phone_code": "+44"},
        {"name": "Singapore", "code": "SG",  "phone_code": "+65"},
        {"name": "UAE",       "code": "AE",  "phone_code": "+971"},
    ]
    for c in countries:
        _create_country(client, auth_token, c)

    resp = client.get(
        "/api/v1/masters/countries?page=1&page_size=2",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 5
    assert data["pagination"]["total_pages"] == 3
    assert len(data["items"]) == 2


# ─────────────────────────────────────────────────────────────────
# 9. test_list_search
# ─────────────────────────────────────────────────────────────────
def test_list_search(client, auth_token):
    _create_country(client, auth_token, {"name": "India",  "code": "IN", "phone_code": "+91"})
    _create_country(client, auth_token, {"name": "Indonesia", "code": "ID", "phone_code": "+62"})
    _create_country(client, auth_token, {"name": "USA",    "code": "US", "phone_code": "+1"})

    resp = client.get(
        "/api/v1/masters/countries?search=ind",
        headers=auth_headers(auth_token),
    )
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 2


# ─────────────────────────────────────────────────────────────────
# 10. test_list_filter_is_active
# ─────────────────────────────────────────────────────────────────
def test_list_filter_is_active(client, auth_token):
    create_resp = _create_country(client, auth_token, {"name": "India", "code": "IN", "phone_code": "+91"})
    _create_country(client, auth_token, {"name": "USA", "code": "US", "phone_code": "+1", "is_active": False})

    resp = client.get(
        "/api/v1/masters/countries?is_active=true",
        headers=auth_headers(auth_token),
    )
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 1
    assert data["items"][0]["code"] == "IN"


# ─────────────────────────────────────────────────────────────────
# 11. test_list_sort
# ─────────────────────────────────────────────────────────────────
def test_list_sort(client, auth_token):
    _create_country(client, auth_token, {"name": "Zulu", "code": "ZZ", "phone_code": "+999"})
    _create_country(client, auth_token, {"name": "Alpha", "code": "AA", "phone_code": "+1"})

    resp = client.get(
        "/api/v1/masters/countries?sort_by=name&sort_order=asc",
        headers=auth_headers(auth_token),
    )
    items = resp.get_json()["data"]["items"]
    assert items[0]["name"] == "Alpha"
    assert items[1]["name"] == "Zulu"


# ─────────────────────────────────────────────────────────────────
# 12. test_list_empty
# ─────────────────────────────────────────────────────────────────
def test_list_empty(client, auth_token):
    resp = client.get("/api/v1/masters/countries", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["pagination"]["total_records"] == 0
    assert data["items"] == []


# ─────────────────────────────────────────────────────────────────
# 13. test_update_success
# ─────────────────────────────────────────────────────────────────
def test_update_success(client, auth_token):
    create_resp = _create_country(client, auth_token)
    country_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/countries/{country_id}",
        json={"name": "India (Updated)", "version": 1},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["name"] == "India (Updated)"
    assert data["version"] == 2


# ─────────────────────────────────────────────────────────────────
# 14. test_update_version_conflict
# ─────────────────────────────────────────────────────────────────
def test_update_version_conflict(client, auth_token):
    create_resp = _create_country(client, auth_token)
    country_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/countries/{country_id}",
        json={"name": "Conflict", "version": 99},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 409
    assert resp.get_json()["errors"][0]["code"] == "ERR_CONCURRENT_MODIFICATION"


# ─────────────────────────────────────────────────────────────────
# 15. test_update_not_found
# ─────────────────────────────────────────────────────────────────
def test_update_not_found(client, auth_token):
    resp = client.put(
        f"/api/v1/masters/countries/{uuid.uuid4()}",
        json={"name": "Ghost", "version": 1},
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────
# 16. test_delete_soft
# ─────────────────────────────────────────────────────────────────
def test_delete_soft(client, auth_token, app):
    create_resp = _create_country(client, auth_token)
    country_id = create_resp.get_json()["data"]["id"]

    resp = client.delete(
        f"/api/v1/masters/countries/{country_id}",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 200

    # Verify record still exists but is inactive
    with app.app_context():
        import uuid
        from app.modules.master.country.repository import CountryRepository
        repo = CountryRepository()
        country = repo.get_by_id(uuid.UUID(country_id))
        assert country is not None
        assert country.is_active is False


# ─────────────────────────────────────────────────────────────────
# 17. test_delete_not_found
# ─────────────────────────────────────────────────────────────────
def test_delete_not_found(client, auth_token):
    resp = client.delete(
        f"/api/v1/masters/countries/{uuid.uuid4()}",
        headers=auth_headers(auth_token),
    )
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────
# 18. test_lookup_endpoint
# ─────────────────────────────────────────────────────────────────
def test_lookup_endpoint(client, auth_token):
    _create_country(client, auth_token, {"name": "India", "code": "IN", "phone_code": "+91"})
    _create_country(client, auth_token, {"name": "USA",   "code": "US", "phone_code": "+1", "is_active": False})

    resp = client.get("/api/v1/masters/countries/lookup", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    items = resp.get_json()["data"]["items"]
    # Only active country returned
    assert len(items) == 1
    assert set(items[0].keys()) == {"id", "name", "code"}


# ─────────────────────────────────────────────────────────────────
# 19. test_unauthorized
# ─────────────────────────────────────────────────────────────────
def test_unauthorized(client):
    resp = client.get("/api/v1/masters/countries")
    assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────────
# 20. test_forbidden
# ─────────────────────────────────────────────────────────────────
def test_forbidden(client, no_perm_token):
    resp = client.get("/api/v1/masters/countries", headers=auth_headers(no_perm_token))
    assert resp.status_code == 403
