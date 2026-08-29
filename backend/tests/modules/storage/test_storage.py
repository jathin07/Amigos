import pytest
import uuid
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db, bcrypt
from app.models import UserAccount, TeamMember, Role, UploadedFile

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
def user_roles(app):
    with app.app_context():
        admin_role = Role(name="Admin", code="ADMIN", is_system=True)
        staff_role = Role(name="Staff", code="STAFF", is_system=True)
        db.session.add_all([admin_role, staff_role])
        db.session.commit()
        return {"ADMIN": admin_role.id, "STAFF": staff_role.id}

@pytest.fixture
def staff_token(app, user_roles):
    """Token for regular staff member (non-admin)"""
    with app.app_context():
        tm = TeamMember(
            first_name="Staff",
            display_name="Staff User",
            official_email="staff@test.com",
            phone="1234567890",
            role_id=user_roles["STAFF"]
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="staff@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [], "role": "Staff"}
        )
        return token, tm.id

@pytest.fixture
def admin_token(app, user_roles):
    """Token for admin member"""
    with app.app_context():
        tm = TeamMember(
            first_name="Admin",
            display_name="Admin User",
            official_email="admin@test.com",
            phone="9876543210",
            role_id=user_roles["ADMIN"]
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="admin@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": ["admin.full"], "role": "Admin"}
        )
        return token, tm.id

@pytest.fixture
def other_user_token(app, user_roles):
    """Token for another staff member"""
    with app.app_context():
        tm = TeamMember(
            first_name="Other",
            display_name="Other User",
            official_email="other@test.com",
            phone="5555555555",
            role_id=user_roles["STAFF"]
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="other@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [], "role": "Staff"}
        )
        return token, tm.id

# ----------------- TEST CASES -----------------

# 1. Valid presigned URL generation (public folder)
def test_generate_presigned_url_happy_path(client, staff_token):
    token, tm_id = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "folder": "public/team",
        "filename": "avatar.jpg",
        "content_type": "image/jpeg",
        "file_size": 1024 * 1024 # 1MB
    }
    res = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    assert res.status_code == 201
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert "upload_url" in json_data["data"]
    assert "public_url" in json_data["data"]
    assert "object_key" in json_data["data"]
    assert json_data["data"]["object_key"].startswith("public/team/")
    assert json_data["data"]["object_key"].endswith(".jpg")

# 2. Unauthorized user (missing bearer token)
def test_generate_presigned_url_unauthorized(client):
    payload = {
        "folder": "public/team",
        "filename": "avatar.jpg",
        "content_type": "image/jpeg",
        "file_size": 1024 * 1024
    }
    res = client.post("/api/v1/storage/presign", json=payload)
    assert res.status_code in (401, 403)

# 3. Invalid folder
def test_generate_presigned_url_invalid_folder(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "folder": "public/invalid",
        "filename": "avatar.jpg",
        "content_type": "image/jpeg",
        "file_size": 1024
    }
    res = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    assert res.status_code == 422
    assert "folder" in res.get_json()["errors"][0]["field"]

# 4. Invalid extension
def test_generate_presigned_url_invalid_extension(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "folder": "public/team",
        "filename": "malicious.exe",
        "content_type": "image/jpeg",
        "file_size": 1024
    }
    res = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    assert res.status_code == 422
    assert "filename" in res.get_json()["errors"][0]["field"]

# 5. Extension and MIME type mismatch
def test_generate_presigned_url_mime_mismatch(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "folder": "public/team",
        "filename": "avatar.jpg",
        "content_type": "application/pdf",
        "file_size": 1024
    }
    res = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    assert res.status_code == 422
    assert "content_type" in res.get_json()["errors"][0]["field"]

# 6. Oversized file
def test_generate_presigned_url_oversized_file(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "folder": "public/team",
        "filename": "huge_avatar.png",
        "content_type": "image/png",
        "file_size": 6 * 1024 * 1024 # 6MB, limit is 5MB
    }
    res = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    assert res.status_code == 422
    assert "file_size" in res.get_json()["errors"][0]["field"]

# 7. Complete upload of existing object (happy path)
def test_complete_upload_happy_path(app, client, staff_token):
    token, tm_id = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Pre-register file in DB
    with app.app_context():
        file_record = UploadedFile(
            object_key="public/team/abc-123.jpg",
            original_filename="avatar.jpg",
            file_size=100,
            content_type="image/jpeg",
            namespace="public",
            folder="public/team",
            uploaded_by_team_member_id=tm_id,
            is_completed=False
        )
        db.session.add(file_record)
        db.session.commit()

    payload = {"object_key": "public/team/abc-123.jpg"}
    res = client.post("/api/v1/storage/complete", json=payload, headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["is_completed"] is True
    assert json_data["data"]["completed_at"] is not None

# 8. Complete upload of nonexistent object
def test_complete_upload_nonexistent(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"object_key": "public/team/nonexistent-key.jpg"}
    res = client.post("/api/v1/storage/complete", json=payload, headers=headers)
    assert res.status_code == 404

# 9. Delete existing object (happy path, owned by current user)
def test_delete_object_happy_path_owner(app, client, staff_token):
    token, tm_id = staff_token
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        file_record = UploadedFile(
            object_key="public/team/avatar-owner.jpg",
            original_filename="avatar.jpg",
            file_size=100,
            content_type="image/jpeg",
            namespace="public",
            folder="public/team",
            uploaded_by_team_member_id=tm_id,
            is_completed=True
        )
        db.session.add(file_record)
        db.session.commit()

    payload = {"object_key": "public/team/avatar-owner.jpg"}
    res = client.delete("/api/v1/storage/object", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.get_json()["status"] == "success"

# 10. Delete object owned by other user (fails with 403)
def test_delete_object_unauthorized_other_user(app, client, staff_token, other_user_token):
    token, _ = staff_token # current caller (staff)
    other_token, other_tm_id = other_user_token # owner of file
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        file_record = UploadedFile(
            object_key="public/team/other-user-file.jpg",
            original_filename="avatar.jpg",
            file_size=100,
            content_type="image/jpeg",
            namespace="public",
            folder="public/team",
            uploaded_by_team_member_id=other_tm_id,
            is_completed=True
        )
        db.session.add(file_record)
        db.session.commit()

    payload = {"object_key": "public/team/other-user-file.jpg"}
    res = client.delete("/api/v1/storage/object", json=payload, headers=headers)
    assert res.status_code == 403

# 11. Admin can delete any object
def test_delete_object_admin_override(app, client, admin_token, other_user_token):
    admin_tok, _ = admin_token # Admin caller
    _, other_tm_id = other_user_token # regular user file owner
    headers = {"Authorization": f"Bearer {admin_tok}"}

    with app.app_context():
        file_record = UploadedFile(
            object_key="public/team/other-user-avatar.jpg",
            original_filename="avatar.jpg",
            file_size=100,
            content_type="image/jpeg",
            namespace="public",
            folder="public/team",
            uploaded_by_team_member_id=other_tm_id,
            is_completed=True
        )
        db.session.add(file_record)
        db.session.commit()

    payload = {"object_key": "public/team/other-user-avatar.jpg"}
    res = client.delete("/api/v1/storage/object", json=payload, headers=headers)
    assert res.status_code == 200

# 12. Delete nonexistent object
def test_delete_object_nonexistent(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"object_key": "public/team/nonexistent.jpg"}
    res = client.delete("/api/v1/storage/object", json=payload, headers=headers)
    assert res.status_code == 404

# 13. Public folder download URL generation (happy path, direct CDN URL)
def test_generate_download_url_public(app, client, staff_token):
    token, tm_id = staff_token
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        file_record = UploadedFile(
            object_key="public/team/public-avatar.jpg",
            original_filename="avatar.jpg",
            file_size=100,
            content_type="image/jpeg",
            namespace="public",
            folder="public/team",
            uploaded_by_team_member_id=tm_id,
            is_completed=True
        )
        db.session.add(file_record)
        db.session.commit()

    res = client.get("/api/v1/storage/download?object_key=public/team/public-avatar.jpg", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert "download_url" in json_data["data"]
    assert "https://cdn.amigostourism.com/public/team/public-avatar.jpg" in json_data["data"]["download_url"]

# 14. Private folder download URL generation (happy path, signed download link)
def test_generate_download_url_private(app, client, staff_token):
    token, tm_id = staff_token
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        file_record = UploadedFile(
            object_key="private/passports/private-passport.pdf",
            original_filename="passport.pdf",
            file_size=5000,
            content_type="application/pdf",
            namespace="private",
            folder="private/passports",
            uploaded_by_team_member_id=tm_id,
            is_completed=True
        )
        db.session.add(file_record)
        db.session.commit()

    res = client.get("/api/v1/storage/download?object_key=private/passports/private-passport.pdf", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert "download_url" in json_data["data"]
    assert "signature=signed-download" in json_data["data"]["download_url"]

# 15. Download URL generation of nonexistent object (fails 404)
def test_generate_download_url_nonexistent(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/storage/download?object_key=public/team/nonexistent.jpg", headers=headers)
    assert res.status_code == 404

# 16. Download URL generation of uncompleted object (fails 400)
def test_generate_download_url_uncompleted(app, client, staff_token):
    token, tm_id = staff_token
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        file_record = UploadedFile(
            object_key="public/team/uncompleted.jpg",
            original_filename="avatar.jpg",
            file_size=100,
            content_type="image/jpeg",
            namespace="public",
            folder="public/team",
            uploaded_by_team_member_id=tm_id,
            is_completed=False
        )
        db.session.add(file_record)
        db.session.commit()

    res = client.get("/api/v1/storage/download?object_key=public/team/uncompleted.jpg", headers=headers)
    assert res.status_code == 400

# 17. Cleanup of uncompleted orphans (happy path)
def test_cleanup_orphans(app, client, admin_token):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        # Complete file - should not be cleaned
        f1 = UploadedFile(
            object_key="public/team/f1.jpg", original_filename="a.jpg", file_size=100,
            content_type="image/jpeg", namespace="public", folder="public/team", is_completed=True
        )
        # Recent uncompleted file - should not be cleaned
        f2 = UploadedFile(
            object_key="public/team/f2.jpg", original_filename="b.jpg", file_size=100,
            content_type="image/jpeg", namespace="public", folder="public/team", is_completed=False
        )
        # Old uncompleted file - should be cleaned
        f3 = UploadedFile(
            object_key="public/team/f3.jpg", original_filename="c.jpg", file_size=100,
            content_type="image/jpeg", namespace="public", folder="public/team", is_completed=False
        )
        db.session.add_all([f1, f2, f3])
        db.session.commit()

        # Manually alter f3 created_at using raw SQL / modification to be 25 hours ago
        f3.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
        db.session.commit()

    res = client.post("/api/v1/storage/cleanup?hours=24", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["deleted_count"] == 1

# 18. Verification metadata stored correctly
def test_metadata_stored_correctly(app, client, staff_token):
    token, tm_id = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "folder": "public/team",
        "filename": "avatar.png",
        "content_type": "image/png",
        "file_size": 250000
    }
    res = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    assert res.status_code == 201
    object_key = res.get_json()["data"]["object_key"]

    with app.app_context():
        record = db.session.scalar(db.select(UploadedFile).where(UploadedFile.object_key == object_key))
        assert record is not None
        assert record.original_filename == "avatar.png"
        assert record.file_size == 250000
        assert record.content_type == "image/png"
        assert record.folder == "public/team"
        assert record.is_completed is False

# 19. UUID key generation uniqueness
def test_uuid_key_generation_uniqueness(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "folder": "public/team",
        "filename": "avatar.jpg",
        "content_type": "image/jpeg",
        "file_size": 100
    }
    res1 = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    res2 = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    
    key1 = res1.get_json()["data"]["object_key"]
    key2 = res2.get_json()["data"]["object_key"]
    assert key1 != key2

# 20. Missing request schema parameters
def test_presign_missing_parameters(client, staff_token):
    token, _ = staff_token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "folder": "public/team",
        "filename": "avatar.jpg"
        # missing content_type and file_size
    }
    res = client.post("/api/v1/storage/presign", json=payload, headers=headers)
    assert res.status_code == 422
    assert len(res.get_json()["errors"]) >= 2
