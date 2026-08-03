import pytest
from datetime import datetime, timezone, timedelta
import uuid

from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db, bcrypt
from app.models import UserAccount, TeamMember, Role, RefreshToken
from app.common.utils import current_utc_time
from app.modules.auth.permissions import role_required, permission_required

@pytest.fixture
def app():
    app = create_app("testing")
    
    # Add dummy routes for testing decorators
    @app.route("/api/v1/test_role", methods=["GET"])
    @role_required("Admin")
    def test_role_route():
        return {"status": "ok"}
        
    @app.route("/api/v1/test_perm", methods=["GET"])
    @permission_required("admin.full")
    def test_perm_route():
        return {"status": "ok"}

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_user(app):
    role = Role(name="Admin", code="ADMIN")
    tm = TeamMember(
        first_name="Test",
        display_name="Test User",
        official_email="test@example.com",
        phone="1234567890",
        employee_code="TM999",
        role=role,
        is_active=True
    )
    db.session.add(role)
    db.session.add(tm)
    db.session.flush()

    user = UserAccount(
        team_member_id=tm.id,
        username="test@example.com",
        password_hash=bcrypt.generate_password_hash("password123").decode(),
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def setup_user_no_perms(app):
    role = Role(name="Basic", code="BASIC")
    tm = TeamMember(
        first_name="Basic",
        display_name="Basic User",
        official_email="basic@example.com",
        phone="1234567891",
        employee_code="TM998",
        role=role,
        is_active=True
    )
    db.session.add(role)
    db.session.add(tm)
    db.session.flush()

    user = UserAccount(
        team_member_id=tm.id,
        username="basic@example.com",
        password_hash=bcrypt.generate_password_hash("password123").decode(),
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user

def test_successful_login(client, setup_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

def test_invalid_password(client, setup_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_unknown_email(client, setup_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "unknown@example.com",
        "password": "password123"
    })
    assert response.status_code == 401

def test_inactive_account(client, setup_user):
    setup_user.is_active = False
    db.session.commit()

    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 401

def test_locked_account(client, setup_user):
    setup_user.locked_until = current_utc_time() + timedelta(minutes=30)
    db.session.commit()

    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"]["code"] == "ERR_ACCOUNT_LOCKED"

def test_expired_access_token(client, setup_user, app):
    with app.app_context():
        expired_token = create_access_token(
            identity=str(setup_user.id),
            expires_delta=timedelta(seconds=-1)
        )
    
    response = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {expired_token}"
    })
    assert response.status_code == 401

def test_revoked_refresh_token(client, setup_user):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    tokens = login_res.get_json()["data"]["session"]
    refresh_token = tokens["refresh_token"]

    token_record = RefreshToken.query.first()
    token_record.is_revoked = True
    db.session.commit()

    refresh_res = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_res.status_code == 401

def test_invalid_jwt(client):
    response = client.get("/api/v1/auth/me", headers={
        "Authorization": "Bearer invalid_token_signature_foo_bar"
    })
    assert response.status_code in [401, 422]

def test_missing_authorization_header(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_user_without_required_role(client, setup_user_no_perms):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "basic@example.com",
        "password": "password123"
    })
    access_token = login_res.get_json()["data"]["session"]["access_token"]

    response = client.get("/api/v1/test_role", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 403

def test_user_without_required_permission(client, setup_user_no_perms):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "basic@example.com",
        "password": "password123"
    })
    access_token = login_res.get_json()["data"]["session"]["access_token"]

    response = client.get("/api/v1/test_perm", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 403

def test_change_password_with_incorrect_password(client, setup_user):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    access_token = login_res.get_json()["data"]["session"]["access_token"]

    res = client.post("/api/v1/auth/change-password", json={
        "current_password": "wrongpassword123",
        "new_password": "newpassword456",
        "confirm_password": "newpassword456"
    }, headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert res.status_code == 400

def test_password_change(client, setup_user):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    access_token = login_res.get_json()["data"]["session"]["access_token"]

    res = client.post("/api/v1/auth/change-password", json={
        "current_password": "password123",
        "new_password": "newpassword456",
        "confirm_password": "newpassword456"
    }, headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert res.status_code == 200

def test_reuse_old_refresh_token(client, setup_user):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    tokens = login_res.get_json()["data"]["session"]
    old_refresh = tokens["refresh_token"]

    refresh_res = client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh
    })
    assert refresh_res.status_code == 200

    refresh_res_again = client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh
    })
    assert refresh_res_again.status_code == 401

def test_get_me(client, setup_user):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    access_token = login_res.get_json()["data"]["session"]["access_token"]

    response = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200

def test_verify(client, setup_user):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    access_token = login_res.get_json()["data"]["session"]["access_token"]

    response = client.get("/api/v1/auth/verify", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200

def test_logout(client, setup_user):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    tokens = login_res.get_json()["data"]["session"]

    logout_res = client.post("/api/v1/auth/logout", json={
        "refresh_token": tokens["refresh_token"]
    }, headers={
        "Authorization": f"Bearer {tokens['access_token']}"
    })
    assert logout_res.status_code == 200

def test_forgot_and_reset_password(client, setup_user):
    res_forgot = client.post("/api/v1/auth/forgot-password", json={
        "email": "test@example.com"
    })
    assert res_forgot.status_code == 200
    assert setup_user.reset_token_hash is not None
