# 11 Dashboard DTOs
## Operational Widget Aggregations and Read-Only Panel Data Schemas

---

> **Module Type**: Read Model (Strictly Read-Only)  
> **Pattern**: CQRS Query Side  
> **Writes**: ❌ None  
> **Events**: ❌ Publish None (Optional cache invalidation subscription only)  
> **Database**: Read-Only Access  
> **Performance Target**: Simple widgets `<100ms`, complex widgets `<500ms`.  
> **Refresh Strategy**: In-memory Redis caching with dynamic event-driven cache invalidation and graceful database query fallback on cache miss or Redis unavailability.

---

## 1. Dashboard Widget Inventory

| Widget | Endpoint | Event-Driven Cache Invalidation | TTL (Fallback) |
| :--- | :--- | :--- | :--- |
| Summary Cards | `GET /api/v1/dashboard/widgets/summary-cards` | `LeadCreated`, `LeadStatusChanged`, `BookingConfirmed`, `PaymentVerified`, `RefundCompleted`, `TripCompleted` | 5 min |
| Lead Funnel | `GET /api/v1/dashboard/widgets/lead-pipeline` | `LeadCreated`, `LeadStatusChanged` | 5 min |
| Booking Funnel | `GET /api/v1/dashboard/widgets/booking-pipeline` | `BookingConfirmed`, `BookingCancelled`, `TripCompleted` | 5 min |
| Finance Summary | `GET /api/v1/dashboard/widgets/finance-summary` | `PaymentVerified`, `RefundCompleted`, `FinanceClosed` | 5 min |
| Upcoming Trips | `GET /api/v1/dashboard/widgets/upcoming-trips` | `BookingConfirmed`, `TripCompleted` | 15 min |
| Operations Overview | `GET /api/v1/dashboard/widgets/operations-overview` | `TripCompleted`, `TaskCreated`, `TaskCompleted`, `VendorAllocationConfirmed` | 10 min |
| Monthly Revenue Trend | `GET /api/v1/dashboard/widgets/revenue-trend` | `PaymentVerified`, `RefundCompleted`, `FinanceClosed` | 30 min |

---

## 2. Response DTO Contracts

Every response payload contains standardized metadata to identify data freshness and cache behavior:
- `generated_at`: ISO timestamp when the payload was built by the database or cache.
- `as_of`: ISO timestamp representing the transaction boundary (usually same as `generated_at` unless pulling from older snapshots).
- `cache_ttl`: Remaining TTL in seconds for the cached data.

---

### 2.1 `SummaryCardsResponse`
`GET /api/v1/dashboard/widgets/summary-cards`
*   **Security Permission**: `dashboard.read`

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `active_leads` | integer | No | Total non-closed CRM Leads |
| `open_proposals` | integer | No | Proposals with status `DRAFT` or `UNDER_DISCUSSION` |
| `confirmed_bookings` | integer | No | Bookings with status `CONFIRMED`, `PLANNING`, `READY`, `ONGOING` |
| `trips_today` | integer | No | Bookings where `trip_start_date <= today <= trip_end_date` |
| `outstanding_payments` | integer | No | Overdue customer PaymentSchedule count |
| `pending_vendor_payments` | integer | No | Confirmed VendorAllocations unpaid count |
| `revenue_this_month` | decimal | No | Sum of payments received this calendar month |
| `profit_this_month` | decimal | No | Gross margin this month (revenue - expenses) |

#### Example Response
```json
{
  "status": "success",
  "message": "Summary cards retrieved successfully.",
  "data": {
    "active_leads": 28,
    "open_proposals": 9,
    "confirmed_bookings": 14,
    "trips_today": 3,
    "outstanding_payments": 2,
    "pending_vendor_payments": 5,
    "revenue_this_month": 852000.00,
    "profit_this_month": 727500.00
  },
  "generated_at": "2026-08-03T18:00:00Z",
  "as_of": "2026-08-03T18:00:00Z",
  "cache_ttl": 300
}
```

---

### 2.2 `LeadPipelineWidgetResponse`
`GET /api/v1/dashboard/widgets/lead-pipeline`
*   **Security Permission**: `dashboard.read`

Returns funnel counts and percentage distributions across CRM stages: `NEW`, `ASSIGNED`, `CONTACTED`, `PROPOSAL`, `NEGOTIATION`, `WON`, `LOST`.

#### Example Response
```json
{
  "status": "success",
  "message": "Lead pipeline retrieved successfully.",
  "data": [
    { "status": "NEW", "count": 25, "percentage": 18.38 },
    { "status": "ASSIGNED", "count": 15, "percentage": 11.03 },
    { "status": "CONTACTED", "count": 30, "percentage": 22.06 },
    { "status": "PROPOSAL", "count": 20, "percentage": 14.71 },
    { "status": "NEGOTIATION", "count": 10, "percentage": 7.35 },
    { "status": "WON", "count": 28, "percentage": 20.59 },
    { "status": "LOST", "count": 8, "percentage": 5.88 }
  ],
  "generated_at": "2026-08-03T18:00:00Z",
  "as_of": "2026-08-03T18:00:00Z",
  "cache_ttl": 300
}
```

---

### 2.3 `BookingPipelineWidgetResponse`
`GET /api/v1/dashboard/widgets/booking-pipeline`
*   **Security Permission**: `dashboard.read`

Returns count and percentage distributions for active/recent bookings across status stages: `WAITING_ADVANCE`, `CONFIRMED`, `READY`, `ONGOING`, `COMPLETED`, `CLOSED`, `CANCELLED`.

#### Example Response
```json
{
  "status": "success",
  "message": "Booking pipeline retrieved successfully.",
  "data": [
    { "status": "WAITING_ADVANCE", "count": 3, "percentage": 10.71 },
    { "status": "CONFIRMED", "count": 5, "percentage": 17.86 },
    { "status": "PLANNING", "count": 4, "percentage": 14.29 },
    { "status": "READY", "count": 2, "percentage": 7.14 },
    { "status": "ONGOING", "count": 3, "percentage": 10.71 },
    { "status": "COMPLETED", "count": 8, "percentage": 28.57 },
    { "status": "CLOSED", "count": 2, "percentage": 7.14 },
    { "status": "CANCELLED", "count": 1, "percentage": 3.57 }
  ],
  "generated_at": "2026-08-03T18:00:00Z",
  "as_of": "2026-08-03T18:00:00Z",
  "cache_ttl": 300
}
```

---

### 2.4 `FinanceSummaryWidgetResponse`
`GET /api/v1/dashboard/widgets/finance-summary`
*   **Security Permission**: `dashboard.read`, `finance.read` (or equivalent)

Exposes critical read-only financial metrics and gross margin percentages:

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `collected` | decimal | No | Total customer payments received this month |
| `outstanding` | decimal | No | Total pending customer balance due |
| `vendor_due` | decimal | No | Total outstanding vendor disbursements |
| `expenses` | decimal | No | Total operations expenses logged this month |
| `refunds` | decimal | No | Total customer refunds completed this month |
| `net_profit` | decimal | No | Gross margins calculated: `collected - expenses - refunds` |
| `gross_margin_percentage` | decimal | No | Margin ratio: `(net_profit / collected) * 100` (or 0 if collected is 0) |

#### Example Response
```json
{
  "status": "success",
  "message": "Finance summary retrieved successfully.",
  "data": {
    "collected": 852000.00,
    "outstanding": 312000.00,
    "vendor_due": 185000.00,
    "expenses": 124500.00,
    "refunds": 48000.00,
    "net_profit": 679500.00,
    "gross_margin_percentage": 79.75
  },
  "generated_at": "2026-08-03T18:00:00Z",
  "as_of": "2026-08-03T18:00:00Z",
  "cache_ttl": 300
}
```

---

### 2.5 `UpcomingTripsWidgetResponse`
`GET /api/v1/dashboard/widgets/upcoming-trips?page=1&page_size=10`
*   **Security Permission**: `dashboard.read`
*   **Query Parameters**:
    *   `page`: Page index (default: 1)
    *   `page_size`: Items per page (default: 10)

Returns upcoming trips departing within the next 14 days, optimized with pagination support.

#### Example Response
```json
{
  "status": "success",
  "message": "Upcoming trips retrieved successfully.",
  "data": {
    "upcoming_trips": [
      {
        "booking_number": "AMT-2026-00001",
        "customer": "Raj Enterprises",
        "destination": "Munnar",
        "coordinator": "Ravi Kumar",
        "departure": "2026-08-10",
        "remaining_days": 7
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 1,
      "total_pages": 1
    }
  },
  "generated_at": "2026-08-03T18:00:00Z",
  "as_of": "2026-08-03T18:00:00Z",
  "cache_ttl": 900
}
```

---

### 2.6 `OperationsOverviewWidgetResponse`
`GET /api/v1/dashboard/widgets/operations-overview`
*   **Security Permission**: `dashboard.read`

Summarizes ongoing coordinator workloads and task metrics across the system:

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `coordinator` | string | No | Display name of the team member |
| `trips_assigned` | integer | No | Total active TripPlans assigned to coordinator |
| `open_tasks` | integer | No | Open Operations Tasks assigned |
| `pending_checklist` | integer | No | Uncompleted operational checklist tasks |
| `pending_vendors` | integer | No | Vendor allocations still in PENDING or NEGOTIATING status |

#### Example Response
```json
{
  "status": "success",
  "message": "Operations overview retrieved successfully.",
  "data": [
    {
      "coordinator_id": "uuid-ravikumar",
      "coordinator": "Ravi Kumar",
      "trips_assigned": 3,
      "open_tasks": 9,
      "pending_checklist": 12,
      "pending_vendors": 4
    }
  ],
  "generated_at": "2026-08-03T18:00:00Z",
  "as_of": "2026-08-03T18:00:00Z",
  "cache_ttl": 600
}
```

---

### 2.7 `MonthlyRevenueTrendResponse`
`GET /api/v1/dashboard/widgets/revenue-trend`
*   **Security Permission**: `dashboard.read`, `finance.read` (or equivalent)

Exposes rolling 6-month transaction metrics for charts:

#### Example Response
```json
{
  "status": "success",
  "message": "Revenue trend retrieved successfully.",
  "data": {
    "trend_months": [
      { "month": "2026-03", "collected": 620000.00, "refund": 10000.00, "expenses": 95000.00, "profit": 515000.00 },
      { "month": "2026-04", "collected": 740000.00, "refund": 20000.00, "expenses": 110000.00, "profit": 610000.00 },
      { "month": "2026-05", "collected": 810000.00, "refund": 15000.00, "expenses": 118000.00, "profit": 677000.00 },
      { "month": "2026-06", "collected": 790000.00, "refund": 25000.00, "expenses": 108000.00, "profit": 657000.00 },
      { "month": "2026-07", "collected": 870000.00, "refund": 30000.00, "expenses": 131000.00, "profit": 709000.00 },
      { "month": "2026-08", "collected": 852000.00, "refund": 48000.00, "expenses": 124500.00, "profit": 679500.00 }
    ],
    "period": "6M"
  },
  "generated_at": "2026-08-03T18:00:00Z",
  "as_of": "2026-08-03T18:00:00Z",
  "cache_ttl": 1800
}
```

---

## 3. Error Codes

| Error Code | HTTP Status | Trigger | Message |
| :--- | :--- | :--- | :--- |
| `DASHBOARD_COMPUTE_ERROR` | 500 | Aggregation fails on fallback | Dashboard data could not be computed. Please retry. |
| `CACHE_UNAVAILABLE` | N/A | Redis down (Internal Log only) | Cache connection failed; falling back to Database. |
