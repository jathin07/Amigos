import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone, date
from unittest.mock import patch
from flask_jwt_extended import create_access_token
from sqlalchemy import select

from app.core.startup import create_app
from app.core.extensions import db, bcrypt
from app.models import (
    UserAccount, TeamMember, Role, Lead, LeadStatus, LeadSource,
    Proposal, ProposalStatus, ContactPerson, Booking, BookingStatus,
    BookingSource, BookingType, Traveler, Document, PaymentSchedule,
    BookingStatusHistory, Task, Customer
)
from app.domain.events import DomainEvent


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
    """Create a user with full booking and proposal permissions and return a JWT."""
    with app.app_context():
        role = Role(name="Booking Admin", code="BOOKING_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Booking",
            display_name="Booking Admin",
            official_email="booking@test.com",
            phone="9999999995",
            employee_code="BOOK01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="booking@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "booking.read",
                "booking.create",
                "booking.update",
                "booking.delete",
                "booking.confirm",
                "booking.cancel",
                "crm.convert",
                "proposal.read",
                "proposal.create",
                "proposal.update"
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
    """Seed necessary lookup tables and an active lead with a finalized proposal."""
    with app.app_context():
        # Proposal Statuses
        p_statuses = {}
        for code in ["DRAFT", "UNDER_DISCUSSION", "APPROVED", "WAITING_FOR_ADVANCE", "CONVERTED", "ARCHIVED"]:
            p_status = ProposalStatus(code=code, name=code.title().replace("_", " "))
            db.session.add(p_status)
            p_statuses[code] = p_status
        
        # Lead Statuses
        l_statuses = {}
        for code in ["NEW", "ASSIGNED", "CONTACTED", "REQUIREMENT_GATHERING", "PROPOSAL_SENT", "NEGOTIATION", "WON", "LOST"]:
            l_status = LeadStatus(code=code, name=code.title().replace("_", " "))
            db.session.add(l_status)
            l_statuses[code] = l_status

        # Lead Source
        source = LeadSource(code="SEO", name="Search Engine Optimization", is_active=True)
        db.session.add(source)
        db.session.flush()

        # Contact Person
        contact = ContactPerson(
            name="Alice Smith",
            email="alice@test.com",
            phone="9876543211",
            is_active=True
        )
        db.session.add(contact)
        db.session.flush()

        # Lead
        lead = Lead(
            lead_number="AM-LD-2026-00001",
            contact_person_id=contact.id,
            lead_source_id=source.id,
            current_status_id=l_statuses["PROPOSAL_SENT"].id,
            budget=Decimal("50000.00"),
            traveler_count=2,
            travel_start_date=date(2026, 8, 20),
            travel_end_date=date(2026, 8, 27)
        )
        db.session.add(lead)
        db.session.flush()

        # Finalized Proposal
        proposal = Proposal(
            lead_id=lead.id,
            version=1,
            proposal_title="Munnar Honeymoon Deluxe",
            price_per_person=Decimal("25000.00"),
            total_amount=Decimal("50000.00"),
            is_final=True,
            status_id=p_statuses["WAITING_FOR_ADVANCE"].id
        )
        db.session.add(proposal)

        # Draft Proposal
        draft_proposal = Proposal(
            lead_id=lead.id,
            version=2,
            proposal_title="Munnar Honeymoon Budget",
            price_per_person=Decimal("15000.00"),
            total_amount=Decimal("30000.00"),
            is_final=False,
            status_id=p_statuses["DRAFT"].id
        )
        db.session.add(draft_proposal)

        # Booking Statuses
        b_statuses = {}
        for code in ["WAITING_FOR_ADVANCE", "CONFIRMED", "PLANNING", "READY", "ONGOING", "COMPLETED", "CLOSED", "CANCELLED"]:
            b_status = BookingStatus(code=code, name=code.title().replace("_", " "), is_active=True)
            db.session.add(b_status)
            b_statuses[code] = b_status

        # Booking Sources & Types
        b_type = BookingType(code="INDIVIDUAL", name="Individual Booking", is_active=True)
        b_source = BookingSource(code="CRM_CONVERSION", name="CRM Conversion", is_active=True)
        db.session.add(b_type)
        db.session.add(b_source)

        # Inactive Coordinator (to test assignment guards)
        inactive_agent = TeamMember(
            first_name="Inactive",
            last_name="Agent",
            display_name="Inactive Agent",
            official_email="inactive@test.com",
            phone="9876543232",
            employee_code="INACT01",
            is_active=False
        )
        db.session.add(inactive_agent)

        db.session.commit()

        return {
            "lead_id": str(lead.id),
            "proposal_id": str(proposal.id),
            "draft_proposal_id": str(draft_proposal.id),
            "contact_id": str(contact.id),
            "inactive_agent_id": str(inactive_agent.id)
        }


# ─────────────────────────────────────────────────────────────────
# Test Cases
# ─────────────────────────────────────────────────────────────────

def test_create_booking_success(client, auth_token, test_data):
    payload = {
        "proposal_id": test_data["proposal_id"],
        "group_name": "Smith Honeymoon Group",
        "travelers": [
            {
                "name": "Jane Smith",
                "age": 28,
                "gender": "Female",
                "id_proof_type": "Passport",
                "id_proof_number": "L1234567",
                "emergency_contact": "9876543210",
                "is_group_leader": True
            },
            {
                "name": "John Smith",
                "age": 30,
                "gender": "Male",
                "is_group_leader": False
            }
        ],
        "installments": [
            {
                "installment_no": 1,
                "percentage": 50.00,
                "due_date": "2026-08-15",
                "remarks": "Advance deposit"
            },
            {
                "installment_no": 2,
                "percentage": 50.00,
                "due_date": "2026-09-15",
                "remarks": "Final payment"
            }
        ]
    }

    resp = client.post(
        "/api/v1/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 201
    res = resp.get_json()
    assert res["success"] is True
    assert res["data"]["booking_number"].startswith("AMT-")
    assert res["data"]["total_travelers"] == 2
    assert Decimal(res["data"]["total_amount"]) == Decimal("50000.00")
    assert res["data"]["status"]["code"] == "WAITING_FOR_ADVANCE"
    assert len(res["data"]["payment_schedule"]) == 2
    assert len(res["data"]["travelers"]) == 2
    assert res["data"]["snapshots"]["package_name"] == "Custom Trip"
    assert res["data"]["snapshots"]["trip_name"] == "Munnar Honeymoon Deluxe"


def test_create_booking_installments_sum_invalid(client, auth_token, test_data):
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 50.00, "due_date": "2026-08-15"},
            {"installment_no": 2, "percentage": 40.00, "due_date": "2026-09-15"}
        ]
    }
    resp = client.post(
        "/api/v1/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 400
    res = resp.get_json()
    assert res["error"]["code"] == "ERR_PAYMENT_PERCENT_INVALID"


def test_create_booking_proposal_not_finalized(client, auth_token, test_data):
    payload = {
        "proposal_id": test_data["draft_proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 100.00, "due_date": "2026-08-15"}
        ]
    }
    resp = client.post(
        "/api/v1/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 409
    res = resp.get_json()
    assert res["error"]["code"] == "ERR_PROPOSAL_NOT_FINALIZED"


def test_confirm_booking_success(client, auth_token, test_data):
    # Setup booking first
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 100.00, "due_date": "2026-08-15"}
        ]
    }
    resp_create = client.post(
        "/api/v1/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    booking_id = resp_create.get_json()["data"]["id"]

    # Retrieve coordinator agent ID
    with client.application.app_context():
        agent = db.session.scalar(select(TeamMember).where(TeamMember.employee_code == "BOOK01"))
        agent_id = str(agent.id)

    # Confirm booking
    resp_conf = client.post(
        f"/api/v1/bookings/{booking_id}/confirm",
        json={
            "row_version": 1,
            "trip_coordinator_team_member_id": agent_id,
            "notes": "Advance payment cleared."
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_conf.status_code == 200
    res = resp_conf.get_json()
    assert res["success"] is True
    assert res["data"]["status"]["code"] == "CONFIRMED"
    assert res["data"]["trip_coordinator"]["id"] == agent_id


def test_confirm_booking_invalid_transition(client, auth_token, test_data):
    # Setup booking
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 100.00, "due_date": "2026-08-15"}
        ]
    }
    resp_create = client.post("/api/v1/bookings", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    booking_id = resp_create.get_json()["data"]["id"]

    # Cancel booking first
    client.post(
        f"/api/v1/bookings/{booking_id}/cancel",
        json={"row_version": 1, "cancellation_reason": "Customer request"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Attempt to confirm cancelled booking (version is now 2)
    resp_conf = client.post(
        f"/api/v1/bookings/{booking_id}/confirm",
        json={
            "row_version": 2,
            "trip_coordinator_team_member_id": str(uuid.uuid4())
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_conf.status_code == 409
    res = resp_conf.get_json()
    assert res["error"]["code"] == "ERR_INVALID_STATUS_TRANSITION"


def test_cancel_booking_success(client, auth_token, test_data):
    # Setup booking
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 100.00, "due_date": "2026-08-15"}
        ]
    }
    resp_create = client.post("/api/v1/bookings", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    booking_id = resp_create.get_json()["data"]["id"]

    # Cancel
    resp_cancel = client.post(
        f"/api/v1/bookings/{booking_id}/cancel",
        json={
            "row_version": 1,
            "cancellation_reason": "Flight cancellation."
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_cancel.status_code == 200
    res = resp_cancel.get_json()
    assert res["data"]["status"]["code"] == "CANCELLED"


def test_add_traveler_success(client, auth_token, test_data):
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 100.00, "due_date": "2026-08-15"}
        ]
    }
    resp_create = client.post("/api/v1/bookings", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    booking_id = resp_create.get_json()["data"]["id"]

    # Add traveler
    resp_add = client.post(
        f"/api/v1/bookings/{booking_id}/travelers",
        json={
            "name": "Tom",
            "age": 25,
            "gender": "Male",
            "is_group_leader": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_add.status_code == 201
    res = resp_add.get_json()
    assert res["data"]["name"] == "Tom"
    
    # Check booking detail total travelers updated
    resp_detail = client.get(f"/api/v1/bookings/{booking_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert resp_detail.get_json()["data"]["total_travelers"] == 2


def test_update_traveler_success(client, auth_token, test_data):
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 100.00, "due_date": "2026-08-15"}
        ]
    }
    resp_create = client.post("/api/v1/bookings", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    booking_json = resp_create.get_json()["data"]
    booking_id = booking_json["id"]
    traveler_id = booking_json["travelers"][0]["id"]

    # Update traveler
    resp_up = client.put(
        f"/api/v1/bookings/{booking_id}/travelers/{traveler_id}",
        json={
            "name": "Jane Doe",
            "age": 29,
            "gender": "Female",
            "is_group_leader": True
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_up.status_code == 200
    res = resp_up.get_json()
    assert res["data"]["name"] == "Jane Doe"
    assert res["data"]["age"] == 29


def test_delete_traveler_success(client, auth_token, test_data):
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True},
            {"name": "Tom", "age": 25, "is_group_leader": False}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 100.00, "due_date": "2026-08-15"}
        ]
    }
    resp_create = client.post("/api/v1/bookings", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    booking_json = resp_create.get_json()["data"]
    booking_id = booking_json["id"]
    
    # Tom's traveler ID (not group leader)
    traveler_id = [t["id"] for t in booking_json["travelers"] if not t["is_group_leader"]][0]

    resp_del = client.delete(
        f"/api/v1/bookings/{booking_id}/travelers/{traveler_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_del.status_code == 204


def test_booking_concurrency_optimistic_lock(client, auth_token, test_data):
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 100.00, "due_date": "2026-08-15"}
        ]
    }
    resp_create = client.post("/api/v1/bookings", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
    booking_id = resp_create.get_json()["data"]["id"]

    # First update
    resp_up1 = client.put(
        f"/api/v1/bookings/{booking_id}",
        json={"row_version": 1, "group_name": "First Update Group"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_up1.status_code == 200

    # Second concurrent update using obsolete version 1
    resp_up2 = client.put(
        f"/api/v1/bookings/{booking_id}",
        json={"row_version": 1, "group_name": "Conflict Group"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp_up2.status_code == 409
    assert resp_up2.get_json()["error"]["code"] == "ERR_OPTIMISTIC_LOCK"


def test_convert_lead_to_booking_refactored(client, auth_token, test_data):
    # Call conversion route
    resp = client.post(
        f"/api/v1/leads/{test_data['lead_id']}/convert",
        json={},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 201
    res = resp.get_json()
    assert res["success"] is True
    assert "booking_id" in res["data"]
    booking_id = res["data"]["booking_id"]

    # Verify that the booking status is WAITING_FOR_ADVANCE and the aggregate is intact
    resp_detail = client.get(f"/api/v1/bookings/{booking_id}", headers={"Authorization": f"Bearer {auth_token}"})
    booking_detail = resp_detail.get_json()["data"]
    assert booking_detail["status"]["code"] == "WAITING_FOR_ADVANCE"
    assert len(booking_detail["travelers"]) == 1
    assert len(booking_detail["payment_schedule"]) == 1


def test_rollback_on_failed_installment_validation(client, auth_token, test_data):
    # Submit travelers list successfully but provide an invalid percentage installment schedule.
    # The transaction must roll back and NOT insert the Booking or any Travelers.
    payload = {
        "proposal_id": test_data["proposal_id"],
        "travelers": [
            {"name": "Jane Rollback", "age": 28, "is_group_leader": True}
        ],
        "installments": [
            {"installment_no": 1, "percentage": 99.00, "due_date": "2026-08-15"} # sum != 100
        ]
    }
    resp = client.post(
        "/api/v1/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 400
    
    # Query database to confirm no Booking or Travelers exist with that name
    with client.application.app_context():
        booking = db.session.scalar(select(Booking).where(Booking.package_name_snapshot == "Custom Trip"))
        assert booking is None
        traveler = db.session.scalar(select(Traveler).where(Traveler.name == "Jane Rollback"))
        assert traveler is None
