import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone, date
from flask_jwt_extended import create_access_token
from sqlalchemy import select

from app.core.startup import create_app
from app.core.extensions import db, bcrypt
from app.models import (
    UserAccount, TeamMember, Role, Booking, BookingStatus,
    BookingSource, BookingType, Destination, Vendor, VendorType,
    TripPlan, TripPlanStatus, TripDay, VendorAllocation, VendorAllocationStatus,
    Payment, PaymentStatus, PaymentMethod, PaymentType as ModelPaymentType,
    PaymentSchedule, VendorPayment, Expense, ExpenseCategory, ExpenseType,
    Refund, RefundStatus, Customer
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
    """Create a user with full finance permissions and return a JWT."""
    with app.app_context():
        role = Role(name="Finance Admin", code="FINANCE_ADMIN", is_system=True)
        db.session.add(role)
        db.session.flush()

        tm = TeamMember(
            first_name="Finance",
            display_name="Finance Exec",
            official_email="fin@test.com",
            phone="9999999992",
            employee_code="FIN01",
            role=role,
            is_active=True,
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id,
            username="fin@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": [
                "finance.payment.read",
                "finance.payment.create",
                "finance.payment.verify",
                "finance.vendor_payment.read",
                "finance.vendor_payment.create",
                "finance.expense.read",
                "finance.expense.create",
                "finance.expense.delete",
                "finance.refund.read",
                "finance.refund.create",
                "finance.profit_summary.read",
                "finance.close",
                "booking.confirm"
            ]},
        )
        return token

@pytest.fixture
def test_data(app):
    """Seed lookup tables, a booking, a vendor, and an allocation."""
    with app.app_context():
        # Setup Booking statuses
        b_statuses = {}
        for code in ["WAITING_FOR_ADVANCE", "CONFIRMED", "PLANNING", "READY", "COMPLETED", "CLOSED", "CANCELLED"]:
            status = BookingStatus(code=code, name=code.title())
            db.session.add(status)
            b_statuses[code] = status

        # Payment Statuses
        p_statuses = {}
        for code in ["PENDING", "RECEIVED", "VERIFIED", "FAILED", "PAID"]:
            status = PaymentStatus(code=code, name=code.title(), is_active=True)
            db.session.add(status)
            p_statuses[code] = status

        # Refund Statuses
        r_statuses = {}
        for code in ["REQUESTED", "APPROVED", "PROCESSED", "COMPLETED", "REJECTED", "FAILED"]:
            status = RefundStatus(code=code, name=code.title(), is_active=True)
            db.session.add(status)
            r_statuses[code] = status

        # Payment Methods
        pm_upi = PaymentMethod(code="UPI", name="UPI", is_active=True)
        pm_bank = PaymentMethod(code="BANK_TRANSFER", name="Bank Transfer", is_active=True)
        db.session.add(pm_upi)
        db.session.add(pm_bank)

        # Payment Types
        pt_advance = ModelPaymentType(code="ADVANCE", name="Advance", is_active=True)
        pt_partial = ModelPaymentType(code="PARTIAL", name="Partial", is_active=True)
        pt_final = ModelPaymentType(code="FINAL", name="Final", is_active=True)
        db.session.add(pt_advance)
        db.session.add(pt_partial)
        db.session.add(pt_final)

        # Expense categories & types
        ec_fuel = ExpenseCategory(code="FUEL", name="Fuel", is_active=True)
        ec_rooms = ExpenseCategory(code="ROOMS", name="Rooms", is_active=True)
        db.session.add(ec_fuel)
        db.session.add(ec_rooms)

        et_ops = ExpenseType(code="OPERATIONAL", name="Operational", is_active=True)
        db.session.add(et_ops)

        # Vendor allocation statuses
        va_statuses = {}
        for code in ["PENDING", "NEGOTIATING", "CONFIRMED", "LOCKED", "SETTLED", "FAILED"]:
            status = VendorAllocationStatus(code=code, name=code.title())
            db.session.add(status)
            va_statuses[code] = status

        # Trip Plan status
        tp_statuses = {}
        for code in ["PLANNING", "READY", "STARTED", "ONGOING", "COMPLETED", "CLOSED"]:
            status = TripPlanStatus(code=code, name=code.title())
            db.session.add(status)
            tp_statuses[code] = status

        db.session.flush()

        # Destination & Geography
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
        dest = Destination(
            code="MUNNAR", slug="munnar", name="Munnar",
            country_id=country.id, state_id=state.id, district_id=district.id,
            description="Hills", is_active=True
        )
        db.session.add(dest)

        # Vendor Type
        v_type = VendorType(code="HOTEL", name="Hotel", is_active=True)
        db.session.add(v_type)
        db.session.flush()

        # Vendor
        vendor = Vendor(
            vendor_name="Munnar Resort", email="munnar@test.com", phone="9876543210",
            vendor_type_id=v_type.id, gst_number="29AABCC1234D1Z2", address="Munnar", is_active=True
        )
        db.session.add(vendor)
        db.session.flush()

        # Team Coordinator
        role = Role(name="Coordinator", code="COORDINATOR")
        db.session.add(role)
        db.session.flush()
        coord = TeamMember(
            first_name="Sam", display_name="Sam", official_email="sam@test.com", phone="9876543210",
            role_id=role.id, employee_code="TM01", is_active=True
        )
        db.session.add(coord)
        db.session.flush()

        # Booking
        b_type = BookingType(code="INDIVIDUAL", name="Individual")
        b_source = BookingSource(code="CRM", name="CRM")
        db.session.add(b_type)
        db.session.add(b_source)
        db.session.flush()

        customer = Customer(customer_type="B2C", customer_since=date.today())
        db.session.add(customer)
        db.session.flush()

        booking = Booking(
            booking_number="AMT-2026-00001",
            booking_type_id=b_type.id,
            booking_source_id=b_source.id,
            booking_status_id=b_statuses["WAITING_FOR_ADVANCE"].id,
            customer_id=customer.id,
            booking_date=date.today(),
            trip_start_date=date.today(),
            trip_end_date=date.today(),
            total_travelers=2,
            total_amount=Decimal("50000.00"),
            trip_coordinator_team_member_id=coord.id,
            booking_created_at=datetime.now(timezone.utc)
        )
        db.session.add(booking)
        db.session.flush()

        # Payment Schedule (50% advance, 50% final)
        sched1 = PaymentSchedule(
            booking_id=booking.id, installment_no=1, due_date=date.today(),
            amount=Decimal("25000.00"), percentage=Decimal("50.00"),
            payment_status_id=db.session.scalar(select(PaymentStatus.id).where(PaymentStatus.code == "PENDING"))
        )
        sched2 = PaymentSchedule(
            booking_id=booking.id, installment_no=2, due_date=date.today(),
            amount=Decimal("25000.00"), percentage=Decimal("50.00"),
            payment_status_id=db.session.scalar(select(PaymentStatus.id).where(PaymentStatus.code == "PENDING"))
        )
        db.session.add(sched1)
        db.session.add(sched2)
        db.session.flush()

        # Trip Plan & Days (for vendor allocation check)
        plan = TripPlan(
            booking_id=booking.id, status_id=tp_statuses["PLANNING"].id,
            prepared_date=date.today(), is_final=True, row_version=1,
            prepared_by_team_member_id=coord.id
        )
        db.session.add(plan)
        db.session.flush()

        day = TripDay(trip_plan_id=plan.id, day_number=1)
        db.session.add(day)
        db.session.flush()

        # Vendor Allocation
        alloc = VendorAllocation(
            trip_day_id=day.id, vendor_id=vendor.id, service_name="Stay",
            service_type_id=v_type.id, service_date=date.today(),
            quantity=2, unit_price=Decimal("5000.00"), quoted_amount=Decimal("10000.00"),
            confirmed_price=Decimal("10000.00"), confirmed_by_team_member_id=coord.id,
            confirmed_at=datetime.now(timezone.utc),
            allocation_status_id=va_statuses["CONFIRMED"].id
        )
        db.session.add(alloc)
        db.session.commit()

        return {
            "booking_id": booking.id,
            "sched1_id": sched1.id,
            "sched2_id": sched2.id,
            "alloc_id": alloc.id,
            "vendor_id": vendor.id,
            "coord_id": coord.id,
            "pm_upi_id": pm_upi.id,
            "pm_bank_id": pm_bank.id,
            "pt_advance_id": pt_advance.id,
            "pt_final_id": pt_final.id,
            "ec_fuel_id": ec_fuel.id,
            "et_ops_id": et_ops.id,
            "b_statuses": b_statuses,
            "tp_statuses": tp_statuses,
            "plan_id": plan.id
        }

# ─────────────────────────────────────────────────────────────────
# Customer Payment Tests
# ─────────────────────────────────────────────────────────────────

def test_record_customer_payment_success(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "booking_id": str(test_data["booking_id"]),
        "payment_schedule_id": str(test_data["sched1_id"]),
        "payment_date": str(date.today()),
        "amount": 25000.00,
        "payment_method_id": str(test_data["pm_upi_id"]),
        "payment_type_id": str(test_data["pt_advance_id"]),
        "installment_no": 1,
        "transaction_reference": "TXN99988",
        "remarks": "Advance payment"
    }

    # Record first payment
    response = client.post("/api/v1/finance/payments", json=payload, headers=headers)
    assert response.status_code == 201
    payment = response.get_json()["data"]
    assert payment["amount"] == "25000.00"
    assert payment["payment_status"]["code"] == "RECEIVED"

    # Verify Booking auto-confirmed upon advance payment (ADVANCE_RECEIVED listener)
    with client.application.app_context():
        b = db.session.get(Booking, test_data["booking_id"])
        assert b.status.code == "CONFIRMED"

def test_record_customer_payment_overrun_and_duplicates(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 1. Record payment
    payload = {
        "booking_id": str(test_data["booking_id"]),
        "payment_date": str(date.today()),
        "amount": 30000.00,
        "payment_method_id": str(test_data["pm_upi_id"]),
        "payment_type_id": str(test_data["pt_advance_id"]),
        "transaction_reference": "TXN111"
    }
    res1 = client.post("/api/v1/finance/payments", json=payload, headers=headers)
    assert res1.status_code == 201

    # 2. Try recording duplicate transaction reference (checks idempotency/prevent duplicate reference rule)
    res_dup = client.post("/api/v1/finance/payments", json=payload, headers=headers)
    assert res_dup.status_code == 409
    assert res_dup.get_json()["error"]["code"] == "DUPLICATE_PAYMENT_REFERENCE"

    # 3. Try recording more than outstanding balance (30k paid, booking total is 50k, so max allowed is 20k. Trying 21k)
    payload_overrun = {
        "booking_id": str(test_data["booking_id"]),
        "payment_date": str(date.today()),
        "amount": 21000.00,
        "payment_method_id": str(test_data["pm_upi_id"]),
        "payment_type_id": str(test_data["pt_final_id"]),
        "transaction_reference": "TXN222"
    }
    res_overrun = client.post("/api/v1/finance/payments", json=payload_overrun, headers=headers)
    assert res_overrun.status_code == 400
    assert res_overrun.get_json()["error"]["code"] == "PAYMENT_EXCEEDS_OUTSTANDING"

def test_verify_customer_payment_flow(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "booking_id": str(test_data["booking_id"]),
        "payment_date": str(date.today()),
        "amount": 10000.00,
        "payment_method_id": str(test_data["pm_upi_id"]),
        "payment_type_id": str(test_data["pt_advance_id"])
    }
    res = client.post("/api/v1/finance/payments", json=payload, headers=headers)
    payment_id = res.get_json()["data"]["id"]

    # Verify payment (Admin only)
    verify_res = client.patch(
        f"/api/v1/finance/payments/{payment_id}/verify",
        json={"verification_notes": "Bank check cleared"},
        headers=headers
    )
    assert verify_res.status_code == 200
    assert verify_res.get_json()["data"]["payment_status"]["code"] == "VERIFIED"

    # Test idempotency (second verification does not error)
    verify_res2 = client.patch(
        f"/api/v1/finance/payments/{payment_id}/verify",
        json={"verification_notes": "Bank check cleared"},
        headers=headers
    )
    assert verify_res2.status_code == 200

# ─────────────────────────────────────────────────────────────────
# Vendor Payment Tests
# ─────────────────────────────────────────────────────────────────

def test_vendor_payment_flow(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 1. Record vendor payment (allocation price is 10,000)
    vp_payload = {
        "vendor_allocation_id": str(test_data["alloc_id"]),
        "payment_date": str(date.today()),
        "amount": 6000.00,
        "payment_method_id": str(test_data["pm_bank_id"]),
        "transaction_reference": "VNEFT1"
    }
    vp_res = client.post("/api/v1/finance/vendor-payments", json=vp_payload, headers=headers)
    assert vp_res.status_code == 201
    assert vp_res.get_json()["data"]["amount"] == "6000.00"

    # 2. Try duplicate payment
    vp_res_dup = client.post("/api/v1/finance/vendor-payments", json=vp_payload, headers=headers)
    assert vp_res_dup.status_code == 409
    assert vp_res_dup.get_json()["error"]["code"] == "DUPLICATE_VENDOR_PAYMENT"

    # 3. Try overrun check (trying to pay another 5000 when balance is 4000)
    vp_payload_overrun = {
        "vendor_allocation_id": str(test_data["alloc_id"]),
        "payment_date": str(date.today()),
        "amount": 5000.00,
        "payment_method_id": str(test_data["pm_bank_id"]),
        "transaction_reference": "VNEFT2"
    }
    vp_res_overrun = client.post("/api/v1/finance/vendor-payments", json=vp_payload_overrun, headers=headers)
    assert vp_res_overrun.status_code == 400
    assert vp_res_overrun.get_json()["error"]["code"] == "VENDOR_PAYMENT_EXCEEDS_BALANCE"

# ─────────────────────────────────────────────────────────────────
# Expense logging & Lock Rules
# ─────────────────────────────────────────────────────────────────

def test_expense_flow_and_finance_lock(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Log expense (happy path)
    exp_payload = {
        "booking_id": str(test_data["booking_id"]),
        "expense_category_id": str(test_data["ec_fuel_id"]),
        "expense_type_id": str(test_data["et_ops_id"]),
        "amount": 1500.00,
        "expense_date": str(date.today()),
        "expense_description": "Fuel refill Munnar"
    }
    exp_res = client.post("/api/v1/finance/expenses", json=exp_payload, headers=headers)
    assert exp_res.status_code == 201
    expense_id = exp_res.get_json()["data"]["id"]

    # 2. Transition Booking to COMPLETED (forces Finance Lock)
    with client.application.app_context():
        booking = db.session.get(Booking, test_data["booking_id"])
        completed_status = db.session.scalar(select(BookingStatus).where(BookingStatus.code == "COMPLETED"))
        booking.booking_status_id = completed_status.id
        db.session.add(booking)
        db.session.commit()

    # 3. Try to add expense during lock (should fail)
    exp_res_locked = client.post("/api/v1/finance/expenses", json=exp_payload, headers=headers)
    assert exp_res_locked.status_code == 409
    assert exp_res_locked.get_json()["error"]["code"] == "EXPENSE_LOCKED"

    # 4. Try to delete expense during lock (should fail)
    exp_del_locked = client.delete(f"/api/v1/finance/expenses/{expense_id}", headers=headers)
    assert exp_del_locked.status_code == 409
    assert exp_del_locked.get_json()["error"]["code"] == "EXPENSE_LOCKED"

    # 5. Try to add vendor payment during lock (should fail)
    vp_payload = {
        "vendor_allocation_id": str(test_data["alloc_id"]),
        "payment_date": str(date.today()),
        "amount": 1000.00,
        "payment_method_id": str(test_data["pm_bank_id"])
    }
    vp_res_locked = client.post("/api/v1/finance/vendor-payments", json=vp_payload, headers=headers)
    assert vp_res_locked.status_code == 409
    assert vp_res_locked.get_json()["error"]["code"] == "FINANCE_LOCKED"

    # 6. Try to record customer payment during lock (should succeed!)
    cust_payload = {
        "booking_id": str(test_data["booking_id"]),
        "payment_date": str(date.today()),
        "amount": 1000.00,
        "payment_method_id": str(test_data["pm_upi_id"]),
        "payment_type_id": str(test_data["pt_final_id"])
    }
    cust_res_locked = client.post("/api/v1/finance/payments", json=cust_payload, headers=headers)
    assert cust_res_locked.status_code == 201

# ─────────────────────────────────────────────────────────────────
# Refunds Tests
# ─────────────────────────────────────────────────────────────────

def test_refund_flow(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # First collect a payment of 30,000 to allow refunds
    payload = {
        "booking_id": str(test_data["booking_id"]),
        "payment_date": str(date.today()),
        "amount": 30000.00,
        "payment_method_id": str(test_data["pm_upi_id"]),
        "payment_type_id": str(test_data["pt_advance_id"])
    }
    client.post("/api/v1/finance/payments", json=payload, headers=headers)

    # 1. Apply refund of 10,000 (valid, cumulative <= 30k)
    refund_payload = {
        "booking_id": str(test_data["booking_id"]),
        "amount": 10000.00,
        "payment_method_id": str(test_data["pm_bank_id"]),
        "remarks": "Day 2 cancellation"
    }
    ref_res = client.post("/api/v1/finance/refunds", json=refund_payload, headers=headers)
    assert ref_res.status_code == 201
    refund_id = ref_res.get_json()["data"]["id"]

    # Approve refund
    transition_res = client.patch(
        f"/api/v1/finance/refunds/{refund_id}/status",
        json={"status": "APPROVED"},
        headers=headers
    )
    assert transition_res.status_code == 200

    # 2. Try applying refund of 25,000 (10k already requested/approved, total paid = 30k, so remaining max = 20k. 25k should fail)
    refund_payload_overrun = {
        "booking_id": str(test_data["booking_id"]),
        "amount": 25000.00,
        "payment_method_id": str(test_data["pm_bank_id"]),
        "remarks": "Overrun"
    }
    ref_res_overrun = client.post("/api/v1/finance/refunds", json=refund_payload_overrun, headers=headers)
    assert ref_res_overrun.status_code == 400
    assert ref_res_overrun.get_json()["error"]["code"] == "REFUND_EXCEEDS_PAID"

# ─────────────────────────────────────────────────────────────────
# Close Finance Gating & Profit Summary Tests
# ─────────────────────────────────────────────────────────────────

def test_close_finance_and_profit_summary(client, auth_token, test_data):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Settle vendor allocation first (while booking is not COMPLETED/locked)
    vp_payload = {
        "vendor_allocation_id": str(test_data["alloc_id"]),
        "payment_date": str(date.today()),
        "amount": 10000.00,
        "payment_method_id": str(test_data["pm_bank_id"]),
        "transaction_reference": "VNEFT_SETTLE"
    }
    vp_res = client.post("/api/v1/finance/vendor-payments", json=vp_payload, headers=headers)
    assert vp_res.status_code == 201

    # 2. Try to close finance (should fail since outstanding customer schedule is still pending, even though vendor is paid)
    close_res_fail = client.post(f"/api/v1/finance/bookings/{test_data['booking_id']}/close", headers=headers)
    assert close_res_fail.status_code == 409
    assert close_res_fail.get_json()["error"]["code"] == "PENDING_INSTALLMENTS_EXIST"

    # 3. Pay remaining balance (outstanding is 50k. Record 50k customer payment)
    cust_pay_payload = {
        "booking_id": str(test_data["booking_id"]),
        "payment_date": str(date.today()),
        "amount": 50000.00,
        "payment_method_id": str(test_data["pm_upi_id"]),
        "payment_type_id": str(test_data["pt_final_id"])
    }
    cust_res = client.post("/api/v1/finance/payments", json=cust_pay_payload, headers=headers)
    assert cust_res.status_code == 201

    # Also update schedule status to PAID (or let verify do it)
    with client.application.app_context():
        s1 = db.session.get(PaymentSchedule, test_data["sched1_id"])
        s2 = db.session.get(PaymentSchedule, test_data["sched2_id"])
        status_received = db.session.scalar(select(PaymentStatus).where(PaymentStatus.code == "RECEIVED"))
        s1.payment_status_id = status_received.id
        s2.payment_status_id = status_received.id
        db.session.add(s1)
        db.session.add(s2)
        db.session.commit()

    # 4. Now transition Booking status to COMPLETED (forces Finance Lock)
    with client.application.app_context():
        booking = db.session.get(Booking, test_data["booking_id"])
        completed_status = db.session.scalar(select(BookingStatus).where(BookingStatus.code == "COMPLETED"))
        booking.booking_status_id = completed_status.id
        db.session.add(booking)
        db.session.commit()

    # 5. Get Profit Summary & derived calculations
    ps_res = client.get(f"/api/v1/finance/bookings/{test_data['booking_id']}/profit-summary", headers=headers)
    assert ps_res.status_code == 200
    summary = ps_res.get_json()["data"]
    assert summary["total_amount"] == "50000.00"
    assert summary["total_paid"] == "50000.00"
    assert summary["vendor_cost"] == "10000.00"
    assert summary["vendor_amount_paid"] == "10000.00"
    assert summary["gross_profit"] == "40000.00" # Net Revenue (50k) - Total Cost (10k vendor) = 40k
    assert summary["profit_margin_percentage"] == "80.00"

    # 6. Now close finance (should succeed!)
    close_res = client.post(f"/api/v1/finance/bookings/{test_data['booking_id']}/close", headers=headers)
    assert close_res.status_code == 200
    assert close_res.get_json()["data"]["status"] == "Closed"
