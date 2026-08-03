import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role, Package
from app.core.extensions import bcrypt


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
    """Create a user with full package permissions and return a valid JWT."""
    with app.app_context():
        role = Role(name="Package Admin", code="PKG_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Package",
            display_name="Package Admin",
            official_email="pkg_admin@test.com",
            phone="9999999991",
            employee_code="TM_PKG01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="pkg_admin@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "package.read",
                "package.create",
                "package.update",
                "package.delete",
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


import uuid as _uuid_mod
from sqlalchemy import text


@pytest.fixture
def destination(app):
    """Insert a row into the original 'destinations' table via raw SQL.

    The Destination name in app.models is overwritten by the master module's
    Destination (destinations_master table). PackageDestination.destination_id
    FK references 'destinations.id', so we insert directly.
    """
    with app.app_context():
        dest_id = _uuid_mod.uuid4()
        db.session.execute(
            text(
                "INSERT INTO destinations "
                "(id, name, state, country, is_active, is_deleted, created_at, updated_at) "
                "VALUES (:id, :name, :state, :country, :is_active, :is_deleted, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "id": str(dest_id),
                "name": "Munnar",
                "state": "Kerala",
                "country": "India",
                "is_active": True,
                "is_deleted": False,
            },
        )
        db.session.commit()
        return str(dest_id)


@pytest.fixture
def destination2(app):
    with app.app_context():
        dest_id = _uuid_mod.uuid4()
        db.session.execute(
            text(
                "INSERT INTO destinations "
                "(id, name, state, country, is_active, is_deleted, created_at, updated_at) "
                "VALUES (:id, :name, :state, :country, :is_active, :is_deleted, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "id": str(dest_id),
                "name": "Alleppey",
                "state": "Kerala",
                "country": "India",
                "is_active": True,
                "is_deleted": False,
            },
        )
        db.session.commit()
        return str(dest_id)


@pytest.fixture
def inactive_destination(app):
    with app.app_context():
        dest_id = _uuid_mod.uuid4()
        db.session.execute(
            text(
                "INSERT INTO destinations "
                "(id, name, state, country, is_active, is_deleted, created_at, updated_at) "
                "VALUES (:id, :name, :state, :country, :is_active, :is_deleted, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "id": str(dest_id),
                "name": "Inactive Place",
                "state": "Kerala",
                "country": "India",
                "is_active": False,
                "is_deleted": False,
            },
        )
        db.session.commit()
        return str(dest_id)


def _headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _base_payload(destination_id=None):
    payload = {
        "title": "Kerala Delight",
        "description": "5 Days tour of Kerala",
        "duration_days": 5,
        "duration_nights": 4,
        "starting_price": "15000.00",
        "starting_city": "Kochi",
        "is_featured": False,
        "is_active": True,
    }
    if destination_id:
        payload["destinations"] = [
            {
                "destination_id": destination_id,
                "day_order": 1,
                "sequence": 1,
                "overnight_stay": True,
                "default_duration": "1 Day",
            }
        ]
    return payload


# ─────────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────────

def test_create_package_success(client, auth_token):
    """Should create a basic package and return 201 with id."""
    resp = client.post("/api/v1/packages", json=_base_payload(), headers=_headers(auth_token))
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["data"]["title"] == "Kerala Delight"
    assert data["data"]["version"] == 1
    assert "id" in data["data"]


def test_create_package_with_nested_collections(client, auth_token, destination):
    """Should persist highlights, inclusions, exclusions and destinations."""
    payload = _base_payload(destination_id=destination)
    payload["highlights"] = [
        {"highlight_text": "Munnar hills sightseeing", "display_order": 1},
        {"highlight_text": "Alleppey houseboat", "display_order": 2},
    ]
    payload["inclusions"] = [
        {"inclusion_text": "4 Nights hotel", "display_order": 1},
    ]
    payload["exclusions"] = [
        {"exclusion_text": "Lunch & dinner", "display_order": 1},
    ]

    resp = client.post("/api/v1/packages", json=payload, headers=_headers(auth_token))
    assert resp.status_code == 201
    data = resp.get_json()["data"]

    assert len(data["highlights"]) == 2
    assert data["highlights"][0]["highlight_text"] == "Munnar hills sightseeing"
    assert data["highlights"][0]["display_order"] == 1

    assert len(data["inclusions"]) == 1
    assert data["inclusions"][0]["inclusion_text"] == "4 Nights hotel"
    # display_order always null for inclusions (no DB column)
    assert data["inclusions"][0]["display_order"] is None

    assert len(data["exclusions"]) == 1
    assert data["exclusions"][0]["display_order"] is None

    assert len(data["destinations"]) == 1
    assert data["destinations"][0]["overnight_stay"] is True


def test_create_package_duplicate_title_conflict(client, auth_token):
    """Second package with same title (case-insensitive) should return 409."""
    client.post("/api/v1/packages", json=_base_payload(), headers=_headers(auth_token))

    payload2 = _base_payload()
    payload2["title"] = "  KERALA DELIGHT  "
    resp = client.post("/api/v1/packages", json=payload2, headers=_headers(auth_token))
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "ERR_PACKAGE_DUPLICATE_TITLE"


def test_create_package_invalid_destination(client, auth_token, inactive_destination):
    """Referencing an inactive destination should return 400 ERR_INVALID_DESTINATION."""
    payload = _base_payload()
    payload["destinations"] = [
        {"destination_id": inactive_destination, "day_order": 1, "sequence": 1}
    ]
    resp = client.post("/api/v1/packages", json=payload, headers=_headers(auth_token))
    assert resp.status_code == 400
    assert resp.get_json()["code"] == "ERR_INVALID_DESTINATION"


def test_create_package_unknown_destination(client, auth_token):
    """Referencing a non-existent destination UUID should return 400."""
    payload = _base_payload()
    payload["destinations"] = [
        {"destination_id": str(uuid.uuid4()), "day_order": 1, "sequence": 1}
    ]
    resp = client.post("/api/v1/packages", json=payload, headers=_headers(auth_token))
    assert resp.status_code == 400
    assert resp.get_json()["code"] == "ERR_INVALID_DESTINATION"


def test_create_package_missing_required_fields(client, auth_token):
    """Missing duration_days / duration_nights should fail validation."""
    resp = client.post("/api/v1/packages", json={"title": "Test"}, headers=_headers(auth_token))
    assert resp.status_code == 400
    assert resp.get_json()["code"] == "ERR_VALIDATION"


# ─────────────────────────────────────────────────────────────────
# Read
# ─────────────────────────────────────────────────────────────────

def test_get_package_detail(client, auth_token, destination):
    """GET /api/v1/packages/{id} should return full detail with audit_info."""
    create_resp = client.post(
        "/api/v1/packages", json=_base_payload(destination_id=destination), headers=_headers(auth_token)
    )
    pkg_id = create_resp.get_json()["data"]["id"]

    resp = client.get(f"/api/v1/packages/{pkg_id}", headers=_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == pkg_id
    assert "audit_info" in data
    assert "version" in data
    assert len(data["destinations"]) == 1


def test_get_package_not_found(client, auth_token):
    """Non-existent package ID should return 404 ERR_PACKAGE_NOT_FOUND."""
    resp = client.get(f"/api/v1/packages/{uuid.uuid4()}", headers=_headers(auth_token))
    assert resp.status_code == 404
    assert resp.get_json()["code"] == "ERR_PACKAGE_NOT_FOUND"


def test_list_packages_pagination(client, auth_token):
    """List endpoint should return pagination envelope."""
    client.post("/api/v1/packages", json=_base_payload(), headers=_headers(auth_token))
    resp = client.get("/api/v1/packages?page=1&page_size=10", headers=_headers(auth_token))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "items" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1


def test_list_packages_filter_is_active(client, auth_token):
    """Filter is_active=false should return only inactive packages."""
    client.post("/api/v1/packages", json=_base_payload(), headers=_headers(auth_token))
    resp = client.get("/api/v1/packages?is_active=false", headers=_headers(auth_token))
    assert resp.status_code == 200
    items = resp.get_json()["data"]["items"]
    for item in items:
        assert item["is_active"] is False


# ─────────────────────────────────────────────────────────────────
# Update
# ─────────────────────────────────────────────────────────────────

def test_update_package_scalar_only(client, auth_token):
    """Updating only a scalar field should increment version and leave collections unchanged."""
    create_resp = client.post(
        "/api/v1/packages",
        json={**_base_payload(), "highlights": [{"highlight_text": "Original highlight", "display_order": 1}]},
        headers=_headers(auth_token),
    )
    pkg = create_resp.get_json()["data"]
    pkg_id = pkg["id"]
    version = pkg["version"]

    resp = client.put(
        f"/api/v1/packages/{pkg_id}",
        json={"starting_price": "16500.00", "version": version},
        headers=_headers(auth_token),
    )
    assert resp.status_code == 200
    updated = resp.get_json()["data"]
    assert updated["version"] == version + 1
    # highlights not in request body → should remain unchanged
    assert len(updated["highlights"]) == 1
    assert updated["highlights"][0]["highlight_text"] == "Original highlight"


def test_update_package_with_nested_replacement(client, auth_token, destination, destination2):
    """Supplying a highlights list should fully replace the collection."""
    payload = _base_payload()
    payload["highlights"] = [{"highlight_text": "Old highlight", "display_order": 1}]
    create_resp = client.post("/api/v1/packages", json=payload, headers=_headers(auth_token))
    pkg = create_resp.get_json()["data"]
    pkg_id = pkg["id"]

    resp = client.put(
        f"/api/v1/packages/{pkg_id}",
        json={
            "highlights": [
                {"highlight_text": "New highlight A", "display_order": 1},
                {"highlight_text": "New highlight B", "display_order": 2},
            ],
            "version": pkg["version"],
        },
        headers=_headers(auth_token),
    )
    assert resp.status_code == 200
    updated = resp.get_json()["data"]
    assert len(updated["highlights"]) == 2
    assert updated["highlights"][0]["highlight_text"] == "New highlight A"


def test_update_package_omitted_collection_unchanged(client, auth_token):
    """Omitting 'inclusions' from the update body leaves existing inclusions intact."""
    payload = _base_payload()
    payload["inclusions"] = [{"inclusion_text": "Breakfast included"}]
    create_resp = client.post("/api/v1/packages", json=payload, headers=_headers(auth_token))
    pkg = create_resp.get_json()["data"]
    pkg_id = pkg["id"]

    # Update only title — inclusions key is absent
    resp = client.put(
        f"/api/v1/packages/{pkg_id}",
        json={"title": "Kerala Delight Updated", "version": pkg["version"]},
        headers=_headers(auth_token),
    )
    assert resp.status_code == 200
    updated = resp.get_json()["data"]
    assert len(updated["inclusions"]) == 1
    assert updated["inclusions"][0]["inclusion_text"] == "Breakfast included"


def test_update_package_empty_array_clears_collection(client, auth_token):
    """Supplying exclusions=[] should remove all existing exclusions."""
    payload = _base_payload()
    payload["exclusions"] = [{"exclusion_text": "Dinner not included"}]
    create_resp = client.post("/api/v1/packages", json=payload, headers=_headers(auth_token))
    pkg = create_resp.get_json()["data"]
    pkg_id = pkg["id"]

    resp = client.put(
        f"/api/v1/packages/{pkg_id}",
        json={"exclusions": [], "version": pkg["version"]},
        headers=_headers(auth_token),
    )
    assert resp.status_code == 200
    updated = resp.get_json()["data"]
    assert len(updated["exclusions"]) == 0


def test_update_package_wrong_version(client, auth_token):
    """Wrong version on update should return 409 ERR_OPTIMISTIC_LOCK."""
    create_resp = client.post("/api/v1/packages", json=_base_payload(), headers=_headers(auth_token))
    pkg_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/packages/{pkg_id}",
        json={"title": "Conflict", "version": 999},
        headers=_headers(auth_token),
    )
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "ERR_OPTIMISTIC_LOCK"


def test_update_package_duplicate_title(client, auth_token):
    """Renaming a package to an existing active title should return 409."""
    client.post("/api/v1/packages", json=_base_payload(), headers=_headers(auth_token))

    payload2 = _base_payload()
    payload2["title"] = "Goa Getaway"
    create_resp2 = client.post("/api/v1/packages", json=payload2, headers=_headers(auth_token))
    pkg2 = create_resp2.get_json()["data"]

    resp = client.put(
        f"/api/v1/packages/{pkg2['id']}",
        json={"title": "Kerala Delight", "version": pkg2["version"]},
        headers=_headers(auth_token),
    )
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "ERR_PACKAGE_DUPLICATE_TITLE"


# ─────────────────────────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────────────────────────

def test_delete_package_soft_delete(client, auth_token):
    """DELETE should soft-delete: is_active=False, not physically removed."""
    create_resp = client.post("/api/v1/packages", json=_base_payload(), headers=_headers(auth_token))
    pkg_id = create_resp.get_json()["data"]["id"]

    resp = client.delete(f"/api/v1/packages/{pkg_id}", headers=_headers(auth_token))
    assert resp.status_code == 200

    # Package should not be reachable via GET (is_deleted=True)
    get_resp = client.get(f"/api/v1/packages/{pkg_id}", headers=_headers(auth_token))
    assert get_resp.status_code == 404


def test_delete_package_not_found(client, auth_token):
    """Deleting a non-existent package should return 404."""
    resp = client.delete(f"/api/v1/packages/{uuid.uuid4()}", headers=_headers(auth_token))
    assert resp.status_code == 404
    assert resp.get_json()["code"] == "ERR_PACKAGE_NOT_FOUND"


# ─────────────────────────────────────────────────────────────────
# Permissions
# ─────────────────────────────────────────────────────────────────

def test_package_read_requires_permission(client, no_perm_token):
    """GET /api/v1/packages without package.read permission should return 403."""
    resp = client.get("/api/v1/packages", headers=_headers(no_perm_token))
    assert resp.status_code == 403


def test_package_create_requires_permission(client, no_perm_token):
    """POST /api/v1/packages without package.create permission should return 403."""
    resp = client.post("/api/v1/packages", json=_base_payload(), headers=_headers(no_perm_token))
    assert resp.status_code == 403


def test_package_update_requires_permission(client, no_perm_token):
    """PUT /api/v1/packages/{id} without package.update permission should return 403."""
    resp = client.put(
        f"/api/v1/packages/{uuid.uuid4()}",
        json={"title": "Test", "version": 1},
        headers=_headers(no_perm_token),
    )
    assert resp.status_code == 403


def test_package_delete_requires_permission(client, no_perm_token):
    """DELETE /api/v1/packages/{id} without package.delete permission should return 403."""
    resp = client.delete(f"/api/v1/packages/{uuid.uuid4()}", headers=_headers(no_perm_token))
    assert resp.status_code == 403
