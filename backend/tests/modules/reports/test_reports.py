import pytest
import uuid
from datetime import datetime, timezone, date, timedelta
from flask_jwt_extended import create_access_token
from unittest.mock import patch, MagicMock

from app.core.startup import create_app
from app.core.extensions import db, bcrypt
from app.models import (
    UserAccount, TeamMember, Role, Lead, LeadStatus, LeadSource, Proposal,
    ProposalStatus, Booking, BookingStatus, PaymentSchedule,
    PaymentStatus, Payment, Expense, Refund, RefundStatus, ReportJob
)
from app.modules.reports.service import ReportsService
from app.modules.reports.repository import FinanceReportRepository

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
def mock_s3():
    with patch("boto3.client") as mock_client:
        s3 = MagicMock()
        s3.generate_presigned_url.return_value = "https://mock-r2-cdn.amigos.com/reports/mock.csv"
        mock_client.return_value = s3
        yield s3

@pytest.fixture
def user_roles(app):
    with app.app_context():
        admin_role = Role(name="Admin", code="ADMIN", is_system=True)
        staff_role = Role(name="Staff", code="STAFF", is_system=True)
        db.session.add_all([admin_role, staff_role])
        db.session.commit()
        return {"ADMIN": admin_role.id, "STAFF": staff_role.id}

@pytest.fixture
def admin_token(app, user_roles):
    with app.app_context():
        tm = TeamMember(
            first_name="Admin", display_name="Admin User",
            official_email="admin@test.com", phone="1234567890",
            role_id=user_roles["ADMIN"]
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id, username="admin@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": ["reports.finance.read", "reports.crm.read", "reports.bookings.read", "reports.customer.read", "reports.operations.read", "reports.vendor-payments.read", "admin"], "role": "Admin"}
        )
        return token, tm.id

@pytest.fixture
def staff_token(app, user_roles):
    """Token with only CRM report access"""
    with app.app_context():
        tm = TeamMember(
            first_name="Sales", display_name="Sales Exec",
            official_email="sales@test.com", phone="9988776655",
            role_id=user_roles["STAFF"]
        )
        db.session.add(tm)
        db.session.flush()

        user = UserAccount(
            team_member_id=tm.id, username="sales@test.com",
            password_hash=bcrypt.generate_password_hash("password123").decode(),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"permissions": ["reports.crm.read"], "role": "Staff"}
        )
        return token, tm.id

@pytest.fixture
def seed_data(app):
    with app.app_context():
        # Seed statuses
        status_new = LeadStatus(code="NEW", name="New")
        b_status_confirmed = BookingStatus(code="CONFIRMED", name="Confirmed")
        p_status_verified = PaymentStatus(code="VERIFIED", name="Verified")
        ref_status_completed = RefundStatus(code="COMPLETED", name="Completed")
        db.session.add_all([status_new, b_status_confirmed, p_status_verified, ref_status_completed])
        db.session.flush()

        # Seed Lead Source
        source = LeadSource(code="GOOGLE", name="Google Forms")
        db.session.add(source)
        db.session.flush()

        # Seed Leads & Bookings
        lead = Lead(
            lead_number="L101", lead_source_id=source.id,
            contact_person_id=uuid.uuid4(), current_status_id=status_new.id,
            traveler_count=10
        )
        db.session.add(lead)

        booking = Booking(
            booking_number="B101", booking_type_id=uuid.uuid4(),
            booking_source_id=uuid.uuid4(), customer_id=uuid.uuid4(),
            booking_status_id=b_status_confirmed.id, booking_date=date.today(),
            trip_start_date=date.today() + timedelta(days=10),
            trip_end_date=date.today() + timedelta(days=15),
            total_travelers=10, total_amount=5000.00
        )
        db.session.add(booking)

        # Seed Payment
        payment = Payment(
            booking_id=uuid.uuid4(), payment_date=date.today(), amount=1500.00,
            payment_method_id=uuid.uuid4(), payment_status_id=p_status_verified.id,
            payment_type_id=uuid.uuid4()
        )
        db.session.add(payment)

        # Seed Expense
        expense = Expense(
            booking_id=uuid.uuid4(), expense_category_id=uuid.uuid4(),
            expense_type_id=uuid.uuid4(), amount=300.00, expense_date=date.today()
        )
        db.session.add(expense)

        db.session.commit()

# --- TARGET TESTS ---

# 1. Happy path query JSON for reports
def test_sync_reports_json(client, admin_token, seed_data):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    today_str = date.today().isoformat()

    # Finance Profit/Loss report
    res = client.get(f"/api/v1/reports/finance?date_from={today_str}&date_to={today_str}", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert "booking_breakdown" in json_data["data"]

    # CRM Conversion report
    res = client.get(f"/api/v1/reports/crm?date_from={today_str}&date_to={today_str}", headers=headers)
    assert res.status_code == 200
    assert "total_leads_created" in res.get_json()["data"]

    # Booking Trends report
    res = client.get(f"/api/v1/reports/bookings?date_from={today_str}&date_to={today_str}", headers=headers)
    assert res.status_code == 200
    assert "total_bookings" in res.get_json()["data"]

    # Customer History report
    res = client.get(f"/api/v1/reports/customer?date_from={today_str}&date_to={today_str}", headers=headers)
    assert res.status_code == 200
    assert "total_unique_customers" in res.get_json()["data"]

    # Operations Efficiency report
    res = client.get(f"/api/v1/reports/operations?date_from={today_str}&date_to={today_str}", headers=headers)
    assert res.status_code == 200
    assert "total_trip_plans_analyzed" in res.get_json()["data"]

    # Vendor Payments report
    res = client.get(f"/api/v1/reports/vendor-payments?date_from={today_str}&date_to={today_str}", headers=headers)
    assert res.status_code == 200
    assert "total_vendor_allocations" in res.get_json()["data"]


# 2. Reject invalid date ranges
def test_reject_invalid_date_range(client, admin_token):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # date_from > date_to
    res = client.get("/api/v1/reports/finance?date_from=2026-12-31&date_to=2026-01-01", headers=headers)
    assert res.status_code == 422
    assert res.get_json()["code"] == "INVALID_DATE_RANGE"


# 3. Reject too wide date range (> 2 years)
def test_reject_too_wide_date_range(client, admin_token):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Range is 3 years
    res = client.get("/api/v1/reports/finance?date_from=2026-01-01&date_to=2029-01-01", headers=headers)
    assert res.status_code == 422
    assert res.get_json()["code"] == "REPORT_DATE_RANGE_TOO_WIDE"


# 4. Validation on page parameter
def test_reject_invalid_page_params(client, admin_token):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/reports/finance?date_from=2026-01-01&date_to=2026-02-01&page=0", headers=headers)
    assert res.status_code == 422


# 5. RBAC security permissions rejection
def test_rbac_rejection(client, staff_token):
    token, _ = staff_token # staff has only reports.crm.read
    headers = {"Authorization": f"Bearer {token}"}
    today_str = date.today().isoformat()
    
    # Finance report requires reports.finance.read
    res = client.get(f"/api/v1/reports/finance?date_from={today_str}&date_to={today_str}", headers=headers)
    assert res.status_code == 403


# 6. Row-level security check compilation
def test_rls_scoping_behavior(app):
    with app.app_context():
        service = ReportsService()
        
        # Admin gets no RLS filtering
        sales_rls, ops_rls = service._apply_rls_scoping(uuid.uuid4(), ["reports.crm.read", "admin"])
        assert sales_rls is None
        assert ops_rls is None

        # Sales executive gets filtered by their own actor ID
        sales_rls, ops_rls = service._apply_rls_scoping(uuid.UUID("4eef1037-b718-d26d-ca59-40bb91972ec3"), ["reports.crm.read"])
        assert sales_rls == uuid.UUID("4eef1037-b718-d26d-ca59-40bb91972ec3")
        assert ops_rls is None


# 7. Sync CSV export return format
def test_sync_csv_export(client, admin_token, seed_data):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    today_str = date.today().isoformat()

    res = client.get(f"/api/v1/reports/finance?date_from={today_str}&date_to={today_str}&format=csv", headers=headers)
    assert res.status_code == 200
    assert res.content_type == "text/csv; charset=utf-8"
    assert "attachment; filename=finance_report" in res.headers["Content-Disposition"]


# 8. Asynchronous background execution trigger
def test_async_export_trigger(client, admin_token, mock_s3):
    token, actor_id = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    today_str = date.today().isoformat()

    def sync_submit(fn, *args, **kwargs):
        fn(*args, **kwargs)
        return MagicMock()

    # Mock get_finance_report_data to return 505 rows, triggering the > 500 threshold for async
    with patch("app.modules.reports.service.executor.submit", side_effect=sync_submit):
        with patch.object(FinanceReportRepository, "get_finance_report_data", return_value=[{"booking_id": "test"} for _ in range(505)]):
            res = client.get(f"/api/v1/reports/finance?date_from={today_str}&date_to={today_str}", headers=headers)
            assert res.status_code == 202
            json_data = res.get_json()
            assert json_data["status"] == "accepted"
            assert json_data["data"]["status"] == "QUEUED"
            
            # Verify ReportJob is created in DB
            job_id = json_data["data"]["job_id"]
            job = db.session.get(ReportJob, uuid.UUID(job_id))
            assert job is not None


# 9. Retrieve job status
def test_get_job_status(client, admin_token):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    job_id = uuid.uuid4()

    # Create dummy job in db
    job = ReportJob(
        id=job_id, report_type="FINANCE_PL", status="PROCESSING",
        progress_percentage=50.0
    )
    db.session.add(job)
    db.session.commit()

    res = client.get(f"/api/v1/reports/jobs/{job_id}", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "PROCESSING"


# 10. Download endpoint returns R2 signed URL
def test_download_job_file_redirect(client, admin_token, mock_s3):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    job_id = uuid.uuid4()

    # Create completed job in db
    job = ReportJob(
        id=job_id, report_type="FINANCE_PL", status="COMPLETED",
        file_url="reports/finance/test.csv", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.session.add(job)
    db.session.commit()

    res = client.get(f"/api/v1/reports/jobs/{job_id}/download", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["download_url"] == "https://mock-r2-cdn.amigos.com/reports/mock.csv"
    assert mock_s3.generate_presigned_url.called


# 11. Expired job download rejection
def test_expired_download_rejection(client, admin_token):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    job_id = uuid.uuid4()

    # Create expired job in db
    job = ReportJob(
        id=job_id, report_type="FINANCE_PL", status="COMPLETED",
        file_url="reports/finance/test.csv", expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db.session.add(job)
    db.session.commit()

    res = client.get(f"/api/v1/reports/jobs/{job_id}/download", headers=headers)
    assert res.status_code == 410
    assert res.get_json()["code"] == "DOWNLOAD_EXPIRED"


# 12. Expired jobs cleaner task
def test_expired_jobs_cleanup(client, admin_token, mock_s3):
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    job_id = uuid.uuid4()

    # Create expired job in db
    job = ReportJob(
        id=job_id, report_type="FINANCE_PL", status="COMPLETED",
        file_url="reports/finance/expired.csv", expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db.session.add(job)
    db.session.commit()

    # Call cleanup endpoint (Admin only)
    res = client.post("/api/v1/reports/cleanup", headers=headers)
    assert res.status_code == 200
    assert "cleaned up 1 expired report" in res.get_json()["message"]

    # Verify R2 deletion call was made
    assert mock_s3.delete_object.called
    
    # Verify DB status updated
    updated_job = db.session.get(ReportJob, job_id)
    assert updated_job.status == "EXPIRED"
    assert updated_job.file_url is None
