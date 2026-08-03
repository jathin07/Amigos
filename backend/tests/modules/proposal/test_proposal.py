import pytest
import uuid
from decimal import Decimal
from unittest.mock import patch, ANY
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from app.core.startup import create_app
from app.core.extensions import db
from app.models import (
    UserAccount, TeamMember, Role, Lead, LeadStatus, LeadSource,
    Proposal, ProposalDestination, ProposalStatus, ContactPerson
)
from app.core.extensions import bcrypt


# ─────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────

@pytest.fixture
def app():
    app = create_app("testing")
    app.config["PROPOSAL_VERSION_MAX_RETRIES"] = 3
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
    """Create a user with proposal permissions and return a valid JWT."""
    with app.app_context():
        role = Role(name="Proposal Admin", code="PROPOSAL_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Proposal",
            display_name="Proposal Admin",
            official_email="proposal@test.com",
            phone="9999999994",
            employee_code="PROP01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="proposal@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "proposal.read",
                "proposal.create",
                "proposal.update",
                "proposal.delete",
                "proposal.finalize"
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
def test_data(app):
    """Populate lookup data, destination, active lead, and lost lead."""
    with app.app_context():
        # Proposal Statuses
        statuses = {}
        for code in ["DRAFT", "UNDER_DISCUSSION", "REVISED", "APPROVED", "WAITING_FOR_ADVANCE", "CONVERTED", "ARCHIVED"]:
            status = ProposalStatus(code=code, name=code.title().replace("_", " "))
            db.session.add(status)
            statuses[code] = status
        db.session.flush()

        # Lead Statuses
        new_status = LeadStatus(code="NEW", name="New")
        lost_status = LeadStatus(code="LOST", name="Lost")
        db.session.add_all([new_status, lost_status])
        db.session.flush()

        # Lead Source
        source = LeadSource(code="REF", name="Referral")
        db.session.add(source)
        db.session.flush()

        # Destination
        dest_table = db.metadata.tables["destinations"]
        dest1_id = uuid.uuid4()
        dest2_id = uuid.uuid4()
        db.session.execute(
            dest_table.insert().values(
                id=dest1_id,
                name="Munnar",
                state="Kerala",
                country="India",
                is_active=True,
                is_deleted=False,
            )
        )
        db.session.execute(
            dest_table.insert().values(
                id=dest2_id,
                name="Vagamon",
                state="Kerala",
                country="India",
                is_active=True,
                is_deleted=False,
            )
        )
        db.session.flush()

        # Contact Person
        contact = ContactPerson(name="Contact Person", phone="9876543210")
        db.session.add(contact)
        db.session.flush()

        # Active Lead
        active_lead = Lead(
            lead_number="AM-LD-2026-00001",
            contact_person_id=contact.id,
            lead_source_id=source.id,
            current_status_id=new_status.id,
            is_deleted=False
        )
        # Lost Lead
        lost_lead = Lead(
            lead_number="AM-LD-2026-00002",
            contact_person_id=contact.id,
            lead_source_id=source.id,
            current_status_id=lost_status.id,
            is_deleted=False
        )
        db.session.add_all([active_lead, lost_lead])
        db.session.commit()

        return {
            "statuses": {code: status.id for code, status in statuses.items()},
            "lead_id": active_lead.id,
            "lost_lead_id": lost_lead.id,
            "dest1_id": dest1_id,
            "dest2_id": dest2_id,
        }


# ─────────────────────────────────────────────────────────────────
# 1. Core CRUD Tests
# ─────────────────────────────────────────────────────────────────

def test_create_proposal_success(client, auth_token, test_data):
    payload = {
        "lead_id": str(test_data["lead_id"]),
        "proposal_title": "Custom Munnar Escape",
        "price_per_person": 10000.00,
        "total_amount": 50000.00,
        "destinations": [
            {
                "destination_id": str(test_data["dest1_id"]),
                "day_order": 1,
                "sequence_no": 1,
                "overnight_stay": True,
                "day_title": "Day 1: Arrival"
            }
        ],
        "structured_itinerary": {
            "days": [{"day_number": 1, "title": "Day 1: Arrival", "hotel": "Test Hotel"}]
        }
    }
    resp = client.post("/api/v1/proposals", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 201
    data = resp.json["data"]
    assert data["version"] == 1
    assert data["proposal_title"] == "Custom Munnar Escape"
    assert len(data["destinations"]) == 1
    assert data["destinations"][0]["destination_name"] == "Munnar"


def test_create_proposal_increments_version(client, auth_token, test_data):
    # First proposal
    payload = {
        "lead_id": str(test_data["lead_id"]),
        "proposal_title": "Munnar V1",
    }
    resp = client.post("/api/v1/proposals", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 201
    assert resp.json["data"]["version"] == 1

    # Second proposal
    payload["proposal_title"] = "Munnar V2"
    resp = client.post("/api/v1/proposals", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 201
    assert resp.json["data"]["version"] == 2


def test_create_proposal_invalid_lead_lost(client, auth_token, test_data):
    payload = {
        "lead_id": str(test_data["lost_lead_id"]),
        "proposal_title": "Munnar Lost Escape",
    }
    resp = client.post("/api/v1/proposals", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 409
    assert resp.json["error"]["code"] == "ERR_LEAD_INELIGIBLE"


def test_create_proposal_invalid_destination(client, auth_token, test_data):
    payload = {
        "lead_id": str(test_data["lead_id"]),
        "proposal_title": "Munnar Bad Dest",
        "destinations": [
            {
                "destination_id": str(uuid.uuid4()),
                "day_order": 1,
            }
        ]
    }
    resp = client.post("/api/v1/proposals", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 400
    assert resp.json["error"]["code"] == "ERR_VALIDATION"


def test_get_proposal_success(client, auth_token, test_data):
    # Create first
    payload = {
        "lead_id": str(test_data["lead_id"]),
        "proposal_title": "Get Test",
    }
    create_resp = client.post("/api/v1/proposals", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    # Retrieve
    get_resp = client.get(f"/api/v1/proposals/{proposal_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert get_resp.status_code == 200
    assert get_resp.json["data"]["proposal_title"] == "Get Test"


def test_get_proposal_not_found(client, auth_token, test_data):
    resp = client.get(f"/api/v1/proposals/{uuid.uuid4()}", headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 404
    assert resp.json["error"]["code"] == "ERR_NOT_FOUND"


def test_list_by_lead_success(client, auth_token, test_data):
    # Create two versions
    client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1"}, headers={"Authorization": f"Bearer {auth_token}"})
    client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V2"}, headers={"Authorization": f"Bearer {auth_token}"})

    resp = client.get(f"/api/v1/leads/{test_data['lead_id']}/proposals", headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 200
    versions = resp.json["data"]
    assert len(versions) == 2
    assert versions[0]["version"] == 2
    assert versions[1]["version"] == 1


def test_update_proposal_success(client, auth_token, test_data):
    # Create
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1"}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    # Update
    payload = {
        "row_version": 1,
        "proposal_title": "Updated Title",
        "total_amount": 60000.00,
    }
    update_resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert update_resp.status_code == 200
    data = update_resp.json["data"]
    assert data["proposal_title"] == "Updated Title"
    assert data["row_version"] == 2


def test_update_proposal_optimistic_lock(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1"}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    payload = {
        "row_version": 99,  # incorrect row version
        "proposal_title": "Updated Title",
    }
    resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 409
    assert resp.json["error"]["code"] == "ERR_CONCURRENT_MODIFICATION"


def test_update_proposal_finalized_blocked(client, auth_token, test_data):
    # Create
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    # Finalize
    client.post(f"/api/v1/proposals/{proposal_id}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})

    # Update (blocked)
    payload = {
        "row_version": 2,
        "proposal_title": "Updated Title",
    }
    resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 409
    assert resp.json["error"]["code"] == "ERR_PROPOSAL_IMMUTABLE"


def test_update_status_valid_transition(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1"}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    payload = {
        "row_version": 1,
        "status_id": str(test_data["statuses"]["UNDER_DISCUSSION"]),
    }
    resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 200
    assert resp.json["data"]["status"]["code"] == "UNDER_DISCUSSION"


def test_update_status_invalid_transition(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1"}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    payload = {
        "row_version": 1,
        "status_id": str(test_data["statuses"]["CONVERTED"]),  # DRAFT -> CONVERTED is illegal
    }
    resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 409
    assert resp.json["error"]["code"] == "ERR_INVALID_STATUS_TRANSITION"


def test_soft_delete_success(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1"}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    resp = client.delete(f"/api/v1/proposals/{proposal_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 200

    # Retrieve again should fail with 404
    get_resp = client.get(f"/api/v1/proposals/{proposal_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert get_resp.status_code == 404


def test_soft_delete_finalized_blocked(client, auth_token, test_data):
    # Create APPROVED
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    # Finalize
    client.post(f"/api/v1/proposals/{proposal_id}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})

    # Delete
    resp = client.delete(f"/api/v1/proposals/{proposal_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 409
    assert resp.json["error"]["code"] == "ERR_PROPOSAL_IMMUTABLE"


# ─────────────────────────────────────────────────────────────────
# 2. Destination Three-State Tests
# ─────────────────────────────────────────────────────────────────

def test_update_destinations_replace(client, auth_token, test_data):
    # Create with dest1
    create_resp = client.post("/api/v1/proposals", json={
        "lead_id": str(test_data["lead_id"]),
        "proposal_title": "Dest Test",
        "destinations": [{"destination_id": str(test_data["dest1_id"]), "day_order": 1}]
    }, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    # Replace with dest2
    payload = {
        "row_version": 1,
        "destinations": [{"destination_id": str(test_data["dest2_id"]), "day_order": 1}]
    }
    resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 200
    dests = resp.json["data"]["destinations"]
    assert len(dests) == 1
    assert dests[0]["destination_id"] == str(test_data["dest2_id"])


def test_update_destinations_clear(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={
        "lead_id": str(test_data["lead_id"]),
        "proposal_title": "Dest Test",
        "destinations": [{"destination_id": str(test_data["dest1_id"]), "day_order": 1}]
    }, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    # Explicit clear destinations: []
    payload = {
        "row_version": 1,
        "destinations": []
    }
    resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 200
    assert len(resp.json["data"]["destinations"]) == 0


def test_update_destinations_absent(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={
        "lead_id": str(test_data["lead_id"]),
        "proposal_title": "Dest Test",
        "destinations": [{"destination_id": str(test_data["dest1_id"]), "day_order": 1}]
    }, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    # Absent key
    payload = {
        "row_version": 1,
        "proposal_title": "New Title Only"
    }
    resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 200
    dests = resp.json["data"]["destinations"]
    assert len(dests) == 1
    assert dests[0]["destination_id"] == str(test_data["dest1_id"])


# ─────────────────────────────────────────────────────────────────
# 3. Finalization Tests
# ─────────────────────────────────────────────────────────────────

def test_finalize_proposal_success(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    resp = client.post(f"/api/v1/proposals/{proposal_id}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 200
    data = resp.json["data"]
    assert data["is_final"] is True
    assert data["status"]["code"] == "WAITING_FOR_ADVANCE"


def test_finalize_not_approved_blocked(client, auth_token, test_data):
    # draft proposal
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1"}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    resp = client.post(f"/api/v1/proposals/{proposal_id}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 409
    assert resp.json["error"]["code"] == "ERR_INVALID_STATUS_TRANSITION"


def test_finalize_conflict_second_final(client, auth_token, test_data):
    # Finalize V1 first
    create1 = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    id1 = create1.json["data"]["id"]
    client.post(f"/api/v1/proposals/{id1}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})

    # Try finalize V2 (conflict)
    create2 = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V2", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    id2 = create2.json["data"]["id"]
    resp = client.post(f"/api/v1/proposals/{id2}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 409
    assert resp.json["error"]["code"] == "ERR_FINALIZATION_CONFLICT"


def test_finalize_optimistic_lock(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    resp = client.post(f"/api/v1/proposals/{proposal_id}/finalize", json={"row_version": 99}, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp.status_code == 409
    assert resp.json["error"]["code"] == "ERR_CONCURRENT_MODIFICATION"


def test_finalize_event_published(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    with patch("app.workflow.engine.event_bus.publish") as mock_publish:
        resp = client.post(f"/api/v1/proposals/{proposal_id}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})
        assert resp.status_code == 200
        mock_publish.assert_any_call("PROPOSAL_FINALIZED", ANY)


# ─────────────────────────────────────────────────────────────────
# 4. Concurrency Tests
# ─────────────────────────────────────────────────────────────────

def test_concurrent_version_creation(app, client, auth_token, test_data):
    """Simulate a version creation collision where rollback triggers a retry."""
    from app.modules.proposal.service import ProposalService

    orig_generate = ProposalService._generate_next_version
    calls = []

    def mocked_generate(self, lead_id):
        ver = orig_generate(self, lead_id)
        calls.append(ver)
        if len(calls) == 1:
            # Force collision on the first attempt by inserting a dummy proposal inside database directly
            db.session.execute(
                db.insert(Proposal).values(
                    id=uuid.uuid4(),
                    lead_id=lead_id,
                    version=ver,
                    row_version=1,
                    proposal_title="Concurrent Collision",
                    status_id=test_data["statuses"]["DRAFT"],
                    is_final=False,
                    is_deleted=False
                )
            )
            db.session.commit()
        return ver

    with patch("app.modules.proposal.service.ProposalService._generate_next_version", mocked_generate):
        resp = client.post("/api/v1/proposals", json={
            "lead_id": str(test_data["lead_id"]),
            "proposal_title": "Retry Target"
        }, headers={"Authorization": f"Bearer {auth_token}"})
        assert resp.status_code == 201
        assert resp.json["data"]["version"] == 2  # generated version 2 (first 1 is in db)


def test_concurrent_finalization(client, auth_token, test_data):
    # Two approved proposals for the same lead
    c1 = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    id1 = c1.json["data"]["id"]
    c2 = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V2", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    id2 = c2.json["data"]["id"]

    # Finalize V1 first
    resp1 = client.post(f"/api/v1/proposals/{id1}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp1.status_code == 200

    # Simultaneous finalization of V2 should fail with conflict
    resp2 = client.post(f"/api/v1/proposals/{id2}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {auth_token}"})
    assert resp2.status_code == 409
    assert resp2.json["error"]["code"] == "ERR_FINALIZATION_CONFLICT"


# ─────────────────────────────────────────────────────────────────
# 5. Permission Tests
# ─────────────────────────────────────────────────────────────────

def test_proposal_requires_read_permission(client, no_perm_token):
    resp = client.get("/api/v1/proposals", headers={"Authorization": f"Bearer {no_perm_token}"})
    assert resp.status_code == 403


def test_proposal_requires_finalize_permission(client, auth_token, test_data):
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "V1", "status_id": str(test_data["statuses"]["APPROVED"])}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    # Create a token with ONLY update permission, missing finalize
    no_finalize_token = create_access_token(
        identity=str(uuid.uuid4()),
        additional_claims={"permissions": ["proposal.update"]}
    )

    resp = client.post(f"/api/v1/proposals/{proposal_id}/finalize", json={"row_version": 1}, headers={"Authorization": f"Bearer {no_finalize_token}"})
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────
# 6. Transaction / Rollback Tests
# ─────────────────────────────────────────────────────────────────

def test_create_destination_failure_rolls_back_proposal(client, auth_token, test_data):
    """If destinations sync fails, the entire proposal creation transaction should roll back."""
    payload = {
        "lead_id": str(test_data["lead_id"]),
        "proposal_title": "Rollback Test",
        "destinations": [{"destination_id": str(test_data["dest1_id"]), "day_order": 1}]
    }

    # Patch sync_destinations to throw an error
    with patch("app.modules.proposal.service.ProposalService._sync_destinations", side_effect=Exception("Failed to save child destination")):
        resp = client.post("/api/v1/proposals", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
        assert resp.status_code == 500

    # Ensure no proposal was created in database
    with client.application.app_context():
        proposals = db.session.scalars(db.select(Proposal).where(Proposal.proposal_title == "Rollback Test")).all()
        assert len(proposals) == 0


def test_update_destination_failure_rolls_back_fields(client, auth_token, test_data):
    """If child destination update fails, the main field updates must also roll back."""
    create_resp = client.post("/api/v1/proposals", json={"lead_id": str(test_data["lead_id"]), "proposal_title": "Original Title"}, headers={"Authorization": f"Bearer {auth_token}"})
    proposal_id = create_resp.json["data"]["id"]

    payload = {
        "row_version": 1,
        "proposal_title": "New Title",
        "destinations": [{"destination_id": str(test_data["dest1_id"]), "day_order": 1}]
    }

    with patch("app.modules.proposal.service.ProposalService._sync_destinations", side_effect=Exception("Failed to update child destinations")):
        resp = client.put(f"/api/v1/proposals/{proposal_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
        assert resp.status_code == 500

    # Verify that title remained "Original Title" in database
    with client.application.app_context():
        proposal = db.session.get(Proposal, uuid.UUID(proposal_id))
        assert proposal.proposal_title == "Original Title"


# ─────────────────────────────────────────────────────────────────
# 7. Performance Tests
# ─────────────────────────────────────────────────────────────────

def test_list_100_proposals_pagination(client, auth_token, test_data):
    """Verify performance is fast and pagination respects limits."""
    # Create 100 proposals in database directly to save request overhead
    with client.application.app_context():
        for i in range(100):
            p = Proposal(
                lead_id=test_data["lead_id"],
                version=i + 1,
                row_version=1,
                proposal_title=f"Bulk Proposal {i}",
                status_id=test_data["statuses"]["DRAFT"],
                is_final=False,
                is_deleted=False
            )
            db.session.add(p)
        db.session.commit()

    import time
    start = time.perf_counter()
    resp = client.get("/api/v1/proposals?page=2&page_size=20", headers={"Authorization": f"Bearer {auth_token}"})
    duration = time.perf_counter() - start

    assert resp.status_code == 200
    assert len(resp.json["data"]) == 20
    assert resp.json["meta"]["total_records"] == 100
    assert resp.json["meta"]["total_pages"] == 5
    # Performance requirement: response under 500ms
    assert duration < 0.500
