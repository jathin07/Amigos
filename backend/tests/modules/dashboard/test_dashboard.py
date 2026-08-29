import pytest
import uuid
from datetime import datetime, timezone, date, timedelta
from flask_jwt_extended import create_access_token
from unittest.mock import patch

from app.core.startup import create_app
from app.core.extensions import db, bcrypt, cache
from app.models import (
    UserAccount, TeamMember, Role, Lead, LeadStatus, Proposal,
    ProposalStatus, Booking, BookingStatus, PaymentSchedule,
    PaymentStatus, Payment, Expense, Refund, RefundStatus
)
from app.domain.events import DomainEvent
from app.workflow.engine import event_bus

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        cache.clear()
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
def auth_token(app, user_roles):
    """Token with general dashboard.read permission"""
    with app.app_context():
        tm = TeamMember(
            first_name="Dash", display_name="Dash User",
            official_email="dash@test.com", phone="1234567890",
            role_id=user_roles["STAFF"]
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id, username="dash@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": ["dashboard.read"], "role": "Staff"}
        )
        return token, tm.id

@pytest.fixture
def finance_auth_token(app, user_roles):
    """Token with both dashboard.read and finance.read permissions"""
    with app.app_context():
        tm = TeamMember(
            first_name="Finance", display_name="Finance User",
            official_email="finance@test.com", phone="9876543210",
            role_id=user_roles["STAFF"]
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id, username="finance@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": ["dashboard.read", "finance.read"], "role": "Staff"}
        )
        return token, tm.id

@pytest.fixture
def test_data(app):
    """Seed test data for pipeline, finance, and operations metrics"""
    with app.app_context():
        # 1. Lead Statuses
        status_new = LeadStatus(code="NEW", name="New")
        status_won = LeadStatus(code="WON", name="Won")
        db.session.add_all([status_new, status_won])
        db.session.flush()

        # 2. Leads
        lead1 = Lead(
            lead_number="L001", lead_source_id=uuid.uuid4(),
            contact_person_id=uuid.uuid4(), current_status_id=status_new.id,
            traveler_count=5
        )
        db.session.add(lead1)

        # 3. Proposal status & Proposals
        p_status_draft = ProposalStatus(code="DRAFT", name="Draft")
        db.session.add(p_status_draft)
        db.session.flush()

        proposal1 = Proposal(
            lead_id=uuid.uuid4(), version=1, proposal_title="Plan A",
            status_id=p_status_draft.id
        )
        db.session.add(proposal1)

        # 4. Booking statuses & Bookings
        b_status_confirmed = BookingStatus(code="CONFIRMED", name="Confirmed")
        db.session.add(b_status_confirmed)
        db.session.flush()

        booking1 = Booking(
            booking_number="B001", booking_type_id=uuid.uuid4(),
            booking_source_id=uuid.uuid4(), customer_id=uuid.uuid4(),
            booking_status_id=b_status_confirmed.id, booking_date=date.today(),
            trip_start_date=date.today() + timedelta(days=5),
            trip_end_date=date.today() + timedelta(days=8),
            total_travelers=2, total_amount=1000.00
        )
        db.session.add(booking1)

        # 5. Payment schedule & verified payments
        pay_status_pending = PaymentStatus(code="PENDING", name="Pending")
        pay_status_verified = PaymentStatus(code="VERIFIED", name="Verified")
        db.session.add_all([pay_status_pending, pay_status_verified])
        db.session.flush()

        schedule1 = PaymentSchedule(
            booking_id=uuid.uuid4(), installment_no=1, due_date=date.today() - timedelta(days=2),
            amount=500.00, percentage=50.0, payment_status_id=pay_status_pending.id
        )
        db.session.add(schedule1)

        payment1 = Payment(
            booking_id=uuid.uuid4(), payment_date=date.today(), amount=500.00,
            payment_method_id=uuid.uuid4(), payment_status_id=pay_status_verified.id,
            payment_type_id=uuid.uuid4()
        )
        db.session.add(payment1)

        # 6. Expenses
        expense1 = Expense(
            booking_id=uuid.uuid4(), expense_category_id=uuid.uuid4(),
            expense_type_id=uuid.uuid4(), amount=100.00, expense_date=date.today()
        )
        db.session.add(expense1)

        # 7. Completed Refunds
        ref_status_completed = RefundStatus(code="COMPLETED", name="Completed")
        db.session.add(ref_status_completed)
        db.session.flush()

        refund1 = Refund(
            booking_id=uuid.uuid4(), refund_status_id=ref_status_completed.id,
            amount=50.00, refund_date=date.today(), payment_method_id=uuid.uuid4()
        )
        db.session.add(refund1)

        db.session.commit()

# ----------------- TEST CASES -----------------

# 1. Summary cards retrieval (happy path)
def test_get_summary_cards(client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/summary-cards", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["active_leads"] == 1
    assert json_data["data"]["open_proposals"] == 1
    assert json_data["data"]["confirmed_bookings"] == 1
    assert json_data["data"]["trips_today"] == 0
    assert json_data["data"]["outstanding_payments"] == 1
    assert json_data["data"]["revenue_this_month"] == 500.0
    assert json_data["data"]["profit_this_month"] == 400.0  # 500 revenue - 100 expense
    assert json_data["cache_status"] == "CACHE_MISS"

# 2. CRM lead pipeline funnel retrieval
def test_get_lead_pipeline(client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/lead-pipeline", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    # Verify won/lost/new statuses exist in the data funnel array
    new_stage = next(item for item in json_data["data"] if item["status"] == "NEW")
    assert new_stage["count"] == 1
    assert new_stage["percentage"] == 100.0
    assert new_stage["color"] == "#2196F3"

# 3. Booking pipeline funnel retrieval
def test_get_booking_pipeline(client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/booking-pipeline", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    confirmed_stage = next(item for item in json_data["data"] if item["status"] == "CONFIRMED")
    assert confirmed_stage["count"] == 1

# 4. Finance summary retrieval
def test_get_finance_summary(client, finance_auth_token, test_data):
    token, _ = finance_auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/finance-summary", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["data"]["collected"] == 500.0
    assert json_data["data"]["outstanding"] == 500.0
    assert json_data["data"]["expenses"] == 100.0
    assert json_data["data"]["refunds"] == 50.0
    assert json_data["data"]["net_profit"] == 350.0  # 500 collected - 100 expenses - 50 refunds
    assert json_data["data"]["gross_margin_percentage"] == 70.0  # 350 / 500 * 100

# 5. Paginated upcoming trips retrieval
def test_get_upcoming_trips(client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/upcoming-trips?page=1&page_size=5", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert len(json_data["data"]["upcoming_trips"]) == 1
    assert json_data["data"]["upcoming_trips"][0]["booking_number"] == "B001"
    assert json_data["data"]["pagination"]["page"] == 1
    assert json_data["data"]["pagination"]["page_size"] == 5

# 6. Operations overview retrieval
def test_get_operations_overview(client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/operations-overview", headers=headers)
    assert res.status_code == 200
    # No coordinator workload should return because no coordinator is currently active/assigned
    assert len(res.get_json()["data"]) == 0

# 7. Monthly revenue trend chart data retrieval
def test_get_revenue_trend(client, finance_auth_token, test_data):
    token, _ = finance_auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/revenue-trend", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert len(json_data["data"]["trend_months"]) == 6
    # This month should have 500 collected, 100 expense, 50 refund
    current_month_str = date.today().strftime("%Y-%m")
    current_month_data = next(item for item in json_data["data"]["trend_months"] if item["month"] == current_month_str)
    assert current_month_data["collected"] == 500.0
    assert current_month_data["expenses"] == 100.0
    assert current_month_data["profit"] == 350.0

# 8. Finance summary rejects if missing finance.read (RBAC)
def test_get_finance_summary_rbac(client, auth_token, test_data):
    token, _ = auth_token # general token without finance.read
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/finance-summary", headers=headers)
    assert res.status_code == 403

# 9. Revenue trend rejects if missing finance.read (RBAC)
def test_get_revenue_trend_rbac(client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/revenue-trend", headers=headers)
    assert res.status_code == 403

# 10. Upcoming trips rejects on invalid page parameters
def test_get_upcoming_trips_invalid_params(client, auth_token):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/upcoming-trips?page=-1", headers=headers)
    assert res.status_code == 400

# 11. Verify cache hit logic (returns status "CACHE_HIT")
def test_cache_hit_status(client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # First call - cache miss
    res1 = client.get("/api/v1/dashboard/widgets/summary-cards", headers=headers)
    assert res1.get_json()["cache_status"] == "CACHE_MISS"

    # Second call - cache hit
    res2 = client.get("/api/v1/dashboard/widgets/summary-cards", headers=headers)
    assert res2.get_json()["cache_status"] == "CACHE_HIT"

# 12. Verify cache invalidation triggers on event publication
def test_event_cache_invalidation(app, client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}

    # Populate cache
    client.get("/api/v1/dashboard/widgets/summary-cards", headers=headers)
    
    # Assert cached in Redis/memory cache
    cached_payload = cache.get("dashboard:v1:summary_cards")
    assert cached_payload is not None

    # Publish lead created event - should invalidate summary_cards and lead_pipeline
    with app.app_context():
        event_bus.publish(DomainEvent.LEAD_CREATED, {"lead_id": str(uuid.uuid4())})

    # Assert cache is cleared
    cached_payload_after = cache.get("dashboard:v1:summary_cards")
    assert cached_payload_after is None

# 13. Verify empty database returns zeroed/empty structures safely
def test_empty_database_responses(client, auth_token):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard/widgets/summary-cards", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["active_leads"] == 0
    assert res.get_json()["data"]["revenue_this_month"] == 0.0

# 14. Verify Redis connection failure fallback (returns DB_FALLBACK)
def test_cache_connection_failure_fallback(client, auth_token, test_data):
    token, _ = auth_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Mock cache.get to raise connection exception
    with patch("app.core.extensions.cache.get", side_effect=Exception("Redis Connection Refused")):
        res = client.get("/api/v1/dashboard/widgets/summary-cards", headers=headers)
        assert res.status_code == 200
        assert res.get_json()["cache_status"] == "DB_FALLBACK"

# 15. Verify that multiple events invalidate corresponding widgets only (selective invalidation)
def test_selective_cache_invalidation(app, client, finance_auth_token, test_data):
    token, _ = finance_auth_token
    headers = {"Authorization": f"Bearer {token}"}

    # Populate both summary cards and finance widgets
    client.get("/api/v1/dashboard/widgets/summary-cards", headers=headers)
    client.get("/api/v1/dashboard/widgets/finance-summary", headers=headers)

    assert cache.get("dashboard:v1:summary_cards") is not None
    assert cache.get("dashboard:v1:finance_summary") is not None

    # Publish task completed event - should NOT invalidate finance summary (only operations_overview)
    with app.app_context():
        event_bus.publish(DomainEvent.TASK_COMPLETED, {"task_id": str(uuid.uuid4())})

    # summary_cards and finance_summary cache should remain active
    assert cache.get("dashboard:v1:summary_cards") is not None
    assert cache.get("dashboard:v1:finance_summary") is not None

    # Publish payment verified event - should invalidate finance_summary and summary_cards
    with app.app_context():
        event_bus.publish(DomainEvent.PAYMENT_VERIFIED, {"payment_id": str(uuid.uuid4())})

    assert cache.get("dashboard:v1:summary_cards") is None
    assert cache.get("dashboard:v1:finance_summary") is None
