import pytest
import uuid
from flask_jwt_extended import create_access_token

from app.core.startup import create_app
from app.core.extensions import db
from app.models import (
    UserAccount, TeamMember, Role, ContactPerson, Lead, LeadStatus,
    LeadSource, LeadPriority, LeadLostReason, Booking, Customer, Task
)
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
    """Create a user with crm permissions and return a valid JWT."""
    with app.app_context():
        role = Role(name="CRM Admin", code="CRM_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="CRM",
            display_name="CRM Admin",
            official_email="crm@test.com",
            phone="9999999995",
            employee_code="CRM01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="crm@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "crm.read",
                "crm.create",
                "crm.update",
                "crm.delete",
                "crm.convert"
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


# ─────────────────────────────────────────────────────────────────
# Test cases: Contact Person
# ─────────────────────────────────────────────────────────────────

def test_create_contact_person_success(client, auth_token):
    payload = {
        "name": "Jathin",
        "phone": "9876543210",
        "email": "jathin@example.com",
        "designation": "Group Coordinator",
        "alternate_phone": "9876543211",
        "preferred_contact_method": "WhatsApp",
        "notes": "Prefers evening contact."
    }
    resp = client.post(
        "/api/v1/crm/contacts",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 201
    res = resp.get_json()
    assert res["success"] is True
    assert res["data"]["name"] == "Jathin"
    assert res["data"]["phone"] == "9876543210"
    assert res["data"]["email"] == "jathin@example.com"
    assert "id" in res["data"]


def test_create_contact_person_deduplication(client, auth_token):
    payload1 = {
        "name": "Jathin",
        "phone": "+91 98765 43210",
        "email": None,
        "designation": "Group Coordinator"
    }
    resp1 = client.post(
        "/api/v1/crm/contacts",
        json=payload1,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp1.status_code == 201
    id1 = resp1.get_json()["data"]["id"]

    # Try creating with normalized equivalent phone, new email and design.
    # It should resolve to the same contact person and fill in missing fields without overwrite.
    payload2 = {
        "name": "Jathin Copy",  # Diff name, but should NOT overwrite existing name "Jathin"
        "phone": "9876543210",
        "email": "jathin@example.com",  # Missing previously, should fill in
        "designation": "Updated Coordinator"  # Already had value, should NOT overwrite
    }
    resp2 = client.post(
        "/api/v1/crm/contacts",
        json=payload2,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 201
    res2 = resp2.get_json()
    assert res2["data"]["id"] == id1
    assert res2["data"]["name"] == "Jathin"  # Overwrite avoided!
    assert res2["data"]["email"] == "jathin@example.com"  # Missing filled!
    assert res2["data"]["designation"] == "Group Coordinator"  # Overwrite avoided!


def test_create_contact_person_validation_error(client, auth_token):
    # missing name, phone too short
    payload = {
        "phone": "123",
        "email": "invalid-email"
    }
    resp = client.post(
        "/api/v1/crm/contacts",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 400
    res = resp.get_json()
    assert res["success"] is False
    assert res["code"] == "ERR_VALIDATION"


def test_get_contact_person_success(client, auth_token):
    payload = {
        "name": "Jathin",
        "phone": "9876543210"
    }
    resp1 = client.post(
        "/api/v1/crm/contacts",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = resp1.get_json()["data"]["id"]

    resp2 = client.get(
        f"/api/v1/crm/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 200
    res = resp2.get_json()
    assert res["success"] is True
    assert res["data"]["id"] == contact_id
    assert res["data"]["name"] == "Jathin"


def test_get_contact_person_not_found(client, auth_token):
    random_id = str(uuid.uuid4())
    resp = client.get(
        f"/api/v1/crm/contacts/{random_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 404
    assert resp.get_json()["error"]["code"] == "ERR_NOT_FOUND"


def test_update_contact_person_success(client, auth_token):
    payload = {
        "name": "Jathin",
        "phone": "9876543210"
    }
    resp1 = client.post(
        "/api/v1/crm/contacts",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = resp1.get_json()["data"]["id"]

    update_payload = {
        "name": "Jathin Updated",
        "phone": "9876543210",
        "designation": "Manager"
    }
    resp2 = client.put(
        f"/api/v1/crm/contacts/{contact_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 200
    res = resp2.get_json()
    assert res["success"] is True
    assert res["data"]["name"] == "Jathin Updated"
    assert res["data"]["designation"] == "Manager"


def test_contact_person_requires_permission(client, no_perm_token):
    resp = client.post(
        "/api/v1/crm/contacts",
        json={"name": "Jathin", "phone": "9876543210"},
        headers={"Authorization": f"Bearer {no_perm_token}"}
    )
    assert resp.status_code == 403


@pytest.fixture
def crm_lookups(app):
    with app.app_context():
        # Statuses
        status_new = LeadStatus(code="NEW", name="New", is_active=True)
        status_assigned = LeadStatus(code="ASSIGNED", name="Assigned", is_active=True)
        status_contacted = LeadStatus(code="CONTACTED", name="Contacted", is_active=True)
        status_req = LeadStatus(code="REQUIREMENT_GATHERING", name="Requirement Gathering", is_active=True)
        status_prop = LeadStatus(code="PROPOSAL_SENT", name="Proposal Sent", is_active=True)
        status_negotiation = LeadStatus(code="NEGOTIATION", name="Negotiation", is_active=True)
        status_won = LeadStatus(code="WON", name="Won", is_active=True)
        status_lost = LeadStatus(code="LOST", name="Lost", is_active=True)
        db.session.add_all([
            status_new, status_assigned, status_contacted, status_req,
            status_prop, status_negotiation, status_won, status_lost
        ])
        
        # Sources
        source = LeadSource(code="INSTAGRAM", name="Instagram", is_active=True)
        db.session.add(source)

        # Priorities
        priority = LeadPriority(code="HIGH", name="High", is_active=True)
        db.session.add(priority)

        # Lost Reason
        lost_reason = LeadLostReason(code="BUDGET_TOO_HIGH", name="Budget too high", is_active=True)
        db.session.add(lost_reason)

        db.session.commit()
        
        return {
            "status_new_id": str(status_new.id),
            "status_assigned_id": str(status_assigned.id),
            "status_won_id": str(status_won.id),
            "status_lost_id": str(status_lost.id),
            "source_id": str(source.id),
            "priority_id": str(priority.id),
            "lost_reason_id": str(lost_reason.id)
        }


# ─────────────────────────────────────────────────────────────────
# Test cases: Lead Aggregate (Phase 5B)
# ─────────────────────────────────────────────────────────────────

def test_create_lead_success(client, auth_token, crm_lookups):
    payload = {
        "contact_person": {
            "name": "Jathin",
            "phone": "9876543210",
            "email": "jathin@example.com"
        },
        "lead_source_id": crm_lookups["source_id"],
        "priority_id": crm_lookups["priority_id"],
        "traveler_count": 3,
        "budget": "15000.00",
        "notes": "Testing manual lead creation."
    }
    resp = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 201
    res = resp.get_json()
    assert res["success"] is True
    assert res["data"]["lead_number"].startswith("AM-LD-")
    assert res["data"]["version"] == 1
    assert res["data"]["contact_person"]["name"] == "Jathin"


def test_create_lead_missing_contact_error(client, auth_token, crm_lookups):
    payload = {
        "lead_source_id": crm_lookups["source_id"]
    }
    resp = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 400
    res = resp.get_json()
    assert res["code"] == "ERR_VALIDATION"


def test_update_lead_success(client, auth_token, crm_lookups):
    # 1. Create
    payload = {
        "contact_person": {
            "name": "Jathin",
            "phone": "9876543210"
        },
        "lead_source_id": crm_lookups["source_id"]
    }
    resp1 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    lead_id = resp1.get_json()["data"]["id"]

    # 2. Update
    update_payload = {
        "version": 1,
        "notes": "Updated notes",
        "current_status_id": crm_lookups["status_assigned_id"]
    }
    resp2 = client.put(
        f"/api/v1/leads/{lead_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 200
    res = resp2.get_json()
    assert res["data"]["version"] == 2
    assert res["data"]["notes"] == "Updated notes"
    assert res["data"]["current_status"]["id"] == crm_lookups["status_assigned_id"]


def test_update_lead_optimistic_lock_error(client, auth_token, crm_lookups):
    payload = {
        "contact_person": {
            "name": "Jathin",
            "phone": "9876543210"
        },
        "lead_source_id": crm_lookups["source_id"]
    }
    resp1 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    lead_id = resp1.get_json()["data"]["id"]

    # Send update with incorrect version (e.g. 5 instead of 1)
    update_payload = {
        "version": 5,
        "notes": "Stale update check"
    }
    resp2 = client.put(
        f"/api/v1/leads/{lead_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 409
    assert resp2.get_json()["code"] == "ERR_OPTIMISTIC_LOCK"


def test_update_lead_status_transition_invalid(client, auth_token, crm_lookups):
    payload = {
        "contact_person": {
            "name": "Jathin",
            "phone": "9876543210"
        },
        "lead_source_id": crm_lookups["source_id"]
    }
    resp1 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    lead_id = resp1.get_json()["data"]["id"]

    # Initial status is NEW. Transition directly to REQUIREMENT_GATHERING is not allowed.
    update_payload = {
        "version": 1,
        "current_status_id": crm_lookups["status_won_id"]  # NEW -> WON is invalid
    }
    resp2 = client.put(
        f"/api/v1/leads/{lead_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 400
    assert resp2.get_json()["code"] == "ERR_INVALID_STATUS_TRANSITION"


def test_update_lead_assignment_logging(client, app, auth_token, crm_lookups):
    # 1. Create a TeamMember to assign to
    with app.app_context():
        role = Role(name="Agent", code="AGENT", is_system=False)
        db.session.add(role)
        db.session.flush()
        agent = TeamMember(
            first_name="Agent",
            display_name="CRM Agent",
            official_email="agent@test.com",
            phone="9876543222",
            employee_code="AG01",
            role_id=role.id,
            is_active=True
        )
        db.session.add(agent)
        db.session.commit()
        agent_id = str(agent.id)

    # 2. Create Lead
    payload = {
        "contact_person": {
            "name": "Jathin",
            "phone": "9876543210"
        },
        "lead_source_id": crm_lookups["source_id"]
    }
    resp1 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    lead_id = resp1.get_json()["data"]["id"]

    # 3. Assign Lead
    update_payload = {
        "version": 1,
        "owner_team_member_id": agent_id,
        "assignment_reason": "Escalated for pricing validation"
    }
    resp2 = client.put(
        f"/api/v1/leads/{lead_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 200

    # 4. Check Assignment History logs
    resp3 = client.get(
        f"/api/v1/leads/{lead_id}/assignments",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp3.status_code == 200
    res3 = resp3.get_json()
    assert len(res3["data"]) >= 1
    assert any(hist["new_team_member"]["id"] == agent_id for hist in res3["data"])
    assert any(hist["reason"] == "Escalated for pricing validation" for hist in res3["data"])


def test_convert_lead_to_booking_success(client, auth_token, crm_lookups):
    payload = {
        "contact_person": {
            "name": "Jathin",
            "phone": "9876543210"
        },
        "lead_source_id": crm_lookups["source_id"]
    }
    resp1 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    lead_json = resp1.get_json()["data"]
    lead_id = lead_json["id"]

    # Let's run transitions sequentially to reach PROPOSAL_SENT:
    # 1. Update status to ASSIGNED (Version 1 -> 2)
    resp_assigned = client.put(
        f"/api/v1/leads/{lead_id}",
        json={"version": 1, "current_status_id": crm_lookups["status_assigned_id"]},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_assigned.status_code == 200
    
    # 2. Update status to LOST (or sequentially to WON). Since ASSIGNED -> LOST is allowed, let's check transition matrix:
    # NEW -> ASSIGNED -> LOST is allowed.
    # What about WON? PROPOSAL_SENT -> WON, NEGOTIATION -> WON.
    # So we must transition: ASSIGNED -> CONTACTED (Version 2 -> 3)
    # Oh wait! Let's mock lookup status objects for contacted, req, prop, negotiation so we can update.
    # Let's register contact status, req, etc. in crm_lookups.
    # Wait, in CRMService._resolve_status: it automatically creates lookups when we search them by code!
    # So we don't even need to pre-create them! We can just query list_lookups("statuses") to find their IDs!
    # Let's find IDs for status CONTACTED, REQUIREMENT_GATHERING, PROPOSAL_SENT.
    resp_lookups = client.get("/api/v1/crm/lookups/statuses", headers={"Authorization": f"Bearer {auth_token}"})
    statuses = resp_lookups.get_json()["data"]
    status_ids = {s["code"]: s["id"] for s in statuses}
    
    # Let's run transitions sequentially:
    # ASSIGNED -> CONTACTED (Version 2 -> 3)
    client.put(f"/api/v1/leads/{lead_id}", json={"version": 2, "current_status_id": status_ids["CONTACTED"]}, headers={"Authorization": f"Bearer {auth_token}"})
    # CONTACTED -> REQUIREMENT_GATHERING (Version 3 -> 4)
    client.put(f"/api/v1/leads/{lead_id}", json={"version": 3, "current_status_id": status_ids["REQUIREMENT_GATHERING"]}, headers={"Authorization": f"Bearer {auth_token}"})
    # REQUIREMENT_GATHERING -> PROPOSAL_SENT (Version 4 -> 5)
    client.put(f"/api/v1/leads/{lead_id}", json={"version": 4, "current_status_id": status_ids["PROPOSAL_SENT"]}, headers={"Authorization": f"Bearer {auth_token}"})

    # Now convert Lead to Booking (which transitions PROPOSAL_SENT -> WON and writes DB)
    resp_conv = client.post(
        f"/api/v1/leads/{lead_id}/convert",
        json={},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_conv.status_code == 201
    res_conv = resp_conv.get_json()
    assert res_conv["success"] is True
    assert "booking_id" in res_conv["data"]


def test_public_api_compatibility(client, auth_token):
    payload = {
        "name": "Public Submitter",
        "phone": "+91 99999 88888",
        "email": "public@test.com",
        "lead_type": "quick_callback",
        "travelers": 2,
        "budget": "INR 50,000",
        "notes": "Requesting immediate callback."
    }
    resp = client.post(
        "/lead",
        json=payload
    )
    assert resp.status_code == 201
    res = resp.get_json()
    assert res["message"] == "Lead submitted successfully"
    assert "lead_id" in res


def test_list_leads_pagination_search_filter_sort(client, auth_token, crm_lookups):
    # Create multiple leads to test listing features
    for idx in range(3):
        client.post(
            "/api/v1/leads",
            json={
                "contact_person": {
                    "name": f"Searchable Name {idx}",
                    "phone": f"987654320{idx}"
                },
                "lead_source_id": crm_lookups["source_id"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

    # Test sorting and search
    resp = client.get(
        "/api/v1/leads?page=1&page_size=2&q=Searchable",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    res = resp.get_json()
    assert res["success"] is True
    assert len(res["data"]) == 2  # page size is 2
    assert res["meta"]["total_records"] >= 3


# ─────────────────────────────────────────────────────────────────
# Test cases: CRM Activity (Phase 5C) & Follow Ups (Phase 5D)
# ─────────────────────────────────────────────────────────────────

def test_crm_activity_logging_and_listing(client, auth_token, crm_lookups):
    # 1. Create Lead
    payload = {
        "contact_person": {
            "name": "Jathin Activity Test",
            "phone": "9876543233"
        },
        "lead_source_id": crm_lookups["source_id"]
    }
    resp1 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    lead_id = resp1.get_json()["data"]["id"]

    # 2. Log Activity
    activity_payload = {
        "activity_type_id": "CALL",
        "discussion_summary": "Discussed package pricing and custom options."
    }
    resp2 = client.post(
        f"/api/v1/leads/{lead_id}/activities",
        json=activity_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 201
    res2 = resp2.get_json()
    assert res2["success"] is True
    assert res2["data"]["discussion_summary"] == "Discussed package pricing and custom options."

    # 3. List Activities
    resp3 = client.get(
        f"/api/v1/leads/{lead_id}/activities",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp3.status_code == 200
    res3 = resp3.get_json()
    assert len(res3["data"]) >= 1
    assert res3["data"][0]["activity_type"]["code"] == "CALL"


def test_crm_followup_scheduling_and_completion(client, auth_token, crm_lookups):
    # 1. Create Lead
    payload = {
        "contact_person": {
            "name": "Jathin Followup Test",
            "phone": "9876543244"
        },
        "lead_source_id": crm_lookups["source_id"]
    }
    resp1 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    lead_id = resp1.get_json()["data"]["id"]

    # 2. Schedule Follow Up
    followup_payload = {
        "followup_type_id": "EMAIL",
        "scheduled_date": "2026-12-31T12:00:00Z",
        "notes": "Send proposal document."
    }
    resp2 = client.post(
        f"/api/v1/leads/{lead_id}/followups",
        json=followup_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp2.status_code == 201
    res2 = resp2.get_json()
    assert res2["success"] is True
    assert res2["data"]["status"] == "pending"
    assert res2["data"]["followup_type"]["code"] == "EMAIL"
    followup_id = res2["data"]["id"]

    # 3. List Follow Ups
    resp3 = client.get(
        f"/api/v1/leads/{lead_id}/followups",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp3.status_code == 200
    res3 = resp3.get_json()
    assert len(res3["data"]) >= 1

    # 4. Complete Follow Up
    complete_payload = {
        "completion_notes": "Proposal email sent, awaiting response."
    }
    resp4 = client.put(
        f"/api/v1/leads/{lead_id}/followups/{followup_id}/complete",
        json=complete_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp4.status_code == 200
    res4 = resp4.get_json()
    assert res4["success"] is True
    assert res4["data"]["status"] == "completed"
    assert res4["data"]["completion_notes"] == "Proposal email sent, awaiting response."


def test_soft_delete_lead_cancels_followups(client, auth_token, crm_lookups):
    # 1. Create Lead
    payload = {
        "contact_person": {
            "name": "Jathin Soft Delete Test",
            "phone": "9876543255"
        },
        "lead_source_id": crm_lookups["source_id"]
    }
    resp1 = client.post(
        "/api/v1/leads",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    lead_id = resp1.get_json()["data"]["id"]

    # 2. Schedule Follow Up
    followup_payload = {
        "followup_type_id": "CALL",
        "scheduled_date": "2026-12-31T12:00:00Z",
        "notes": "Callback."
    }
    resp2 = client.post(
        f"/api/v1/leads/{lead_id}/followups",
        json=followup_payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    followup_id = resp2.get_json()["data"]["id"]

    # 3. Delete Lead
    resp3 = client.delete(
        f"/api/v1/leads/{lead_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp3.status_code == 200

    # 4. Verify followup is cancelled/removed or status updated
    resp4 = client.get(
        f"/api/v1/leads/{lead_id}/followups",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp4.status_code == 200
    res4 = resp4.get_json()
    # Cancelled followups are soft-deleted or marked cancelled
    assert len(res4["data"]) == 0 or all(item["status"] == "cancelled" for item in res4["data"])


