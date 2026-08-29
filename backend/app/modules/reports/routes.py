from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError
import uuid
from datetime import date

from app.modules.auth.permissions import permission_required, login_required
from app.core.extensions import db
from app.models import ReportJob
from .service import ReportsService
from .schemas import (
    ReportFilterSchema,
    ReportJobResponseSchema,
    AsyncJobInitiatedSchema,
    FinanceProfitLossReportResponseSchema,
    CRMConversionReportResponseSchema,
    BookingTrendsReportResponseSchema,
    CustomerHistoryReportResponseSchema,
    OperationsEfficiencyReportResponseSchema,
    VendorPaymentReportResponseSchema
)

reports_bp = Blueprint("reports", __name__)


def handle_validation_error(err: ValidationError):
    # Extract error message string to map specific analytical error codes
    msg_str = str(err.messages)
    code = "VALIDATION_ERROR"
    if "End date must be after start date" in msg_str:
        code = "INVALID_DATE_RANGE"
    elif "must not exceed 2 years" in msg_str:
        code = "REPORT_DATE_RANGE_TOO_WIDE"
    elif "format is not supported" in msg_str:
        code = "UNSUPPORTED_FORMAT"

    return jsonify({
        "status": "error",
        "message": err.messages,
        "code": code
    }), 422


@reports_bp.route("/finance", methods=["GET"])
@permission_required("reports.finance.read")
def get_finance_report():
    try:
        # Load and validate filters
        filters = ReportFilterSchema().load(request.args)
    except ValidationError as err:
        return handle_validation_error(err)

    service = ReportsService()
    date_from = filters["date_from"]
    date_to = filters["date_to"]
    team_member_id = filters.get("team_member_id")
    fmt = filters["format"]

    # In a real app we'd fetch the current logged-in identity UUID
    # For testing, we mock or read from a test header if needed, defaulting to a UUID
    actor_id = uuid.uuid4() 
    permissions = ["reports.finance.read"]

    # 1. Fetch breakdown to check row limit
    try:
        breakdown = service.finance_repo.get_finance_report_data(date_from, date_to, team_member_id)
        row_count = len(breakdown)

        # 2. Threshold check: if > 500 rows or format is explicitly csv and user triggered async
        if row_count > 500:
            job = service.initiate_export_job(
                "FINANCE_PL", date_from, date_to, team_member_id, actor_id,
                permissions, fmt, request.remote_addr
            )
            return jsonify(AsyncJobInitiatedSchema().dump({"data": job})), 202

        # 3. Synchronous JSON or CSV return
        report_data = service.generate_report_sync(
            "FINANCE_PL", date_from, date_to, team_member_id, actor_id, permissions
        )

        if fmt == "csv":
            # Stream CSV data
            generator = service.csv_exporter.export_generator(report_data["booking_breakdown"])
            headers = {"Content-Disposition": f"attachment; filename=finance_report_{date_from}_{date_to}.csv"}
            return Response(generator, mimetype="text/csv", headers=headers)

        return jsonify(FinanceProfitLossReportResponseSchema().dump({"data": report_data})), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Report generation failed. Please try again.",
            "code": "REPORT_GENERATION_FAILED",
            "details": str(e)
        }), 500


@reports_bp.route("/crm", methods=["GET"])
@permission_required("reports.crm.read")
def get_crm_report():
    try:
        filters = ReportFilterSchema().load(request.args)
    except ValidationError as err:
        return handle_validation_error(err)

    service = ReportsService()
    date_from = filters["date_from"]
    date_to = filters["date_to"]
    team_member_id = filters.get("team_member_id")
    fmt = filters["format"]

    actor_id = uuid.uuid4()
    permissions = ["reports.crm.read"]

    try:
        report_data = service.generate_report_sync(
            "CRM_CONVERSION", date_from, date_to, team_member_id, actor_id, permissions
        )

        if fmt == "csv":
            generator = service.csv_exporter.export_generator(report_data["team_member_breakdown"])
            headers = {"Content-Disposition": f"attachment; filename=crm_report_{date_from}_{date_to}.csv"}
            return Response(generator, mimetype="text/csv", headers=headers)

        return jsonify(CRMConversionReportResponseSchema().dump({"data": report_data})), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Report generation failed.",
            "code": "REPORT_GENERATION_FAILED",
            "details": str(e)
        }), 500


@reports_bp.route("/bookings", methods=["GET"])
@permission_required("reports.bookings.read")
def get_booking_report():
    try:
        filters = ReportFilterSchema().load(request.args)
    except ValidationError as err:
        return handle_validation_error(err)

    service = ReportsService()
    date_from = filters["date_from"]
    date_to = filters["date_to"]
    fmt = filters["format"]

    actor_id = uuid.uuid4()
    permissions = ["reports.bookings.read"]

    try:
        report_data = service.generate_report_sync(
            "BOOKING_TRENDS", date_from, date_to, None, actor_id, permissions
        )

        if fmt == "csv":
            generator = service.csv_exporter.export_generator(report_data["monthly_trends"])
            headers = {"Content-Disposition": f"attachment; filename=bookings_report_{date_from}_{date_to}.csv"}
            return Response(generator, mimetype="text/csv", headers=headers)

        return jsonify(BookingTrendsReportResponseSchema().dump({"data": report_data})), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Report generation failed.",
            "code": "REPORT_GENERATION_FAILED",
            "details": str(e)
        }), 500


@reports_bp.route("/customer", methods=["GET"])
@permission_required("reports.customer.read")
def get_customer_report():
    try:
        filters = ReportFilterSchema().load(request.args)
    except ValidationError as err:
        return handle_validation_error(err)

    service = ReportsService()
    date_from = filters["date_from"]
    date_to = filters["date_to"]
    fmt = filters["format"]

    actor_id = uuid.uuid4()
    permissions = ["reports.customer.read"]

    try:
        report_data = service.generate_report_sync(
            "CUSTOMER_HISTORY", date_from, date_to, None, actor_id, permissions
        )

        if fmt == "csv":
            generator = service.csv_exporter.export_generator(report_data["top_customers"])
            headers = {"Content-Disposition": f"attachment; filename=customer_report_{date_from}_{date_to}.csv"}
            return Response(generator, mimetype="text/csv", headers=headers)

        return jsonify(CustomerHistoryReportResponseSchema().dump({"data": report_data})), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Report generation failed.",
            "code": "REPORT_GENERATION_FAILED",
            "details": str(e)
        }), 500


@reports_bp.route("/operations", methods=["GET"])
@permission_required("reports.operations.read")
def get_operations_report():
    try:
        filters = ReportFilterSchema().load(request.args)
    except ValidationError as err:
        return handle_validation_error(err)

    service = ReportsService()
    date_from = filters["date_from"]
    date_to = filters["date_to"]
    fmt = filters["format"]

    actor_id = uuid.uuid4()
    permissions = ["reports.operations.read"]

    try:
        report_data = service.generate_report_sync(
            "OPERATIONS_EFFICIENCY", date_from, date_to, None, actor_id, permissions
        )

        if fmt == "csv":
            generator = service.csv_exporter.export_generator(report_data["coordinator_performance"])
            headers = {"Content-Disposition": f"attachment; filename=operations_report_{date_from}_{date_to}.csv"}
            return Response(generator, mimetype="text/csv", headers=headers)

        return jsonify(OperationsEfficiencyReportResponseSchema().dump({"data": report_data})), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Report generation failed.",
            "code": "REPORT_GENERATION_FAILED",
            "details": str(e)
        }), 500


@reports_bp.route("/vendor-payments", methods=["GET"])
@permission_required("reports.vendor-payments.read")
def get_vendor_report():
    try:
        filters = ReportFilterSchema().load(request.args)
    except ValidationError as err:
        return handle_validation_error(err)

    service = ReportsService()
    date_from = filters["date_from"]
    date_to = filters["date_to"]
    fmt = filters["format"]

    actor_id = uuid.uuid4()
    permissions = ["reports.vendor-payments.read"]

    try:
        report_data = service.generate_report_sync(
            "VENDOR_PAYMENTS", date_from, date_to, None, actor_id, permissions
        )

        if fmt == "csv":
            generator = service.csv_exporter.export_generator(report_data["vendor_breakdown"])
            headers = {"Content-Disposition": f"attachment; filename=vendor_report_{date_from}_{date_to}.csv"}
            return Response(generator, mimetype="text/csv", headers=headers)

        return jsonify(VendorPaymentReportResponseSchema().dump({"data": report_data})), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Report generation failed.",
            "code": "REPORT_GENERATION_FAILED",
            "details": str(e)
        }), 500


# --- Report Jobs / Secure Downloads ---

@reports_bp.route("/jobs/<uuid:job_id>", methods=["GET"])
@login_required()
def get_job_status(job_id):
    job = db.session.get(ReportJob, job_id)
    if not job:
        return jsonify({
            "status": "error",
            "message": "The requested report job could not be found.",
            "code": "EXPORT_NOT_FOUND"
        }), 404

    return jsonify(ReportJobResponseSchema().dump({"data": job})), 200


@reports_bp.route("/jobs/<uuid:job_id>/download", methods=["GET"])
@login_required()
def download_job_file(job_id):
    service = ReportsService()
    url = service.get_job_signed_download_url(job_id)

    if not url:
        return jsonify({
            "status": "error",
            "message": "The requested report job could not be found.",
            "code": "EXPORT_NOT_FOUND"
        }), 404

    if url == "EXPIRED":
        return jsonify({
            "status": "error",
            "message": "The generated export file has expired and is no longer available.",
            "code": "DOWNLOAD_EXPIRED"
        }), 410

    # Redirect client to secure, temporary R2 signed URL
    return jsonify({
        "status": "success",
        "download_url": url
    }), 200


@reports_bp.route("/cleanup", methods=["POST"])
@permission_required("admin")
def cleanup_expired_reports():
    """Trigger manual lifecycle cleanup of expired report files."""
    service = ReportsService()
    purged_count = service.cleanup_expired_report_jobs()
    return jsonify({
        "status": "success",
        "message": f"Successfully cleaned up {purged_count} expired report artifacts."
    }), 200
