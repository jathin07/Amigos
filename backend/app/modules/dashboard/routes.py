from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.modules.auth.permissions import permission_required, login_required
from .service import DashboardQueryService
from .schemas import (
    SummaryCardsResponseSchema,
    LeadPipelineResponseSchema,
    BookingPipelineResponseSchema,
    FinanceSummaryResponseSchema,
    UpcomingTripsResponseSchema,
    OperationsOverviewResponseSchema,
    MonthlyRevenueTrendResponseSchema
)

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/widgets/summary-cards", methods=["GET"])
@permission_required("dashboard.read")
def get_summary_cards():
    service = DashboardQueryService()
    try:
        data = service.get_summary_cards()
        return jsonify(SummaryCardsResponseSchema().dump(data)), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Dashboard summary cards could not be computed.",
            "code": "DASHBOARD_COMPUTE_ERROR",
            "details": str(e)
        }), 500

@dashboard_bp.route("/widgets/lead-pipeline", methods=["GET"])
@permission_required("dashboard.read")
def get_lead_pipeline():
    service = DashboardQueryService()
    try:
        data = service.get_lead_pipeline()
        return jsonify(LeadPipelineResponseSchema().dump(data)), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Lead pipeline funnel metrics could not be computed.",
            "code": "DASHBOARD_COMPUTE_ERROR",
            "details": str(e)
        }), 500

@dashboard_bp.route("/widgets/booking-pipeline", methods=["GET"])
@permission_required("dashboard.read")
def get_booking_pipeline():
    service = DashboardQueryService()
    try:
        data = service.get_booking_pipeline()
        return jsonify(BookingPipelineResponseSchema().dump(data)), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Booking pipeline metrics could not be computed.",
            "code": "DASHBOARD_COMPUTE_ERROR",
            "details": str(e)
        }), 500

@dashboard_bp.route("/widgets/finance-summary", methods=["GET"])
@permission_required("dashboard.read", "finance.read")
def get_finance_summary():
    service = DashboardQueryService()
    try:
        data = service.get_finance_summary()
        return jsonify(FinanceSummaryResponseSchema().dump(data)), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Finance summary statistics could not be computed.",
            "code": "DASHBOARD_COMPUTE_ERROR",
            "details": str(e)
        }), 500

@dashboard_bp.route("/widgets/upcoming-trips", methods=["GET"])
@permission_required("dashboard.read")
def get_upcoming_trips():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    
    if page <= 0 or page_size <= 0:
        return jsonify({
            "status": "error",
            "message": "Query parameters page and page_size must be positive integers.",
            "code": "VALIDATION_ERROR"
        }), 400

    service = DashboardQueryService()
    try:
        data = service.get_upcoming_trips(page, page_size)
        return jsonify(UpcomingTripsResponseSchema().dump(data)), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Upcoming trips list could not be computed.",
            "code": "DASHBOARD_COMPUTE_ERROR",
            "details": str(e)
        }), 500

@dashboard_bp.route("/widgets/operations-overview", methods=["GET"])
@permission_required("dashboard.read")
def get_operations_overview():
    service = DashboardQueryService()
    try:
        data = service.get_operations_overview()
        return jsonify(OperationsOverviewResponseSchema().dump(data)), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Operations overview workload metrics could not be computed.",
            "code": "DASHBOARD_COMPUTE_ERROR",
            "details": str(e)
        }), 500

@dashboard_bp.route("/widgets/revenue-trend", methods=["GET"])
@permission_required("dashboard.read", "finance.read")
def get_revenue_trend():
    service = DashboardQueryService()
    try:
        data = service.get_revenue_trend()
        return jsonify(MonthlyRevenueTrendResponseSchema().dump(data)), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Revenue trend statistics could not be computed.",
            "code": "DASHBOARD_COMPUTE_ERROR",
            "details": str(e)
        }), 500
