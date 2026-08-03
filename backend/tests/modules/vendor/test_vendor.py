import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role, Vendor, VendorType
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
    """Create a user with vendor permissions and return a valid JWT."""
    with app.app_context():
        role = Role(name="Vendor Admin", code="VENDOR_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Vendor",
            display_name="Vendor Admin",
            official_email="vendor_admin@test.com",
            phone="9999999995",
            employee_code="TM_VND01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="vendor_admin@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "vendor.read",
                "vendor.create",
                "vendor.update",
                "vendor.delete",
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
def vendor_type(app):
    with app.app_context():
        vt = VendorType(code="ACCOMMODATION", name="Accommodation Service", is_active=True)
        db.session.add(vt)
        db.session.commit()
        return str(vt.id)


# ─────────────────────────────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────────────────────────────

def test_create_and_get_vendor(client, auth_token, vendor_type):
    """Should successfully create and retrieve a vendor."""
    payload = {
        "vendor_name": "  Grand Hyatt Kochi  ",
        "vendor_type_id": vendor_type,
        "contact_person": "Jane Hyatt",
        "phone": " +919876543220 ",
        "email": "INFO@GRANDHYATT.COM",
        "address": "Mulavukad, Kochi",
        "city": "Kochi",
        "state": "Kerala",
        "service_area": "Accommodation",
        "internal_rating": 5,
        "gst_number": " 32aaaaa1111a1z1 ",
        "notes": "Premium lake resort",
        "is_active": True
    }

    # Create via POST
    resp = client.post(
        "/api/v1/vendors",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["data"]["vendor_name"] == "Grand Hyatt Kochi" # trimmed
    assert data["data"]["phone"] == "+919876543220" # trimmed
    assert data["data"]["email"] == "info@grandhyatt.com" # lowercase
    assert data["data"]["gst_number"] == "32AAAAA1111A1Z1" # trimmed & uppercase
    assert data["data"]["is_verified"] is False # system-managed default
    assert data["data"]["version"] == 1

    vendor_id = data["data"]["id"]

    # Retrieve via GET /<id>
    resp = client.get(
        f"/api/v1/vendors/{vendor_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["contact_person"] == "Jane Hyatt"


def test_invalid_vendor_type(client, auth_token):
    """Should return 400 when vendor_type_id does not reference an active VendorType."""
    payload = {
        "vendor_name": "Test Vendor",
        "vendor_type_id": str(uuid.uuid4()), # random UUID
        "phone": "+910000000000",
    }
    resp = client.post(
        "/api/v1/vendors",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 400
    assert resp.get_json()["code"] == "ERR_INVALID_VENDOR_TYPE"


def test_duplicate_gst_number(client, auth_token, vendor_type):
    """Should block creation of vendors with duplicate normalized GST numbers."""
    payload1 = {
        "vendor_name": "Vendor A",
        "vendor_type_id": vendor_type,
        "phone": "123",
        "gst_number": "32AAAAA1111A1Z1"
    }
    resp = client.post(
        "/api/v1/vendors",
        json=payload1,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 201

    # Duplicate GST (different spacing/casing)
    payload2 = {
        "vendor_name": "Vendor B",
        "vendor_type_id": vendor_type,
        "phone": "456",
        "gst_number": "  32aaaaa1111a1z1  "
    }
    resp = client.post(
        "/api/v1/vendors",
        json=payload2,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "ERR_VENDOR_DUPLICATE_GST"


def test_update_optimistic_locking(client, auth_token, vendor_type):
    """Should enforce version-based optimistic locking on update."""
    payload = {
        "vendor_name": "Locking Vendor",
        "vendor_type_id": vendor_type,
        "phone": "12345",
    }
    resp = client.post(
        "/api/v1/vendors",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    data = resp.get_json()["data"]
    vendor_id = data["id"]
    version = data["version"]

    # Wrong version
    resp = client.put(
        f"/api/v1/vendors/{vendor_id}",
        json={"phone": "99999", "version": version + 10},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 409
    assert resp.get_json()["code"] == "ERR_OPTIMISTIC_LOCK"

    # Correct version
    resp = client.put(
        f"/api/v1/vendors/{vendor_id}",
        json={"phone": "99999", "version": version},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    updated = resp.get_json()["data"]
    assert updated["phone"] == "99999"
    assert updated["version"] == version + 1


def test_verification_lifecycle(client, auth_token, vendor_type):
    """Should verify/unverify vendors via dedicated state transition endpoints."""
    payload = {
        "vendor_name": "Verifying Vendor",
        "vendor_type_id": vendor_type,
        "phone": "12345",
    }
    resp = client.post(
        "/api/v1/vendors",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    vendor_id = resp.get_json()["data"]["id"]

    # 1. verify
    resp = client.post(
        f"/api/v1/vendors/{vendor_id}/verify",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["is_verified"] is True
    assert data["verified_at"] is not None

    # 2. unverify
    resp = client.post(
        f"/api/v1/vendors/{vendor_id}/unverify",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["is_verified"] is False
    assert data["verified_at"] is None


def test_soft_delete(client, auth_token, vendor_type):
    """Should soft-delete and omit vendor from list query."""
    payload = {
        "vendor_name": "Deletable Vendor",
        "vendor_type_id": vendor_type,
        "phone": "12345",
    }
    resp = client.post(
        "/api/v1/vendors",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    vendor_id = resp.get_json()["data"]["id"]

    # Delete
    resp = client.delete(
        f"/api/v1/vendors/{vendor_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200

    # Retrieve GET should return 404
    resp = client.get(
        f"/api/v1/vendors/{vendor_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 404

    # List should be empty
    resp = client.get(
        "/api/v1/vendors?search=Deletable",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert len(resp.get_json()["data"]["items"]) == 0


def test_rbac_permission_gating(client, no_perm_token, auth_token, vendor_type):
    """Should restrict access without required roles/permissions."""
    payload = {
        "vendor_name": "RBAC Vendor",
        "vendor_type_id": vendor_type,
        "phone": "12345",
    }
    resp = client.post(
        "/api/v1/vendors",
        json=payload,
        headers={"Authorization": f"Bearer {no_perm_token}"}
    )
    assert resp.status_code == 403
