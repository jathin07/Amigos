import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import UserAccount, TeamMember, Role
from app.core.extensions import bcrypt
from app.modules.master.city.models import City
from app.modules.master.district.models import District
from app.modules.master.state.models import State
from app.modules.master.country.models import Country


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
    with app.app_context():
        role = Role(name="Master Admin", code="MASTER_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="City",
            display_name="City Admin",
            official_email="city@test.com",
            phone="9999999912",
            employee_code="CTEST01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="city@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "master.city.read",
                "master.city.create",
                "master.city.update",
                "master.city.delete",
            ]},
        )
        return token


@pytest.fixture
def no_perm_token(app):
    with app.app_context():
        token = create_access_token(
            identity=str(uuid.uuid4()),
            additional_claims={"permissions": []},
        )
        return token


@pytest.fixture
def test_hierarchy(app):
    with app.app_context():
        country = Country(name="India", code="IN", phone_code="+91", is_active=True)
        db.session.add(country)
        db.session.flush()

        state = State(name="Kerala", code="KL", country_id=country.id, is_active=True)
        db.session.add(state)
        db.session.flush()

        district = District(name="Ernakulam", code="EKM", state_id=state.id, is_active=True)
        db.session.add(district)
        db.session.commit()

        return {
            "state_id": str(state.id),
            "district_id": str(district.id)
        }


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_city_success(client, auth_token, test_hierarchy):
    payload = {
        "name": "Kochi",
        "code": "COK",
        "state_id": test_hierarchy["state_id"],
        "District_id": test_hierarchy["district_id"],
        "description": "Port City"
    }
    resp = client.post("/api/v1/masters/cities", json=payload, headers=auth_headers(auth_token))
    assert resp.status_code == 201
    assert resp.get_json()["data"]["code"] == "COK"


def test_duplicate_code(client, auth_token, test_hierarchy):
    payload = {
        "name": "Kochi",
        "code": "COK",
        "state_id": test_hierarchy["state_id"],
        "District_id": test_hierarchy["district_id"]
    }
    client.post("/api/v1/masters/cities", json=payload, headers=auth_headers(auth_token))
    resp = client.post("/api/v1/masters/cities", json=payload, headers=auth_headers(auth_token))
    assert resp.status_code == 409


def test_create_validation_error(client, auth_token):
    resp = client.post("/api/v1/masters/cities", json={"name": "Kochi"}, headers=auth_headers(auth_token))
    assert resp.status_code == 400


def test_get_by_id(client, auth_token, test_hierarchy):
    payload = {
        "name": "Kochi",
        "code": "COK",
        "state_id": test_hierarchy["state_id"],
        "District_id": test_hierarchy["district_id"]
    }
    create_resp = client.post("/api/v1/masters/cities", json=payload, headers=auth_headers(auth_token))
    city_id = create_resp.get_json()["data"]["id"]

    resp = client.get(f"/api/v1/masters/cities/{city_id}", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["id"] == city_id


def test_get_not_found(client, auth_token):
    resp = client.get(f"/api/v1/masters/cities/{uuid.uuid4()}", headers=auth_headers(auth_token))
    assert resp.status_code == 404


def test_update_success(client, auth_token, test_hierarchy):
    payload = {
        "name": "Kochi",
        "code": "COK",
        "state_id": test_hierarchy["state_id"],
        "District_id": test_hierarchy["district_id"]
    }
    create_resp = client.post("/api/v1/masters/cities", json=payload, headers=auth_headers(auth_token))
    city_id = create_resp.get_json()["data"]["id"]

    resp = client.put(
        f"/api/v1/masters/cities/{city_id}",
        json={"name": "Cochin", "version": 1},
        headers=auth_headers(auth_token)
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["name"] == "Cochin"


def test_delete_soft(client, auth_token, test_hierarchy, app):
    payload = {
        "name": "Kochi",
        "code": "COK",
        "state_id": test_hierarchy["state_id"],
        "District_id": test_hierarchy["district_id"]
    }
    create_resp = client.post("/api/v1/masters/cities", json=payload, headers=auth_headers(auth_token))
    city_id = create_resp.get_json()["data"]["id"]

    resp = client.delete(f"/api/v1/masters/cities/{city_id}", headers=auth_headers(auth_token))
    assert resp.status_code == 200

    with app.app_context():
        city = City.query.get(uuid.UUID(city_id))
        assert city.is_active is False
