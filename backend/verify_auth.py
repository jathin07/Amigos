import os
import sys
import uuid
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.startup import create_app
from app.core.extensions import db, bcrypt
import app.models

from app.models import (
    UserAccount,
    TeamMember,
    Role
)

app = create_app("testing")


# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def print_title(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_result(name, response):
    status = "PASS" if response.status_code < 400 else "FAIL"

    print(f"\n{name}")
    print(f"Status : {response.status_code} [{status}]")
    print("Response:")
    print(response.get_json())


# --------------------------------------------------------
# Main Test
# --------------------------------------------------------

try:

    with app.app_context():

        print_title("Preparing Database")

        db.drop_all()
        db.create_all()

        role = Role(
            name="Admin",
            code="admin"
        )

        db.session.add(role)
        db.session.flush()

        team_member = TeamMember(
            id=uuid.uuid4(),
            first_name="Test",
            last_name="User",
            display_name="Test User",
            employee_code="TM999",
            official_email="test@example.com",
            designation="Tester",
            phone="1234567890",
            role=role,
            is_active=True
        )

        db.session.add(team_member)
        db.session.flush()

        user = UserAccount(
            id=uuid.uuid4(),
            username="testuser",
            team_member=team_member,
            password_hash=bcrypt.generate_password_hash(
                "Password123"
            ).decode(),
            is_active=True
        )

        db.session.add(user)
        db.session.commit()

        print("Database Ready")

        client = app.test_client()

        # ====================================================
        # 1 LOGIN SUCCESS
        # ====================================================

        print_title("1. LOGIN SUCCESS")

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Password123"
            }
        )

        print_result("Login", response)

        if response.status_code != 200:
            raise Exception("Login failed")

        body = response.get_json()

        access_token = body["data"]["session"]["access_token"]
        refresh_token = body["data"]["session"]["refresh_token"]

        # ====================================================
        # 2 INVALID PASSWORD
        # ====================================================

        print_title("2. INVALID PASSWORD")

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword"
            }
        )

        print_result("Invalid Password", response)

        # ====================================================
        # 3 INVALID EMAIL
        # ====================================================

        print_title("3. INVALID EMAIL")

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@test.com",
                "password": "Password123"
            }
        )

        print_result("Invalid Email", response)

        # ====================================================
        # 4 CURRENT USER
        # ====================================================

        print_title("4. CURRENT USER")

        response = client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        print_result("Current User", response)

        # ====================================================
        # 5 INVALID JWT
        # ====================================================

        print_title("5. INVALID JWT")

        response = client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer invalidtoken"
            }
        )

        print_result("Invalid JWT", response)

        # ====================================================
        # 6 REFRESH TOKEN
        # ====================================================

        print_title("6. REFRESH TOKEN")

        response = client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": refresh_token
            }
        )

        print_result("Refresh", response)

        if response.status_code == 200:
            new_refresh = response.get_json()["data"]["refresh_token"]

            if new_refresh == refresh_token:
                print("\n❌ Refresh token rotation FAILED")
            else:
                print("\n✅ Refresh token rotated successfully")

        # ====================================================
        # 7 REUSE OLD TOKEN
        # ====================================================

        print_title("7. OLD REFRESH TOKEN")

        response = client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": refresh_token
            }
        )

        print_result("Reuse Old Refresh Token", response)

        # ====================================================
        # 8 LOGOUT
        # ====================================================

        print_title("8. LOGOUT")

        response = client.post(
            "/api/v1/auth/logout",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            json={
                "refresh_token": new_refresh
            }
        )

        print_result("Logout", response)

        # ====================================================
        # 9 REFRESH AFTER LOGOUT
        # ====================================================

        print_title("9. REFRESH AFTER LOGOUT")

        response = client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": new_refresh
            }
        )

        print_result("Refresh After Logout", response)

        # ====================================================
        # CLEANUP
        # ====================================================

        print_title("Cleaning Database")

        db.drop_all()

        print("\n🎉 Authentication Verification Completed Successfully")

except Exception:

    traceback.print_exc()

    with app.app_context():
        db.drop_all()