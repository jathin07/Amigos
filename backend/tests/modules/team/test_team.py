import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role, Department
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
    """Create a user with team permissions and return a valid JWT."""
    with app.app_context():
        role = Role(name="Team Admin", code="TEAM_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Team",
            display_name="Team Admin",
            official_email="team_admin@test.com",
            phone="9999999994",
            employee_code="TM_ADM01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="team_admin@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "team.read",
                "team.create",
                "team.update",
                "team.delete",
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
def lookup_data(app):
    with app.app_context():
        dept = Department(code="SALES", name="Sales Department", is_active=True)
        role = Role(code="CONSULTANT", name="Travel Consultant", is_active=True)
        db.session.add(dept)
        db.session.add(role)
        db.session.commit()
        return {
            "department_id": str(dept.id),
            "role_id": str(role.id)
        }


# ─────────────────────────────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────────────────────────────

def test_create_and_get_team_member(client, auth_token, lookup_data):
    """Should successfully create and retrieve a team member."""
    payload = {
        "first_name": "Jane",
        "last_name": "Smith",
        "display_name": "Jane Smith",
        "employee_code": "TM002",
        "official_email": "jane.smith@amigos.com",
        "phone": "+1234567890",
        "designation": "Sales Advisor",
        "department_id": lookup_data["department_id"],
        "role_id": lookup_data["role_id"],
        "employment_status": "FULL_TIME",
        "joined_date": "2026-02-01",
        "is_active": True
    }

    # Create via POST
    resp = client.post(
        "/api/v1/team-members",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["data"]["first_name"] == "Jane"
    assert data["data"]["employee_code"] == "TM002"
    assert data["data"]["version"] == 1
    assert data["data"]["department_id"] == lookup_data["department_id"]

    member_id = data["data"]["id"]

    # Retrieve via GET /<id>
    resp = client.get(
        f"/api/v1/team-members/{member_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["display_name"] == "Jane Smith"


def test_duplicate_employee_code_and_email(client, auth_token, lookup_data):
    """Should return 409 Conflict when employee_code or official_email is duplicated."""
    payload1 = {
        "first_name": "Alice",
        "display_name": "Alice User",
        "employee_code": "TM100",
        "official_email": "alice@amigos.com",
        "phone": "123",
        "is_active": True
    }
    resp = client.post(
        "/api/v1/team-members",
        json=payload1,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 201

    # Duplicate employee_code
    payload2 = {
        "first_name": "Bob",
        "display_name": "Bob User",
        "employee_code": "TM100", # duplicate
        "official_email": "bob@amigos.com",
        "phone": "456",
        "is_active": True
    }
    resp = client.post(
        "/api/v1/team-members",
        json=payload2,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "ERR_DUPLICATE_EMPLOYEE_CODE"

    # Duplicate email
    payload3 = {
        "first_name": "Charlie",
        "display_name": "Charlie User",
        "employee_code": "TM200",
        "official_email": "alice@amigos.com", # duplicate
        "phone": "789",
        "is_active": True
    }
    resp = client.post(
        "/api/v1/team-members",
        json=payload3,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "ERR_DUPLICATE_EMAIL"


def test_update_optimistic_locking(client, auth_token):
    """Should enforce optimistic locking with version checks."""
    payload = {
        "first_name": "Bob",
        "display_name": "Bob User",
        "employee_code": "TM300",
        "official_email": "bob@amigos.com",
        "phone": "9999",
    }
    resp = client.post(
        "/api/v1/team-members",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    data = resp.get_json()["data"]
    member_id = data["id"]
    version = data["version"]

    # Update with wrong version
    resp = client.put(
        f"/api/v1/team-members/{member_id}",
        json={"designation": "Manager", "version": version + 5},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "ERR_OPTIMISTIC_LOCK"

    # Update with correct version
    resp = client.put(
        f"/api/v1/team-members/{member_id}",
        json={"designation": "Manager", "version": version},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    updated_data = resp.get_json()["data"]
    assert updated_data["designation"] == "Manager"
    assert updated_data["version"] == version + 1


def test_lookup_and_date_validations(client, auth_token):
    """Should validate relationship FKs, manager loop, and date range checks."""
    # 1. Invalid dates (left_date < joined_date)
    payload = {
        "first_name": "Dave",
        "display_name": "Dave",
        "employee_code": "TM400",
        "official_email": "dave@amigos.com",
        "phone": "123",
        "joined_date": "2026-05-10",
        "left_date": "2026-05-01" # left before joined
    }
    resp = client.post(
        "/api/v1/team-members",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 400

    # 2. Self reporting manager validation during update
    payload_valid = {
        "first_name": "Dave",
        "display_name": "Dave",
        "employee_code": "TM400",
        "official_email": "dave@amigos.com",
        "phone": "123",
    }
    resp = client.post(
        "/api/v1/team-members",
        json=payload_valid,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    member = resp.get_json()["data"]
    member_id = member["id"]

    resp = client.put(
        f"/api/v1/team-members/{member_id}",
        json={
            "reporting_manager_id": member_id, # self manager
            "version": member["version"]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 400
    assert resp.get_json()["code"] == "ERR_INVALID_MANAGER"


def test_soft_delete(client, auth_token):
    """Should soft-delete team member and omit from list query."""
    # 1. Create a member
    payload = {
        "first_name": "Eve",
        "display_name": "Eve",
        "employee_code": "TM500",
        "official_email": "eve@amigos.com",
        "phone": "123",
    }
    resp = client.post(
        "/api/v1/team-members",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    member_id = resp.get_json()["data"]["id"]

    # Verify present in list
    resp = client.get(
        "/api/v1/team-members?search=Eve",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert len(resp.get_json()["data"]["items"]) == 1

    # 2. Delete
    resp = client.delete(
        f"/api/v1/team-members/{member_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200

    # Verify not present in GET /<id>
    resp = client.get(
        f"/api/v1/team-members/{member_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 404

    # Verify not present in list
    resp = client.get(
        "/api/v1/team-members?search=Eve",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert len(resp.get_json()["data"]["items"]) == 0
