import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone, date
from flask_jwt_extended import create_access_token
from sqlalchemy import select

from app.core.startup import create_app
from app.core.extensions import db, bcrypt
from app.models import (
    UserAccount, TeamMember, Role, Lead, LeadStatus, LeadSource,
    Proposal, ProposalStatus, ContactPerson, Booking, BookingStatus,
    BookingSource, BookingType, Destination, Vendor, VendorType,
    TripPlan, TripPlanStatus, TripDay, VendorAllocation, VendorAllocationStatus,
    Checklist, Task, TaskStatus, TaskPriority, Customer
)
from app.domain.events import DomainEvent
from app.workflow.engine import event_bus


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
    """Create a user with full operations permissions and return a JWT."""
    with app.app_context():
        role = Role(name="Operations Admin", code="OPERATIONS_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Ops",
            display_name="Ops Coordinator",
            official_email="ops@test.com",
            phone="9999999991",
            employee_code="OPS01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="ops@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "operations.read",
                "operations.create",
                "operations.update",
                "operations.lock",
                "operations.update_checklist",
                "booking.confirm"
            ]},
        )
        return token


@pytest.fixture
def test_data(app):
    """Seed necessary lookup tables and an active confirmed booking."""
    with app.app_context():
        # Statuses & priorities
        tp_statuses = {}
        for code in ["PLANNING", "READY", "STARTED", "ONGOING", "COMPLETED", "CLOSED"]:
            status = TripPlanStatus(code=code, name=code.title())
            db.session.add(status)
            tp_statuses[code] = status

        va_statuses = {}
        for code in ["PENDING", "NEGOTIATING", "CONFIRMED", "LOCKED", "SETTLED", "FAILED"]:
            status = VendorAllocationStatus(code=code, name=code.title())
            db.session.add(status)
            va_statuses[code] = status

        t_statuses = {}
        for code in ["PENDING", "IN_PROGRESS", "DONE"]:
            status = TaskStatus(code=code, name=code.title())
            db.session.add(status)
            t_statuses[code] = status

        t_priorities = {}
        for code in ["LOW", "MEDIUM", "HIGH"]:
            prio = TaskPriority(code=code, name=code.title())
            db.session.add(prio)
            t_priorities[code] = prio

        b_statuses = {}
        for code in ["WAITING_FOR_ADVANCE", "CONFIRMED", "PLANNING", "READY", "COMPLETED", "CLOSED", "CANCELLED"]:
            status = BookingStatus(code=code, name=code.title())
            db.session.add(status)
            b_statuses[code] = status

        db.session.flush()

        from app.modules.master.country.models import Country
        from app.modules.master.state.models import State
        from app.modules.master.district.models import District

        country = Country(name="India", code="IN")
        db.session.add(country)
        db.session.flush()

        state = State(name="Kerala", code="KL", country_id=country.id)
        db.session.add(state)
        db.session.flush()

        district = District(name="Idukki", code="UK", state_id=state.id)
        db.session.add(district)
        db.session.flush()

        # Destination
        dest = Destination(
            code="MUNNAR",
            slug="munnar",
            name="Munnar",
            country_id=country.id,
            state_id=state.id,
            district_id=district.id,
            description="Beautiful hills",
            is_active=True
        )
        db.session.add(dest)

        # Vendor Type
        v_type = VendorType(code="HOTEL", name="Hotel Stay", is_active=True)
        db.session.add(v_type)

        # Team Member (Coordinator)
        role = Role(name="Trip Coordinator", code="COORDINATOR")
        db.session.add(role)
        db.session.flush()
        coord = TeamMember(
            first_name="Sam",
            display_name="Sam",
            official_email="sam@test.com",
            phone="9876543210",
            role_id=role.id,
            employee_code="TM01",
            is_active=True
        )
        db.session.add(coord)
        db.session.flush()

        # Vendor
        vendor = Vendor(
            vendor_name="Munnar Deluxe Resort",
            email="munnar@test.com",
            phone="9988776655",
            vendor_type_id=v_type.id,
            gst_number="29AABCC1234D1Z2",
            address="Munnar Hills, Kerala",
            is_active=True
        )
        db.session.add(vendor)
        db.session.flush()

        # Booking
        b_type = BookingType(code="INDIVIDUAL", name="Individual")
        b_source = BookingSource(code="CRM", name="CRM")
        db.session.add(b_type)
        db.session.add(b_source)
        db.session.flush()

        customer = Customer(
            customer_type="B2C",
            customer_since=date.today()
        )
        db.session.add(customer)
        db.session.flush()

        booking = Booking(
            booking_number="AMT-2026-00001",
            booking_type_id=b_type.id,
            booking_source_id=b_source.id,
            booking_status_id=b_statuses["CONFIRMED"].id,
            customer_id=customer.id,
            booking_date=date.today(),
            trip_start_date=date(2026, 8, 20),
            trip_end_date=date(2026, 8, 22),
            total_travelers=2,
            total_amount=Decimal("50000.00"),
            trip_coordinator_team_member_id=coord.id,
            booking_created_at=datetime.now(timezone.utc)
        )
        db.session.add(booking)
        db.session.commit()

        return {
            "booking_id": booking.id,
            "vendor_id": vendor.id,
            "vendor_type_id": v_type.id,
            "coord_id": coord.id,
            "dest_id": dest.id,
            "tp_statuses": tp_statuses,
            "va_statuses": va_statuses,
            "t_statuses": t_statuses,
            "t_priorities": t_priorities
        }


# ─────────────────────────────────────────────────────────────────
# TripPlan Tests
# ─────────────────────────────────────────────────────────────────

def test_create_trip_plan_success(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "booking_id": str(test_data["booking_id"]),
        "prepared_date": "2026-08-03",
        "notes": "Initial draft itinerary plan"
    }
    response = client.post("/api/v1/operations/trip-plans", json=payload, headers=headers)
    assert response.status_code == 201
    res_data = response.get_json()["data"]
    assert res_data["is_final"] is True
    assert res_data["status"] == "PLANNING"
    # Duration was 3 days (Aug 20 to 22), so 3 TripDays should be scaffolded
    assert len(res_data["trip_days"]) == 3


def test_create_trip_plan_duplicate_fails(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "booking_id": str(test_data["booking_id"]),
        "prepared_date": "2026-08-03"
    }
    response1 = client.post("/api/v1/operations/trip-plans", json=payload, headers=headers)
    assert response1.status_code == 201

    # Second one should fail due to uniqueness index
    response2 = client.post("/api/v1/operations/trip-plans", json=payload, headers=headers)
    assert response2.status_code == 409
    assert response2.get_json()["error"]["code"] == "TRIP_PLAN_ALREADY_EXISTS"


# ─────────────────────────────────────────────────────────────────
# VendorAllocation & Checklist Tests
# ─────────────────────────────────────────────────────────────────

def test_vendor_allocation_flow(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Create Trip Plan
    plan_payload = {
        "booking_id": str(test_data["booking_id"]),
        "prepared_date": "2026-08-03"
    }
    plan_res = client.post("/api/v1/operations/trip-plans", json=plan_payload, headers=headers).get_json()["data"]
    plan_id = plan_res["id"]
    day_id = plan_res["trip_days"][0]["id"]

    # 2. Add Vendor Allocation
    alloc_payload = {
        "vendor_id": str(test_data["vendor_id"]),
        "service_name": "Premium Suite Room Stay",
        "service_type_id": str(test_data["vendor_type_id"]),
        "service_date": "2026-08-20",
        "quantity": 2,
        "unit_price": 5000.00
    }
    alloc_res = client.post(
        f"/api/v1/operations/trip-plans/{plan_id}/days/{day_id}/allocations",
        json=alloc_payload,
        headers=headers
    )
    assert alloc_res.status_code == 201
    alloc_data = alloc_res.get_json()["data"]
    assert alloc_data["quoted_amount"] == "10000.00"
    assert alloc_data["allocation_status"] == "PENDING"
    alloc_id = alloc_data["id"]

    # 3. Confirm Allocation (overrun check: quoted=10k, max confirm = 11k)
    confirm_res = client.post(
        f"/api/v1/operations/allocations/{alloc_id}/confirm",
        json={"confirmed_price": 12000.00}, # 20% overrun - should fail
        headers=headers
    )
    assert confirm_res.status_code == 409
    assert confirm_res.get_json()["error"]["code"] == "ALLOCATION_PRICE_OVERRUN"

    # Confirm with acceptable price
    confirm_res2 = client.post(
        f"/api/v1/operations/allocations/{alloc_id}/confirm",
        json={"confirmed_price": 10500.00}, # 5% overrun - allowed
        headers=headers
    )
    assert confirm_res2.status_code == 200
    confirm_data = confirm_res2.get_json()["data"]
    assert confirm_data["confirmed_price"] == "10500.00"
    assert confirm_data["allocation_status"] == "CONFIRMED"

    # 4. Lock Allocation
    lock_res = client.post(
        f"/api/v1/operations/allocations/{alloc_id}/lock",
        headers=headers
    )
    assert lock_res.status_code == 200
    assert lock_res.get_json()["data"]["is_locked"] is True


def test_complete_trip_gating_checklist(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Trigger BookingConfirmed subscription directly or create TripPlan & checklists
    # We will trigger the event handler to verify subscription works
    event_bus.publish(DomainEvent.BOOKING_CONFIRMED, {"booking_id": str(test_data["booking_id"])})

    # Retrieve TripPlan created by event subscription
    tp_res = client.get(f"/api/v1/operations/trip-plans", headers=headers).get_json()["data"]
    assert len(tp_res) == 1
    plan_id = tp_res[0]["id"]

    # Retrieve checklists seeded by event subscriber
    chk_res = client.get(f"/api/v1/operations/trip-plans/{plan_id}/checklist", headers=headers).get_json()["data"]
    assert len(chk_res["items"]) == 3
    assert chk_res["completion_rate"] == "0.00"

    # 2. Try to complete trip -> should fail (checklist rate is 0%, open allocations not locked)
    complete_res = client.post(
        f"/api/v1/operations/trip-plans/{plan_id}/complete",
        json={"notes": "Finished"},
        headers=headers
    )
    assert complete_res.status_code == 409
    assert complete_res.get_json()["error"]["code"] in ["CHECKLIST_INCOMPLETE", "UNCONFIRMED_ALLOCATIONS"]

    # 3. Mark all checklists complete
    for item in chk_res["items"]:
        client.patch(
            f"/api/v1/operations/trip-plans/{plan_id}/checklist/{item['id']}",
            json={"is_completed": True},
            headers=headers
        )

    # Re-retrieve completion validation
    chk_res2 = client.get(f"/api/v1/operations/trip-plans/{plan_id}/checklist", headers=headers).get_json()["data"]
    assert chk_res2["completion_rate"] == "100.00"


# ─────────────────────────────────────────────────────────────────
# Task Operations Tests
# ─────────────────────────────────────────────────────────────────

def test_task_operations_flow(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Query lookups inside the active session
    prio_high = db.session.scalar(select(TaskPriority).where(TaskPriority.code == "HIGH"))
    status_pending = db.session.scalar(select(TaskStatus).where(TaskStatus.code == "PENDING"))
    status_in_progress = db.session.scalar(select(TaskStatus).where(TaskStatus.code == "IN_PROGRESS"))
    status_done = db.session.scalar(select(TaskStatus).where(TaskStatus.code == "DONE"))

    # 1. Create Task
    task_payload = {
        "booking_id": str(test_data["booking_id"]),
        "assigned_to_team_member_id": str(test_data["coord_id"]),
        "title": "Book resort rooms",
        "description": "Double check Munnar room availability",
        "priority_id": str(prio_high.id),
        "task_status_id": str(status_pending.id),
        "due_date": "2026-08-10",
        "estimated_hours": 2.5
    }
    task_res = client.post("/api/v1/operations/tasks", json=task_payload, headers=headers)
    assert task_res.status_code == 201
    task_data = task_res.get_json()["data"]
    assert task_data["title"] == "Book resort rooms"
    assert task_data["priority"] == "HIGH"
    task_id = task_data["id"]

    # 2. Update status to IN_PROGRESS
    update_res = client.patch(
        f"/api/v1/operations/tasks/{task_id}/status",
        json={"task_status_id": str(status_in_progress.id)},
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.get_json()["data"]["status"] == "IN_PROGRESS"

    # 3. Bulk status update
    bulk_res = client.patch(
        "/api/v1/operations/tasks/bulk-status",
        json={
            "task_ids": [task_id],
            "task_status_id": str(status_done.id)
        },
        headers=headers
    )
    assert bulk_res.status_code == 200
    assert bulk_res.get_json()["data"]["updated_count"] == 1

    # Verify task status is DONE
    task_done = client.get(f"/api/v1/operations/tasks/{task_id}", headers=headers).get_json()["data"]
    assert task_done["status"] == "DONE"
