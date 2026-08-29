# 15 Report DTOs
## Analytical Business Reports — Request Filters and Response Summary Schemas

> **Module Type**: Read Model (Analytical, Strictly Read-Only)
> **Design Note**: Reports are distinct from Dashboard widgets. Reports operate on historical data ranges, support date filtering, and support both synchronous execution (< 500 rows) and asynchronous background export jobs (>= 501 rows) with secure file uploads to Cloudflare R2.
> **Security**: Role-Based Access Control (RBAC) and Row-Level Security (RLS) data scoping are strictly enforced for all analytical data access.

---

## Report Inventory

| Report | Endpoint | Output Formats | Min Role | RLS Data Scoping |
| :--- | :--- | :--- | :--- | :--- |
| Finance P&L Report | `GET /api/v1/reports/finance` | JSON, CSV, XLSX, PDF | Finance Executive, Admin | Full Org view (restricted to Finance) |
| CRM Conversion Report | `GET /api/v1/reports/crm` | JSON, CSV | Sales Executive, Admin | Sales Exec sees own leads; Admin sees all |
| Booking Trends Report | `GET /api/v1/reports/bookings` | JSON, CSV | Admin | Full Org view |
| Customer History Report | `GET /api/v1/reports/customer` | JSON, CSV | Sales Executive, Admin | Sales Exec sees own customers; Admin sees all |
| Operations Efficiency Report | `GET /api/v1/reports/operations` | JSON, CSV | Operations Executive, Admin | Coordinator sees assigned trips; Admin sees all |
| Vendor Payment Report | `GET /api/v1/reports/vendor-payments` | JSON, CSV | Finance Executive, Admin | Full Org view |

---

## 1. Shared Report Filter Query Parameters

All report endpoints support the following query parameters:

| Parameter | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| `date_from` | string | Yes | Format: ISO Date (`YYYY-MM-DD`). Must be before `date_to`. | `2026-01-01` |
| `date_to` | string | Yes | Format: ISO Date (`YYYY-MM-DD`). Max 2 years range from `date_from`. | `2026-12-31` |
| `team_member_id` | string | No | Format: UUID. Filter by specific coordinator/sales executive. | `8a0ba629-2608-5212-13c0-0448b6d1f4c2` |
| `booking_status` | string | No | Valid BookingStatus code. | `COMPLETED` |
| `format` | string | No | Enum: `json`, `csv`, `xlsx`, `pdf`. Default: `json`. | `csv` |
| `page` | integer | No | `>= 1`, Default: 1. | `1` |
| `per_page` | integer | No | 1–200, Default: 50. | `50` |
| `sort_by` | string | No | Sort column name (e.g. `booking_date`, `total_amount`). | `booking_date` |
| `sort_order` | string | No | Enum: `asc`, `desc`. Default: `desc`. | `desc` |

---

## 2. Asynchronous Export Job DTOs

When an export request exceeds the synchronous threshold (500 rows), the API initiates a background job and responds with a `ReportJob` status object and an HTTP status of `202 Accepted`.

### 2.1 Initiating Asynchronous Report (`202 Accepted` Response)
```json
{
  "status": "accepted",
  "message": "Report dataset exceeds synchronous execution limit. Export job queued.",
  "data": {
    "job_id": "4eef1037-b718-d26d-ca59-40bb91972ec3",
    "report_type": "FINANCE_PL",
    "status": "QUEUED",
    "progress_percentage": 0.0,
    "file_url": null,
    "expires_at": null,
    "created_at": "2026-08-03T21:35:00Z"
  }
}
```

### 2.2 Checking Export Job Status (`GET /api/v1/reports/jobs/<job_id>`)

**Response DTO (`ReportJobResponse`):**

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `job_id` | string | No | Unique UUID for the background export job. |
| `report_type` | string | No | Enum: `FINANCE_PL`, `CRM_CONVERSION`, `BOOKING_TRENDS`, `CUSTOMER_HISTORY`, `OPERATIONS_EFFICIENCY`, `VENDOR_PAYMENTS`. |
| `status` | string | No | Enum: `QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`. |
| `progress_percentage` | decimal | No | Current completion progress from `0.0` to `100.0`. |
| `file_url` | string | Yes | R2-hosted link (GET signed URL) when status is `COMPLETED`. |
| `expires_at` | string | Yes | ISO DateTime when the generated file is deleted (24 hours after completion). |
| `error_details` | string | Yes | Failure details if status is `FAILED`. |
| `row_count` | integer | Yes | Number of exported data rows. |
| `file_size_bytes` | integer | Yes | Generated file size. |
| `created_at` | string | No | ISO DateTime of job creation. |

```json
{
  "status": "success",
  "data": {
    "job_id": "4eef1037-b718-d26d-ca59-40bb91972ec3",
    "report_type": "FINANCE_PL",
    "status": "COMPLETED",
    "progress_percentage": 100.0,
    "file_url": "https://4eef1037b718d26dca5940bb91972ec3.r2.cloudflarestorage.com/reports/finance/report-4eef1037.csv?expires=1785856100&signature=...",
    "expires_at": "2026-08-04T21:35:00Z",
    "error_details": null,
    "row_count": 1845,
    "file_size_bytes": 382490,
    "created_at": "2026-08-03T21:35:00Z"
  }
}
```

---

## 3. Synchronous Report Response DTOs

### 3.1 `FinanceProfitLossReportResponse`
```json
{
  "status": "success",
  "data": {
    "report_period_from": "2026-01-01",
    "report_period_to": "2026-08-03",
    "total_bookings_analyzed": 48,
    "total_revenue": 4250000.00,
    "total_refunds": 85000.00,
    "net_revenue": 4165000.00,
    "total_vendor_costs": 2180000.00,
    "total_operational_expenses": 312000.00,
    "total_costs": 2492000.00,
    "gross_profit": 1673000.00,
    "profit_margin_percentage": 40.17,
    "outstanding_customer_balance": 312000.00,
    "pending_vendor_disbursements": 185000.00,
    "booking_breakdown": [
      {
        "booking_id": "uuid-booking-1",
        "booking_number": "AMT-2026-00001",
        "group_name": "Raj Enterprises Annual Trip",
        "trip_start_date": "2026-08-10",
        "total_amount": 85000.00,
        "revenue_collected": 60000.00,
        "vendor_cost": 38000.00,
        "operational_expense": 4500.00,
        "gross_profit": 17500.00,
        "profit_margin_percentage": 29.17,
        "status": "CONFIRMED"
      }
    ],
    "generated_at": "2026-08-03T21:35:00Z"
  }
}
```

### 3.2 `CRMConversionReportResponse`
```json
{
  "status": "success",
  "data": {
    "report_period_from": "2026-01-01",
    "report_period_to": "2026-08-03",
    "total_leads_created": 214,
    "total_leads_won": 48,
    "total_leads_lost": 32,
    "total_leads_active": 134,
    "conversion_rate_percentage": 60.00,
    "average_lead_age_days": 12.5,
    "average_deal_size": 88541.67,
    "lead_source_breakdown": [
      { "source": "Google Forms", "leads": 72, "won": 18, "conversion_rate": 25.00 },
      { "source": "Walk-in", "leads": 40, "won": 16, "conversion_rate": 40.00 }
    ],
    "team_member_breakdown": [
      { "team_member_id": "uuid-tm-1", "name": "Ravi Kumar", "leads_assigned": 80, "won": 22, "conversion_rate": 27.50 }
    ],
    "generated_at": "2026-08-03T21:35:00Z"
  }
}
```

### 3.3 `BookingTrendsReportResponse`
```json
{
  "status": "success",
  "data": {
    "report_period_from": "2026-01-01",
    "report_period_to": "2026-08-03",
    "total_bookings": 48,
    "total_travelers_served": 1842,
    "average_group_size": 38.4,
    "average_booking_value": 88541.67,
    "monthly_trends": [
      { "month": "2026-01", "bookings_created": 5, "bookings_completed": 3, "total_revenue": 412000.00 }
    ],
    "trip_type_breakdown": [
      { "trip_type": "College IV", "count": 18, "percentage": 37.50 }
    ],
    "top_destinations": [
      { "destination": "Coorg", "booking_count": 14, "percentage": 29.17 }
    ],
    "generated_at": "2026-08-03T21:35:00Z"
  }
}
```

### 3.4 `CustomerHistoryReportResponse`
```json
{
  "status": "success",
  "data": {
    "report_period_from": "2026-01-01",
    "report_period_to": "2026-08-03",
    "total_unique_customers": 42,
    "repeat_customers": 14,
    "repeat_customer_rate_percentage": 33.33,
    "top_customers": [
      {
        "customer_id": "uuid-customer-1",
        "customer_name": "Raj Enterprises",
        "total_bookings": 4,
        "total_revenue": 340000.00,
        "last_trip_date": "2026-07-15",
        "preferred_destinations": ["Coorg", "Ooty"]
      }
    ],
    "generated_at": "2026-08-03T21:35:00Z"
  }
}
```

### 3.5 `OperationsEfficiencyReportResponse`
```json
{
  "status": "success",
  "data": {
    "report_period_from": "2026-01-01",
    "report_period_to": "2026-08-03",
    "total_trip_plans_analyzed": 45,
    "average_checklist_completion_rate": 88.40,
    "trips_delayed_by_checklist": 3,
    "average_vendor_allocations_per_trip": 6.2,
    "vendor_settlement_rate_percentage": 76.50,
    "coordinator_performance": [
      {
        "coordinator_id": "uuid-tm-1",
        "coordinator_name": "Ravi Kumar",
        "trips_managed": 18,
        "average_checklist_completion": 94.40,
        "on_time_trips": 17,
        "delayed_trips": 1
      }
    ],
    "generated_at": "2026-08-03T21:35:00Z"
  }
}
```

### 3.6 `VendorPaymentReportResponse`
```json
{
  "status": "success",
  "data": {
    "report_period_from": "2026-01-01",
    "report_period_to": "2026-08-03",
    "total_vendor_allocations": 298,
    "total_quoted_value": 8420000.00,
    "total_confirmed_value": 7980000.00,
    "total_disbursed": 6100000.00,
    "total_pending": 1880000.00,
    "settlement_rate_percentage": 76.44,
    "vendor_breakdown": [
      {
        "vendor_id": "uuid-vendor-1",
        "vendor_name": "Hotel Coorg View",
        "total_allocations": 14,
        "total_confirmed_value": 840000.00,
        "total_paid": 780000.00,
        "balance_due": 60000.00,
        "settlement_rate": 92.86
      }
    ],
    "generated_at": "2026-08-03T21:35:00Z"
  }
}
```

---

## 4. Error Catalogue

| Error Code | HTTP Status | Trigger | Message |
| :--- | :--- | :--- | :--- |
| `INVALID_DATE_RANGE` | 422 | `date_to` is before or equal to `date_from` | Date range is invalid. End date must be after start date. |
| `REPORT_DATE_RANGE_TOO_WIDE` | 422 | Date range exceeds 2 years | Date range must not exceed 2 years. |
| `REPORT_TOO_LARGE` | 422 | Execution dataset exceeds system export limits. | Report size exceeds allowed limits. Try adding narrower filters. |
| `EXPORT_TIMEOUT` | 504 | Background generation task timed out. | The export generation timed out. Please try filtering for shorter periods. |
| `EXPORT_NOT_FOUND` | 404 | Checking status of nonexistent job ID. | The requested report job could not be found. |
| `DOWNLOAD_EXPIRED` | 410 | Accessing file after 24-hour retention period. | The generated export file has expired and is no longer available. |
| `UNSUPPORTED_FORMAT` | 422 | Requesting formatting extension other than `json`, `csv`, `xlsx`, `pdf`. | Requested export format is not supported. |

---

## 5. Security & Row-Level Scoping Specifications

Row-Level Security (RLS) policies are handled at the query construction phase to ensure tenants or team members do not read unauthorized data.

- **Finance / Admin Roles**: Full organization read scope. No row filtration applied.
- **Sales Executive**: Leads and bookings where `created_by` or `assigned_to` matches the user's `team_member_id`.
- **Operations Coordinator**: Bookings and trip plans where `trip_coordinator_team_member_id` matches the user's `team_member_id`.
