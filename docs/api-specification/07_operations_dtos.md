# 07 Operations DTOs
## Operational Trip Planning, Vendor Allocation, Checklist, and Task Schemas

> **Aggregate Root**: `TripPlan`
> **Standalone Aggregates**: `VendorAllocation`, `Task`
> **Child Aggregate**: `Checklist` (owned by `Booking`, managed through Operations)
> **Pattern**: All child entities are accessed only through their parent aggregate endpoints.
> Direct `POST /trip-days` or `POST /checklists` standalone endpoints must never be created.

---

## Aggregate Rules

- `TripPlan` is the Aggregate Root for all trip execution planning.
- `TripDay` is a child entity of `TripPlan`; it cannot exist independently.
- `VendorAllocation` belongs to a `TripDay` but operates as a standalone aggregate (independent negotiation lifecycle).
- `Checklist` belongs to `Booking`; it is gated through Operations before status transitions.
- `Task` is a standalone aggregate; it may belong to a `Booking` or a `Lead`.
- All child entities are modified only through `OperationsService`.
- Child repositories (`TripDayRepository`, `ChecklistRepository`) are internal implementation details.
- A `Booking` cannot transition to `Ready` status unless all `Checklist` items are `is_completed = true`.
- A confirmed `VendorAllocation` cannot be modified without admin override (`is_locked = true`).

---

## TripPlan State Machine

```
Planning → Ready → Started → Ongoing → Completed → Closed
```

| Transition | Trigger | Guard Condition |
| :--- | :--- | :--- |
| `Planning → Ready` | Operations Owner marks plan ready | All `Checklist` items `is_completed = true`. All allocations `is_locked = true`. |
| `Ready → Started` | Trip start date reached or manual trigger | Parent `Booking` must be `Confirmed`. |
| `Started → Ongoing` | In-progress update by coordinator | No guard. |
| `Ongoing → Completed` | Manual completion by Operations Owner | No pending `Task` items with `HIGH` priority. |
| `Completed → Closed` | Finance closure event received | `FinanceClosed` domain event received from Finance module. |

---

## VendorAllocation State Machine

```
PENDING → NEGOTIATING → CONFIRMED → LOCKED → SETTLED
                                 ↘ FAILED
```

| Status Code | Meaning |
| :--- | :--- |
| `PENDING` | Vendor identified; no price confirmed |
| `NEGOTIATING` | Quote received; under discussion |
| `CONFIRMED` | Price agreed; allocation committed |
| `LOCKED` | Admin-locked; cannot be modified without override |
| `SETTLED` | Vendor payment fully disbursed |
| `FAILED` | Allocation cancelled or vendor rejected |

**Lock Rule**: Confirmed allocations (`is_locked = true`) require admin-level permission to modify. This prevents accidental overrides after agreements are finalized.

---

## 1. Request DTOs

---

### 1.1 `CreateTripPlanRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `booking_id` | string | Yes | No | Format: UUID | — | `uuid-booking-1` |
| `prepared_date` | string | Yes | No | Format: ISO Date; not future | — | `2026-08-01` |
| `trip_plan_type` | string | No | No | Enum: `MANUAL`, `PACKAGE` | `MANUAL` | `MANUAL` |
| `notes` | string | No | Yes | Max: 1000 chars | — | `Preferred rooms on upper floor` |

```json
{
  "booking_id": "uuid-booking-1",
  "prepared_date": "2026-08-01",
  "trip_plan_type": "MANUAL",
  "notes": "Preferred rooms on upper floor. Group has 2 senior citizens."
}
```

**Validation Rules:**
- `booking_id` must reference an existing `Booking` record with status `Confirmed`.
- Only one active `TripPlan` may exist per `Booking` (`is_final = true` DB constraint).
- `prepared_date` must not be in the future.
- `TripPlan` is auto-linked to the `Booking.trip_coordinator_team_member_id`; coordinator must be assigned.

---

### 1.2 `UpdateTripDayRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `start_location` | string | No | Yes | Max: 100 chars | — | `Bangalore` |
| `end_location` | string | No | Yes | Max: 100 chars | — | `Coorg` |
| `overnight_destination_id` | string | No | Yes | Format: UUID | — | `uuid-dest-1` |
| `start_time` | string | No | Yes | Format: `HH:MM` (24h) | — | `06:00` |
| `end_time` | string | No | Yes | Format: `HH:MM` (24h) | — | `22:00` |
| `morning_plan` | string | No | Yes | Max: 2000 chars | — | `Tea estate visit` |
| `afternoon_plan` | string | No | Yes | Max: 2000 chars | — | `Lunch at hotel` |
| `evening_plan` | string | No | Yes | Max: 2000 chars | — | `Campfire session` |
| `night_stay` | string | No | Yes | Max: 150 chars | — | `Hotel Coorg View` |
| `notes` | string | No | Yes | Max: 1000 chars | — | `AC rooms requested` |

```json
{
  "start_location": "Bangalore",
  "end_location": "Coorg",
  "overnight_destination_id": "uuid-dest-1",
  "start_time": "06:00",
  "end_time": "22:00",
  "morning_plan": "Departure from Bangalore at 6AM. Drive to Coorg via Mysore route. Stop at Cauvery Nisargadhama.",
  "afternoon_plan": "Lunch at Hotel Coorg View. Check-in and rest period.",
  "evening_plan": "Tea estate guided tour. Campfire and cultural program.",
  "night_stay": "Hotel Coorg View - 5 rooms (2 AC Double, 3 AC Twin)",
  "notes": "AC rooms specifically requested. Senior citizen couple on ground floor."
}
```

---

### 1.3 `CreateVendorAllocationRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `vendor_id` | string | Yes | No | Format: UUID | — | `uuid-vendor-1` |
| `service_name` | string | Yes | No | Max: 150 chars | — | `Room Accommodation - 5 Rooms` |
| `service_type_id` | string | Yes | No | Format: UUID (VendorType) | — | `uuid-vt-hotel` |
| `service_date` | string | No | Yes | Format: ISO Date | — | `2026-08-10` |
| `quantity` | integer | Yes | No | `>= 1`, Max: 500 | 1 | `5` |
| `unit_price` | decimal | Yes | No | `> 0`, Max: 9,999,999.99 | — | `2000.00` |
| `quoted_amount` | decimal | Yes | No | `> 0`, Max: 9,999,999.99 | — | `10000.00` |
| `notes` | string | No | Yes | Max: 500 chars | — | `Include breakfast` |

```json
{
  "vendor_id": "uuid-vendor-1",
  "service_name": "Room Accommodation - 5 Rooms",
  "service_type_id": "uuid-vt-hotel",
  "service_date": "2026-08-10",
  "quantity": 5,
  "unit_price": 2000.00,
  "quoted_amount": 10000.00,
  "notes": "Include breakfast for all guests. Confirm by Aug 5."
}
```

**Validation Rules:**
- `vendor_id` must reference an active, non-deleted vendor.
- `quoted_amount` should equal `unit_price × quantity`; warn on mismatch (> 5% deviation).
- `service_date` must fall within parent booking's `trip_start_date` and `trip_end_date`.
- A locked allocation (`is_locked = true`) cannot be modified; return 409.
- Duplicate allocations (same `vendor_id` + `service_date` + `service_name`) on the same `TripDay` return a 409 with a warning.

---

### 1.4 `ConfirmVendorAllocationRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `confirmed_price` | decimal | Yes | No | `> 0`; must not exceed `quoted_amount × 1.10` | — | `9500.00` |
| `notes` | string | No | Yes | Max: 500 chars | — | `Negotiated ₹500 discount` |

```json
{
  "confirmed_price": 9500.00,
  "notes": "Negotiated ₹500 room discount. Confirmation ref #H2045."
}
```

**Business Rule:** `confirmed_price` must not exceed `quoted_amount` by more than 10% (anti-overrun guard). Exceeding this threshold requires an admin override flag.

---

### 1.5 `LockVendorAllocationRequest`

No request body required. Locking is an administrative action performed by an admin-role team member.

```json
{}
```

**Permission Required:** Admin or Senior Operations Manager role.

---

### 1.6 `CreateTaskRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `booking_id` | string | Conditional | Yes | Format: UUID; mutually exclusive with `lead_id` | — | `uuid-booking-1` |
| `lead_id` | string | Conditional | Yes | Format: UUID; mutually exclusive with `booking_id` | — | `null` |
| `assigned_to_team_member_id` | string | Yes | No | Format: UUID | — | `uuid-tm-2` |
| `parent_task_id` | string | No | Yes | Format: UUID | — | `null` |
| `title` | string | Yes | No | 3–200 chars | — | `Confirm hotel reservation` |
| `description` | string | No | Yes | Max: 2000 chars | — | `Call Hotel Coorg View` |
| `due_date` | string | No | Yes | Format: ISO Date; not past | — | `2026-08-05` |
| `priority_id` | string | Yes | No | Format: UUID (TaskPriority) | — | `uuid-priority-high` |
| `estimated_hours` | decimal | No | Yes | `> 0`, Max: 999.99 | — | `2.00` |

```json
{
  "booking_id": "uuid-booking-1",
  "lead_id": null,
  "assigned_to_team_member_id": "uuid-tm-2",
  "parent_task_id": null,
  "title": "Confirm hotel reservation for 5 rooms",
  "description": "Call Hotel Coorg View at +91-9876543210 and confirm reservation for check-in Aug 10. Request ground floor room for senior couple.",
  "due_date": "2026-08-05",
  "priority_id": "uuid-priority-high",
  "estimated_hours": 2.00
}
```

**Validation Rules:**
- Exactly one of `booking_id` or `lead_id` must be provided (XOR constraint).
- `due_date` must not be in the past.
- `assigned_to_team_member_id` must reference an active team member.
- `parent_task_id` if provided must belong to the same `booking_id` or `lead_id`.

---

### 1.7 `UpdateTaskStatusRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `task_status_id` | string | Yes | No | Format: UUID (TaskStatus) | — | `uuid-status-done` |
| `completed_date` | string | No | Yes | Format: ISO Date | — | `2026-08-05` |
| `actual_hours` | decimal | No | Yes | `>= 0`, Max: 999.99 | — | `1.50` |
| `notes` | string | No | Yes | Max: 500 chars | — | `Hotel confirmed via call` |

```json
{
  "task_status_id": "uuid-status-done",
  "completed_date": "2026-08-05",
  "actual_hours": 1.50,
  "notes": "Hotel confirmed via call. Confirmation reference #H2045."
}
```

---

### 1.8 `BulkAssignTasksRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `task_ids` | array[string] | Yes | No | Min: 1, Max: 50 UUIDs | — | `["uuid-task-1", "uuid-task-2"]` |
| `assigned_to_team_member_id` | string | Yes | No | Format: UUID | — | `uuid-tm-3` |

```json
{
  "task_ids": ["uuid-task-1", "uuid-task-2"],
  "assigned_to_team_member_id": "uuid-tm-3"
}
```

**Validation Rules:**
- All `task_ids` must be non-deleted tasks.
- `assigned_to_team_member_id` must reference an active team member.
- Soft-deleted or completed tasks in the list are silently skipped (partial success model).

---

### 1.9 `CompleteChecklistItemRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `is_completed` | boolean | Yes | No | — | — | `true` |

```json
{
  "is_completed": true
}
```

---

### 1.10 `CompleteTripRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `completion_notes` | string | No | Yes | Max: 1000 chars | — | `Trip completed successfully` |

```json
{
  "completion_notes": "Trip completed successfully. All travelers returned safely on Aug 13."
}
```

**Guard Condition:** All `Checklist` items for the booking must be `is_completed = true` before this transition is allowed. Service must validate and return `CHECKLIST_INCOMPLETE` if violated.

---

## 2. Response DTOs

---

### 2.1 `TripPlanSummaryResponse`

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | TripPlan UUID |
| `booking_id` | string | No | Parent booking UUID |
| `booking_number` | string | No | e.g., `AMT-2026-00001` |
| `version` | integer | No | Plan version number |
| `trip_plan_type` | string | No | `MANUAL` or `PACKAGE` |
| `status` | object | No | `{ id, code, name }` |
| `prepared_date` | string | No | ISO Date |
| `prepared_by` | object | No | `{ id, display_name }` |
| `approved_by` | object | Yes | `{ id, display_name }` or null |
| `approved_at` | string | Yes | ISO DateTime or null |
| `is_final` | boolean | No | Whether this is the active plan |
| `trip_days_count` | integer | No | Number of days in plan |
| `vendor_allocations_count` | integer | No | Total vendor allocations |
| `checklist_completion_rate` | decimal | No | Percentage e.g. `87.50` |
| `created_at` | string | No | ISO DateTime |

```json
{
  "id": "uuid-trip-plan-1",
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "version": 1,
  "trip_plan_type": "MANUAL",
  "status": { "id": "uuid-status-1", "code": "PLANNING", "name": "Planning" },
  "prepared_date": "2026-08-01",
  "prepared_by": { "id": "uuid-tm-1", "display_name": "Ravi Kumar" },
  "approved_by": null,
  "approved_at": null,
  "is_final": true,
  "trip_days_count": 4,
  "vendor_allocations_count": 6,
  "checklist_completion_rate": 62.50,
  "created_at": "2026-08-01T09:30:00Z"
}
```

---

### 2.2 `TripPlanDetailResponse`

```json
{
  "id": "uuid-trip-plan-1",
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "version": 1,
  "trip_plan_type": "MANUAL",
  "status": { "id": "uuid-status-1", "code": "PLANNING", "name": "Planning" },
  "prepared_date": "2026-08-01",
  "prepared_by": { "id": "uuid-tm-1", "display_name": "Ravi Kumar" },
  "approved_by": null,
  "approved_at": null,
  "final_itinerary_pdf": null,
  "notes": "Preferred rooms on upper floor. Group has 2 senior citizens.",
  "is_final": true,
  "row_version": 1,
  "trip_days": [
    {
      "id": "uuid-trip-day-1",
      "day_number": 1,
      "start_location": "Bangalore",
      "end_location": "Coorg",
      "overnight_destination_id": "uuid-dest-1",
      "overnight_destination_name": "Coorg",
      "start_time": "06:00",
      "end_time": "22:00",
      "morning_plan": "Departure from Bangalore at 6AM. Drive to Coorg via Mysore route.",
      "afternoon_plan": "Lunch at Hotel Coorg View. Check-in and rest.",
      "evening_plan": "Tea estate guided tour. Campfire and cultural program.",
      "night_stay": "Hotel Coorg View - 5 rooms (2 AC Double, 3 AC Twin)",
      "notes": "AC rooms specifically requested.",
      "vendor_allocations": [
        {
          "id": "uuid-alloc-1",
          "vendor_id": "uuid-vendor-1",
          "vendor_name": "Hotel Coorg View",
          "service_name": "Room Accommodation - 5 Rooms",
          "service_type": { "id": "uuid-vt-1", "code": "HOTEL", "name": "Hotel" },
          "service_date": "2026-08-10",
          "quantity": 5,
          "unit_price": 2000.00,
          "quoted_amount": 10000.00,
          "confirmed_price": 9500.00,
          "is_locked": false,
          "allocation_status": { "code": "CONFIRMED", "name": "Confirmed" },
          "total_paid": 4750.00,
          "balance_due": 4750.00,
          "settlement_status": "PARTIAL"
        }
      ]
    }
  ],
  "checklist": [
    {
      "id": "uuid-chk-1",
      "item_name": "Verify driver details and vehicle number",
      "is_completed": false,
      "completed_at": null
    },
    {
      "id": "uuid-chk-2",
      "item_name": "Collect advance payment receipt",
      "is_completed": true,
      "completed_at": "2026-08-02T10:00:00Z"
    }
  ],
  "checklist_completion_rate": 50.00,
  "created_at": "2026-08-01T09:30:00Z",
  "updated_at": "2026-08-01T09:30:00Z"
}
```

---

### 2.3 `VendorAllocationDetailResponse`

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | Allocation UUID |
| `trip_day_id` | string | No | Parent TripDay UUID |
| `vendor_id` | string | No | Vendor UUID |
| `vendor_name` | string | No | Snapshot vendor name at allocation time |
| `vendor_phone` | string | Yes | Snapshot vendor contact phone |
| `service_name` | string | No | Service description |
| `service_type` | object | No | `{ id, code, name }` |
| `service_date` | string | Yes | ISO Date |
| `quantity` | integer | No | Units booked |
| `unit_price` | decimal | No | Price per unit |
| `quoted_amount` | decimal | No | Total quoted price |
| `confirmed_price` | decimal | Yes | Final negotiated price |
| `is_locked` | boolean | No | Whether admin-locked |
| `allocation_status` | object | No | `{ code, name }` |
| `confirmed_by` | object | Yes | `{ id, display_name }` |
| `confirmed_at` | string | Yes | ISO DateTime |
| `total_paid` | decimal | No | Sum of settled VendorPayments |
| `balance_due` | decimal | No | `quoted_amount - total_paid` |
| `settlement_status` | string | No | `PENDING`, `PARTIAL`, `SETTLED` |
| `notes` | string | Yes | Free-text operational notes |

```json
{
  "id": "uuid-alloc-1",
  "trip_day_id": "uuid-trip-day-1",
  "vendor_id": "uuid-vendor-1",
  "vendor_name": "Hotel Coorg View",
  "vendor_phone": "+91-9876543210",
  "service_name": "Room Accommodation - 5 Rooms",
  "service_type": { "id": "uuid-vt-1", "code": "HOTEL", "name": "Hotel" },
  "service_date": "2026-08-10",
  "quantity": 5,
  "unit_price": 2000.00,
  "quoted_amount": 10000.00,
  "confirmed_price": 9500.00,
  "is_locked": true,
  "allocation_status": { "code": "CONFIRMED", "name": "Confirmed" },
  "confirmed_by": { "id": "uuid-tm-1", "display_name": "Ravi Kumar" },
  "confirmed_at": "2026-08-02T14:00:00Z",
  "total_paid": 4750.00,
  "balance_due": 4750.00,
  "settlement_status": "PARTIAL",
  "notes": "Negotiated ₹500 discount. Confirmation ref #H2045."
}
```

---

### 2.4 `TaskDetailResponse`

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | Task UUID |
| `booking_id` | string | Yes | Parent Booking UUID |
| `lead_id` | string | Yes | Parent Lead UUID |
| `assigned_to` | object | No | `{ id, display_name }` |
| `assigned_by` | object | Yes | `{ id, display_name }` |
| `parent_task_id` | string | Yes | Parent task UUID for subtasks |
| `title` | string | No | Task title |
| `description` | string | Yes | Detailed description |
| `due_date` | string | Yes | ISO Date |
| `completed_date` | string | Yes | ISO Date |
| `task_status` | object | No | `{ id, code, name }` |
| `priority` | object | No | `{ id, code, name }` |
| `estimated_hours` | decimal | Yes | Planned effort |
| `actual_hours` | decimal | Yes | Actual effort logged |
| `subtasks` | array | No | Array of `TaskSummaryResponse` |
| `created_at` | string | No | ISO DateTime |

```json
{
  "id": "uuid-task-1",
  "booking_id": "uuid-booking-1",
  "lead_id": null,
  "assigned_to": { "id": "uuid-tm-2", "display_name": "Priya Sharma" },
  "assigned_by": { "id": "uuid-tm-1", "display_name": "Ravi Kumar" },
  "parent_task_id": null,
  "title": "Confirm hotel reservation for 5 rooms",
  "description": "Call Hotel Coorg View and confirm reservation for check-in Aug 10.",
  "due_date": "2026-08-05",
  "completed_date": null,
  "task_status": { "id": "uuid-ts-1", "code": "IN_PROGRESS", "name": "In Progress" },
  "priority": { "id": "uuid-tp-1", "code": "HIGH", "name": "High" },
  "estimated_hours": 2.00,
  "actual_hours": null,
  "subtasks": [],
  "created_at": "2026-08-01T09:30:00Z"
}
```

---

### 2.5 `ChecklistSummaryResponse`

```json
{
  "booking_id": "uuid-booking-1",
  "total_items": 8,
  "completed_items": 5,
  "pending_items": 3,
  "completion_rate": 62.50,
  "is_ready_for_transition": false,
  "items": [
    {
      "id": "uuid-chk-1",
      "item_name": "Verify driver details and vehicle number",
      "is_completed": false,
      "completed_at": null
    },
    {
      "id": "uuid-chk-2",
      "item_name": "Collect advance payment receipt",
      "is_completed": true,
      "completed_at": "2026-08-02T10:00:00Z"
    }
  ]
}
```

---

### 2.6 `TripCompletionValidationResponse`

Returned by `GET /api/v1/operations/trip-plans/{id}/completion-check` before attempting completion.

```json
{
  "booking_id": "uuid-booking-1",
  "trip_plan_id": "uuid-trip-plan-1",
  "can_complete": false,
  "blocking_reasons": [
    "3 checklist items are not completed",
    "VendorAllocation uuid-alloc-2 is in NEGOTIATING status (not confirmed)"
  ],
  "checklist_completion_rate": 62.50,
  "unconfirmed_allocations": 1,
  "pending_high_priority_tasks": 0
}
```

---

### 2.7 `TripPlanListResponse` (Paginated)

```json
{
  "items": [
    {
      "id": "uuid-trip-plan-1",
      "booking_id": "uuid-booking-1",
      "booking_number": "AMT-2026-00001",
      "version": 1,
      "status": { "code": "PLANNING", "name": "Planning" },
      "trip_days_count": 4,
      "checklist_completion_rate": 62.50,
      "prepared_date": "2026-08-01",
      "created_at": "2026-08-01T09:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

## 3. Error Catalogue

| Error Code | HTTP Status | Trigger | Message |
| :--- | :--- | :--- | :--- |
| `TRIP_PLAN_ALREADY_EXISTS` | 409 | Creating TripPlan when one is already `is_final = true` | A final trip plan already exists for this booking |
| `BOOKING_NOT_CONFIRMED` | 409 | Creating TripPlan for non-confirmed booking | Booking must be in Confirmed status before creating a trip plan |
| `VENDOR_ALLOCATION_LOCKED` | 409 | Modifying a locked allocation | This vendor allocation is locked and cannot be modified |
| `CHECKLIST_INCOMPLETE` | 409 | Completing trip with pending checklist items | All checklist items must be completed before marking trip complete |
| `TRIP_PLAN_NOT_FOUND` | 404 | Trip plan UUID does not exist | Trip plan not found |
| `VENDOR_ALLOCATION_NOT_FOUND` | 404 | Allocation UUID does not exist | Vendor allocation not found |
| `TASK_NOT_FOUND` | 404 | Task UUID does not exist | Task not found |
| `ALLOCATION_PRICE_OVERRUN` | 422 | Confirmed price exceeds quoted amount by > 10% | Confirmed price exceeds quoted amount threshold |
| `CONCURRENT_UPDATE` | 409 | `row_version` mismatch on TripPlan update | Concurrent modification detected. Please refresh and retry |
| `SERVICE_DATE_OUT_OF_RANGE` | 422 | `service_date` outside booking trip dates | Service date must fall within the booking trip date range |
| `INVALID_TASK_PARENT` | 422 | Both `booking_id` and `lead_id` provided | A task must belong to either a booking or a lead, not both |

---

## 4. Security Matrix

| Operation | Min Role | Notes |
| :--- | :--- | :--- |
| `GET /trip-plans` | Operations Executive | Filtered to own assignments by default |
| `POST /trip-plans` | Operations Executive | Requires booking in `Confirmed` status |
| `PATCH /trip-plans/{id}/days/{day_id}` | Operations Executive | Must be assigned Operations Owner |
| `POST /trip-plans/{id}/allocations` | Operations Executive | — |
| `PATCH /allocations/{id}/confirm` | Operations Executive | — |
| `PATCH /allocations/{id}/lock` | Admin | Admin-only action |
| `POST /trip-plans/{id}/complete` | Operations Executive | Checklist guard enforced |
| `POST /tasks` | Any Team Member | Can create tasks for own assignments |
| `POST /tasks/bulk-assign` | Operations Executive | — |
| `PATCH /checklist/{item_id}` | Trip Coordinator | — |

---

## 5. Domain Events Published

| Event | Trigger | Payload |
| :--- | :--- | :--- |
| `TripCompleted` | `POST /trip-plans/{id}/complete` succeeds | `{ trip_plan_id, booking_id, completed_at, operations_owner_id }` |
| `ChecklistCompleted` | All checklist items `is_completed = true` | `{ booking_id, completed_at }` |
| `VendorAllocationConfirmed` | Allocation status → `CONFIRMED` | `{ allocation_id, vendor_id, trip_day_id, confirmed_price }` |

---

## 6. Domain Events Subscribed

| Event | Source | Action |
| :--- | :--- | :--- |
| `BookingConfirmed` | Booking Module | Auto-create `TripPlan` stub; copy checklist items from template |
| `FinanceClosed` | Finance Module | Transition `TripPlan` status to `CLOSED` |
