# 06 Booking DTOs
## Operational Booking Aggregate Schemas

> **Status: FROZEN — Implementation Ready (Phase 7 / Phase 9)**
> This document defines the frozen API contracts, validation rules, field types, and lifecycle expectations for the Booking module.
> Last updated: 2026-08-03

The Booking module is the central transactional engine of the Amigos platform, managing confirmed trips, traveler manifests, payment schedules, and documents.

All Booking endpoints are located under the route prefix: `/api/v1/bookings` (with lookups under `/api/v1/lookups` or `/api/v1/crm/lookups`).

---

# 1. Business Context

A Booking represents a formal transactional contract with a client for a customized travel itinerary. It maps:
- The customer profile (`Customer` / `ContactPerson`)
- The traveler manifest (`Traveler`)
- Travel details snapshotted from a finalized proposal
- A payment schedule (`PaymentSchedule`) divided into installments
- Uploaded traveler ID proofs and legal documentation (`Document`)

---

# 2. Module Boundaries & Responsibilities

### 2.1 Module Responsibilities

| Module | Owns | Cannot Modify |
| :--- | :--- | :--- |
| **Proposal** | Proposal Versions, Day Itineraries, pricing estimates | Bookings, payment logs, operations check |
| **Booking** | Booking Aggregate, travelers, schedules, document link | Proposal, customer profiles, raw payments |
| **Customer** | Customer Profile, direct coordinator contacts | Booking details, payment schedules |
| **Finance** | Payment Logs, payment verification statuses, cash flows | Travelers list, booking dates, checklist |
| **Operations** | Trip Plan routing, tasks allocations, checklists | Payment schedules, booking price, traveler manifest |
| **Notification** | Emails dispatcher, templates matching | Booking status values, traveler manifestation |

### 2.2 Aggregate Rules & Invariants
- **Booking is the Aggregate Root**.
- **No Standalone CRUD**: Child entities (`Traveler`, `Document`, `PaymentSchedule`, `BookingStatusHistory`) cannot exist without a parent `Booking`. They **must never** expose independent root-level CRUD endpoints (e.g., `POST /travelers` is illegal; instead, nested endpoints like `POST /bookings/{id}/travelers` must be used).
- **Service Gating**: Child entities are modified only through the `BookingService`.
- **Encapsulated Repositories**: Child repositories are internal implementation details of the Booking module and must never be exposed externally.
- **Aggregate Consistency Rule**: Every modification affecting Travelers, Documents, PaymentSchedules, or Timeline must occur through the `BookingService`. No other module or service may update aggregate children directly.

#### Booking Aggregate Invariants (Permanent Truths)
- Booking always has exactly one `ProposalVersion`.
- Booking always belongs to one `Customer`.
- Booking always contains exactly one Lead Traveler.
- Booking total amount equals the sum of installment absolute amounts.
- Booking number never changes after creation.
- Closed or completed bookings are immutable.
- Children cannot exist independently.

### 2.3 Customer Ownership
- **CRM/Customer Module Dominance**: Booking **does not own** the `Customer` entity.
- **Reference Only**: Booking only links to an existing `Customer` via `customer_id`. The Customer module owns addresses, phone numbers, emails, and profile maintenance. If a new customer profile needs to be created during CRM conversion, Booking delegates to `CustomerService`.

### 2.4 Proposal-to-Booking Locking
- **One-to-One Match**: A booking links to exactly one finalized Proposal via `proposal_version_id` (enforced by a DB unique constraint).
- **Immutability Inheritance**: Once a booking is successfully created, the linked `Proposal` becomes permanently locked and cannot be edited, deleted, or unfinalized. After conversion, the Proposal is strictly read-only; only audit metadata may change.

### 2.5 Booking Number Generation Strategy
- **Format**: `AMT-YYYY-XXXXX` (e.g., `AMT-2026-00001`, `AMT-2026-00002`).
- **Generation Layer**: Sequence generation is managed in the **Service Layer** to maintain strict business formatting control.
- **Sequence Storage**: Booking numbers are generated using a dedicated database sequence table. `SELECT MAX()` must not be used because it is unsafe under concurrent requests and prone to race conditions.
- **Reset Frequency**: The sequence counter (`XXXXX`) resets to `00001` on January 1st of every calendar year (`YYYY`).
- **Permanence**: Once assigned, booking numbers are permanent. Cancelled bookings retain their numbers, and soft-deleted bookings retain their numbers. Numbers are **never** recycled or reused.

---

# 3. Status Transition Matrix

### 3.1 Lifecycle Diagram

```
Proposal Approved / Finalized
              │
              ▼
     WAITING_FOR_ADVANCE ──────────┐
              │                    │
        Finance Verify             │
              ▼                    │
          CONFIRMED                │
              │                    │
       Ops Coordinator             │
              ▼                    │
          PLANNING                 │
              │                    │
     Checklists Complete           │
              ▼                    │
            READY                  │
              │                    │
          Trip Start               │
              ▼                    │
           ONGOING                 │
              │                    │
           Trip End                │
              ▼                    │
          COMPLETED                │
              │                    │
        Finance Audit              ▼
              ▼                CANCELLED
            CLOSED
```

### 3.2 Transition Preconditions
- **`WAITING_FOR_ADVANCE` -> `CONFIRMED`**: 
  - Requirement: First payment transaction of type `ADVANCE` logged and verified by Finance.
  - Requirement: Proposal status is `CONVERTED`.
  - Requirement: Linked Customer exists.
- **`CONFIRMED` -> `PLANNING`**:
  - Requirement: Operations Owner/Trip Coordinator assigned and active.
- **`PLANNING` -> `READY`**:
  - Requirement: Trip checklist tasks are fully completed (`is_completed = true`).
  - Requirement: All vendor allocations confirmed and locked.
- **`READY` -> `ONGOING`**:
  - Requirement: Trip start date reached.
- **`ONGOING` -> `COMPLETED`**:
  - Requirement: Trip end date reached.
- **`COMPLETED` -> `CLOSED`**:
  - Requirement: No outstanding customer payments.
  - Requirement: All vendor invoices settled.

### 3.3 Cancellation Boundaries
- A Booking can transition to `CANCELLED` from `WAITING_FOR_ADVANCE`, `CONFIRMED`, `PLANNING`, or `READY`.
- **No Cancel on Execution**: A Booking **cannot** be cancelled once the trip is `ONGOING`, `COMPLETED`, or `CLOSED`.
- **Reopening Paths**: Reopening a `COMPLETED` or `CLOSED` booking is restricted to Admin roles. A reopened booking reverts to `PLANNING` status.

---

# 4. Detailed Validation Rules

### 4.1 Payment Schedule Rules
- **Sum Constraint**: The sum of all installment percentages must equal exactly `100.00%`.
- **Percentage Bounds**: Every individual percentage must be greater than `0.00%` and less than or equal to `100.00%`. No negative percentages allowed.
- **Strict Sequences**: Installment numbers (`installment_no`) must start at `1` and increment sequentially (`1, 2, 3...`) without gaps or duplicates.
- **Temporal Alignment**: Due dates must be strictly ascending (`due_date` of installment N+1 must be later than installment N).
- **Creation Bound**: No installment due date can precede the booking date.
- **Financial Cohesion**: The sum of all installment absolute amounts must equal the booking's `total_amount` exactly.

### 4.2 Traveler Rules
- **Lead Traveler Requirement**: A booking traveler manifest must have **exactly one** Lead Traveler (`is_group_leader = true`).
- **Minimum Manifest**: At least one traveler is required.
- **Delete Guard**: The designated Lead Traveler cannot be deleted until the leadership role is reassigned to another traveler in the manifest.
- **DOB & Age Validation**: Age must be `>= 0` and `<= 120`. DOB must correspond to the calculated age.
- **Aadhaar / Passport Validation**: If an ID proof type is provided, the ID proof number must match the format patterns (Passport: `^[A-Z][0-9]{7}$`, Aadhaar: `^[0-9]{4}-[0-9]{4}-[0-9]{4}$`).
- **Passport Expiry**: Passport expiry date must be at least 6 months after the `trip_end_date`.
- **Emergency Contact**: Emergency contact phone number and relationship are mandatory for the Lead Traveler.

### 4.3 Document Lifecycle
Every document uploaded follows a transition path to maintain compliance:
`UPLOADED (Draft uploaded) ──> UNDER_REVIEW (Checked by operations) ──> VERIFIED (Approved) ──> EXPIRED (Validity date exceeded)`

---

# 5. Cross-Module Communication Matrix

| Module | Communication Method | Reason |
| :--- | :--- | :--- |
| **CRM** | Direct Service (Temporary) | Lead conversion call; to be replaced by `LeadConverted` domain event |
| **Proposal** | Read Repository / Model | Fetch snapshotted pricing and day structures |
| **Customer** | CustomerService / Model | Verify linked customer billing reference |
| **Team** | TeamMemberService / Model | Validate operations team members and coordinator IDs |
| **Master** | Read Repository / Model | Fetch booking lookups, document types, and configurations |
| **Finance** | Domain Event | Emits `BookingCreated`/`BookingCancelled`; Subscribes to payments |
| **Operations** | Domain Event | Emits `BookingConfirmed`/`BookingCancelled` |
| **Notifications** | Domain Event | Subscribes to status changes for dispatching payloads |

---

# 6. Event Catalogue & Event Consumers

> [!IMPORTANT]
> **Transactional Event Rule**: Domain events must strictly be published **only after a successful database transaction commit**. Under no circumstances should an event be emitted before database writes have been finalized.

### 6.1 Event list
- `BookingCreated`: Emitted after a booking draft is saved in `WAITING_FOR_ADVANCE`.
- `BookingConfirmed`: Emitted when the booking status changes to `CONFIRMED`.
- `BookingCancelled`: Emitted when a booking is cancelled.
- `BookingCoordinatorAssigned`: Emitted when `trip_coordinator_team_member_id` is updated.
- `TravelerAdded` / `TravelerRemoved`: Emitted when the traveler manifest changes.
- `PaymentScheduleGenerated`: Emitted when installments are defined.
- `BookingCompleted`: Emitted when status changes to `COMPLETED`.
- `BookingClosed`: Emitted when status changes to `CLOSED`.

---

# 7. Request DTOs

### 7.1 `CreateBookingRequest`
```json
{
  "proposal_id": "5fa85f64-5717-4562-b3fc-2c963f66afa6",
  "group_name": "Summer Adventure 2026",
  "travelers": [
    {
      "name": "Jane Doe",
      "age": 29,
      "gender": "Female",
      "id_proof_type": "Passport",
      "id_proof_number": "A1234567",
      "emergency_contact": "+919876543210",
      "special_requirements": "Vegetarian meal",
      "is_group_leader": true
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
```

### 7.2 `UpdateBookingRequest`
```json
{
  "row_version": 1,
  "group_name": "Summer Adventure 2026 Updated",
  "internal_notes": "Needs group coordinator review."
}
```

### 7.3 `TravelerRequest`
```json
{
  "name": "Arjun",
  "age": 28,
  "gender": "Male",
  "id_proof_type": "Aadhaar",
  "id_proof_number": "1234-5678-9012",
  "emergency_contact": "9876543210",
  "special_requirements": "Wheelchair access",
  "is_group_leader": false
}
```

### 7.4 `ConfirmBookingRequest`
```json
{
  "row_version": 1,
  "trip_coordinator_team_member_id": "8abb7d05-7181-4b22-ac00-8abb7d05aa45",
  "notes": "Operations coordinator assigned; trip plan approved."
}
```

### 7.5 `CancelBookingRequest`
```json
{
  "row_version": 1,
  "cancellation_reason": "Customer cancelled due to flight changes."
}
```

---

# 8. Response DTOs

### 8.1 `BookingSummaryResponse`
```json
{
  "id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
  "booking_number": "AMT-2026-00001",
  "group_name": "Summer Adventure 2026",
  "booking_date": "2026-08-03",
  "trip_start_date": "2026-08-20",
  "trip_end_date": "2026-08-27",
  "total_travelers": 1,
  "total_amount": 50000.00,
  "status": {
    "id": "3b710d5a-0225-4f8b-a03f-5b6acab4917b",
    "code": "WAITING_FOR_ADVANCE",
    "name": "Waiting for Advance"
  },
  "created_at": "2026-08-03T12:00:00Z"
}
```

### 8.2 `BookingDetailResponse`
```json
{
  "id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
  "booking_number": "AMT-2026-00001",
  "row_version": 1,
  "entry_mode": "NORMAL",
  "group_name": "Summer Adventure 2026",
  "booking_date": "2026-08-03",
  "trip_start_date": "2026-08-20",
  "trip_end_date": "2026-08-27",
  "total_travelers": 1,
  "total_amount": 50000.00,
  "proposal_version_id": "5fa85f64-5717-4562-b3fc-2c963f66afa6",
  "lead_id": "21005817-81b7-4c73-b880-a75b3f3aad74",
  "customer_id": "0ad9da46-7181-4b22-ac00-8abb7d05aa45",
  "contact_person_id": "8abb7d05-7181-4b22-ac00-0ad9da46fa45",
  "trip_coordinator": {
    "id": "8abb7d05-7181-4b22-ac00-8abb7d05aa45",
    "display_name": "John Coordinator"
  },
  "snapshots": {
    "package_name": "Munnar Escape Premium",
    "organization_name": "ACME Corp",
    "contact_person_name": "Jane Smith",
    "trip_name": "Munnar Premium Escapade"
  },
  "status": {
    "id": "3b710d5a-0225-4f8b-a03f-5b6acab4917b",
    "code": "WAITING_FOR_ADVANCE",
    "name": "Waiting for Advance"
  },
  "travelers": [
    {
      "id": "c18b2e6a-360d-44b9-a3b8-da403095eac8",
      "name": "Jane Doe",
      "age": 29,
      "gender": "Female",
      "id_proof_type": "Passport",
      "id_proof_number": "A1234567",
      "emergency_contact": "+919876543210",
      "special_requirements": "Vegetarian meal",
      "is_group_leader": true
    }
  ],
  "payment_schedule": [
    {
      "id": "0e520dfd-73f6-4da5-bd5b-5e2a93f50b8b",
      "installment_no": 1,
      "due_date": "2026-08-15",
      "percentage": 50.00,
      "amount": 25000.00,
      "status": "UNPAID",
      "remarks": "Advance deposit"
    },
    {
      "id": "56441c6f-c886-442b-9649-6c8b58b13700",
      "installment_no": 2,
      "due_date": "2026-09-15",
      "percentage": 50.00,
      "amount": 25000.00,
      "status": "UNPAID",
      "remarks": "Final payment"
    }
  ],
  "audit": {
    "created_by": "0e520dfd-73f6-4da5-bd5b-5e2a93f50b8b",
    "created_at": "2026-08-03T12:00:00Z",
    "updated_by": null,
    "updated_at": null
  }
}
```

### 8.3 `BookingTimelineResponse` (Unified Audit History)
The status history is conceptualized as a unified **Booking Timeline** mapping major changes:
- Status changes
- Traveler manifest modifications (adds/removes)
- Payment schedule additions/updates
- Coordinator updates
- Document uploads
- Booking cancellations
```json
{
  "booking_id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timeline_events": [
    {
      "id": "1de13eb5-d528-4931-b99f-73d3f24630b7",
      "from_status": null,
      "to_status": {
        "code": "WAITING_FOR_ADVANCE",
        "name": "Waiting for Advance"
      },
      "changed_by": {
        "id": "0e520dfd-73f6-4da5-bd5b-5e2a93f50b8b",
        "display_name": "Sales Executive"
      },
      "changed_at": "2026-08-03T12:00:00Z",
      "notes": "Booking created from finalized proposal."
    }
  ]
}
```

---

# 9. Performance & Loading Strategy

- **List Endpoint (`GET /bookings`)**: Uses `BookingSummaryResponse` mapping. Under the hood, the repository query strictly avoids N+1 problems by executing a flat query **without** child collections (`travelers`, `payment_schedules`, `documents`).
- **Detail Endpoint (`GET /bookings/{id}`)**: Uses a single SQL statement compiled with SQLAlchemy `joinedload` options for:
  - `Booking.travelers`
  - `Booking.payment_schedules`
  - `Booking.documents`
  - `Booking.status_history`
  This guarantees a single database roundtrip for detail rendering.

---

# 10. Security & Authorization Matrix

The Booking module enforces granular security scopes:

| Endpoint | HTTP Method | Required Permission |
| :--- | :--- | :--- |
| `GET /api/v1/bookings` | GET | `booking.read` |
| `GET /api/v1/bookings/{id}` | GET | `booking.read` |
| `POST /api/v1/bookings` | POST | `booking.create` |
| `PUT /api/v1/bookings/{id}` | PUT | `booking.update` |
| `DELETE /api/v1/bookings/{id}` | DELETE | `booking.delete` |
| `POST /api/v1/bookings/{id}/confirm` | POST | `booking.confirm` |
| `POST /api/v1/bookings/{id}/cancel` | POST | `booking.cancel` |

---

# 11. Error Catalogue

All error responses strictly enforce a standard response envelope.

**Error Envelope**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERR_OPTIMISTIC_LOCK",
    "message": "The resource has been modified by another process.",
    "details": {}
  },
  "validation_errors": []
}
```

| HTTP Status | Error Code | Description |
| :--- | :--- | :--- |
| `400 Bad Request` | `ERR_VALIDATION` | Request payload fails structural schema checks |
| `404 Not Found` | `ERR_NOT_FOUND` | Booking, traveler, document, or lookup not found |
| `409 Conflict` | `ERR_CONCURRENT_MODIFICATION` | Optimistic lock check failed (wrong `row_version`) |
| `409 Conflict` | `ERR_FINALIZATION_CONFLICT` | A finalized proposal is already converted to a booking |
| `422 Unprocessable Entity` | `ERR_BOOKING_IMMUTABLE` | Booking is closed or completed and cannot be mutated |
| `422 Unprocessable Entity` | `ERR_INVALID_STATUS_TRANSITION` | Requested status transition violates lifecycle matrix |
| `422 Unprocessable Entity` | `ERR_INSTALLMENTS_SUM_INVALID` | Installment percentage sum does not equal exactly 100.00% |
| `422 Unprocessable Entity` | `ERR_PROPOSAL_NOT_FINALIZED` | The linked proposal is not finalized |
