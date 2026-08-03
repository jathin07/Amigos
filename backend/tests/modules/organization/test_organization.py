import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role, OrganizationType, Organization, OrganizationDivision, ContactPerson
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
    """Create a user with organization permissions and return a valid JWT."""
    with app.app_context():
        role = Role(name="Org Admin", code="ORG_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Org",
            display_name="Org Admin",
            official_email="org@test.com",
            phone="9999999995",
            employee_code="ORG01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="org@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "organization.read",
                "organization.update",
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
def org_type(app):
    with app.app_context():
        ot = OrganizationType(code="COLLEGE", name="College/University", is_active=True)
        db.session.add(ot)
        db.session.commit()
        return ot.id


# ─────────────────────────────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────────────────────────────

def test_get_organization_not_found(client, auth_token):
    """Should return 404 when organization has not been configured yet."""
    resp = client.get(
        "/api/v1/organization",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["code"] == "ERR_NOT_FOUND"


def test_put_organization_validation_error(client, auth_token):
    """Should validate required fields on initial creation."""
    # missing organization_name and organization_type_id
    resp = client.put(
        "/api/v1/organization",
        json={},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["code"] == "ERR_VALIDATION"


def test_create_and_get_organization(client, auth_token, org_type):
    """Should successfully create a single organization configuration and fetch it."""
    payload = {
        "organization_name": "ABC University",
        "organization_type_id": str(org_type),
        "address": "123 Main St",
        "city": "Bangalore",
        "state": "Karnataka",
        "phone": "0809876543",
        "email": "info@abc.edu",
        "website": "www.abc.edu",
        "notes": "Premium account",
        "divisions": [
            {
                "department": "Computer Science",
                "course": "B.Tech",
                "batch": "2026"
            }
        ],
        "contact_persons": [
            {
                "name": "Dr. Alice",
                "designation": "HOD",
                "phone": "+919876543231",
                "email": "alice@abc.edu",
                "is_primary": True
            }
        ]
    }

    # 1. Create via PUT
    resp = client.put(
        "/api/v1/organization",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Organization updated successfully."
    assert data["data"]["organization_name"] == "ABC University"
    assert data["data"]["city"] == "Bangalore"
    assert len(data["data"]["divisions"]) == 1
    assert data["data"]["divisions"][0]["department"] == "Computer Science"
    assert len(data["data"]["contact_persons"]) == 1
    assert data["data"]["contact_persons"][0]["name"] == "Dr. Alice"
    assert data["data"]["contact_persons"][0]["is_primary"] is True

    # Save IDs to check sync updates later
    div_id = data["data"]["divisions"][0]["id"]
    contact_id = data["data"]["contact_persons"][0]["id"]

    # 2. Retrieve via GET
    resp = client.get(
        "/api/v1/organization",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    get_data = resp.get_json()
    assert get_data["data"]["organization_name"] == "ABC University"
    assert get_data["data"]["audit_info"]["created_by"] is not None


def test_update_sync_organization(client, auth_token, org_type):
    """Should update fields and sync child lists (add, edit, remove)."""
    # 1. Initial create
    payload = {
        "organization_name": "Initial Org",
        "organization_type_id": str(org_type),
        "divisions": [
            {
                "department": "Physics",
                "course": "B.Sc"
            },
            {
                "department": "Chemistry",
                "course": "B.Sc"
            }
        ],
        "contact_persons": [
            {
                "name": "Bob",
                "phone": "12345"
            }
        ]
    }
    resp = client.put(
        "/api/v1/organization",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    
    physics_id = next(d["id"] for d in data["divisions"] if d["department"] == "Physics")
    bob_id = data["contact_persons"][0]["id"]

    # 2. Perform updates
    # We will:
    # - Update "Physics" department to "Physics & Astro"
    # - Delete "Chemistry" department (omit it from divisions list)
    # - Add "Mathematics" department
    # - Update "Bob" phone
    # - Add "Charlie" contact person
    update_payload = {
        "organization_name": "Updated Org Name",
        "divisions": [
            {
                "id": physics_id,
                "department": "Physics & Astro",
                "course": "B.Sc"
            },
            {
                "department": "Mathematics",
                "course": "M.Sc"
            }
        ],
        "contact_persons": [
            {
                "id": bob_id,
                "name": "Bob",
                "phone": "54321",
                "is_active": True
            },
            {
                "name": "Charlie",
                "phone": "67890",
                "is_primary": True
            }
        ]
    }

    resp = client.put(
        "/api/v1/organization",
        json=update_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    updated_data = resp.get_json()["data"]

    assert updated_data["organization_name"] == "Updated Org Name"
    
    # Verify divisions sync
    assert len(updated_data["divisions"]) == 2
    dept_names = [d["department"] for d in updated_data["divisions"]]
    assert "Physics & Astro" in dept_names
    assert "Mathematics" in dept_names
    assert "Chemistry" not in dept_names

    # Verify contact persons sync
    assert len(updated_data["contact_persons"]) == 2
    contacts = {c["name"]: c for c in updated_data["contact_persons"]}
    assert contacts["Bob"]["phone"] == "54321"
    assert contacts["Charlie"]["phone"] == "67890"


def test_organization_permissions(client, no_perm_token):
    """Should deny access to users without required permissions."""
    resp = client.get(
        "/api/v1/organization",
        headers={"Authorization": f"Bearer {no_perm_token}"}
    )
    assert resp.status_code == 403

    resp = client.put(
        "/api/v1/organization",
        json={"organization_name": "Blocked"},
        headers={"Authorization": f"Bearer {no_perm_token}"}
    )
    assert resp.status_code == 403
