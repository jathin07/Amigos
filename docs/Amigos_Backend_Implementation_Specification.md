
# Amigos Tourism Backend Implementation Specification
## Domain-Event-Driven Modular API Roadmap (Antigravity Edition)

> This document is the implementation contract for backend development.
> The database schema, business workflow, folder structure, and domain architecture are considered **frozen**.
> Development must extend the architecture rather than redesign it.

---

# Global Implementation Constraints

The following components must **not** be modified unless explicitly requested:

- Database Schema
- Folder Structure
- Domain Modules
- Workflow Architecture
- Dependency Rules
- Business Workflow
- Naming Conventions

**Monolith Migration Scope Constraints**:
- Only monolithic endpoints inside `admin_routes.py` are within the scope of modularization/migration.
- Legacy `public_routes.py` must remain completely intact and unchanged. Public endpoints (such as public package/destination listings and lead creation) are not to be migrated or removed.

---

# Global Engineering Rules

1. Routes → Services → Workflow (cross-module only) → Services → Repositories → Database.
2. Routes never access repositories directly.
3. Workflow handlers never access models or repositories directly.
4. Repositories contain data access only.
5. Business logic belongs only in services.
6. Cross-module updates must be performed through Domain Events.
7. Every API must use `/api/v1/`.
8. Every feature must include validation, tests, and Swagger/OpenAPI documentation.

---

# Standard Module Implementation Template

Every module must follow this implementation structure.

## Objective

Describe the business purpose of the module.

## Prerequisites

List completed phases required before implementation.

## Folder Structure

Create:

- routes.py
- service.py
- repository.py
- validator.py
- schemas.py (or schemas/request.py and schemas/response.py for complex modules)

## Database Models

List all models used by the module.

## APIs

List REST endpoints.

## Services

Describe service responsibilities.

## Repository

Describe repository responsibilities.

## Validators

Describe validation rules.

## Workflow Events

List published and subscribed events.

## Tests

- Unit Tests
- Integration Tests
- Workflow Tests

## Acceptance Criteria

- APIs working
- Validation complete
- Workflow integrated
- Tests passing
- Swagger updated

## Definition of Done

- [ ] Folder created
- [ ] Repository completed
- [ ] Service completed
- [ ] Validator completed
- [ ] Schemas completed
- [ ] Routes completed
- [ ] Workflow integrated
- [ ] Tests completed
- [ ] API documented
- [ ] Ready for next phase

---

# Proposed Backend Module Architecture (v3)

To ensure high cohesion (related things stay together) and low coupling (modules communicate through APIs/events, not direct dependencies), the application backend boundaries are refined into the following modules.

## Module Directory Structure

```text
app/
│
├── api/
│
├── core/
│
├── common/
│
├── domain/
│
├── infrastructure/
│
├── workflow/
│
├── integrations/
│
└── modules/
    │
    ├── auth/                  # Authentication, User Accounts, JWT, RBAC
    │
    ├── organization/          # Company Profile, divisions, branding, invoicing configs
    │
    ├── team/                  # TeamMember profile, employee/team management
    │
    ├── master/                # Reusable reference/configuration data (Geo data, lookups)
    │
    ├── vendor/                # Vendor profiles, rates, bank details
    │
    ├── crm/                   # Lead lifecycle, CRM activity, follow-ups
    │
    ├── proposal/              # Proposal creation, versioning, approvals
    │
    ├── package/               # Package catalog, pricing, day plans, inclusions/exclusions
    │
    ├── booking/               # Confirmed bookings, travelers, schedules
    │
    ├── operations/            # Trip plans, checklists, tasks, vendor allocations
    │
    ├── finance/               # Expense tracking, payments, refunds, invoicing
    │
    ├── notifications/         # Notification channels (Email, WhatsApp, SMS, In-App)
    │
    ├── dashboard/             # Aggregated operational widgets (Read-only)
    │
    ├── reports/               # Analytical business reports (Read-only)
    │
    └── historical_booking/    # Dedicated admin-only historical booking flow
```

## Module Boundaries and Responsibilities

### 1. Authentication Module (`modules/auth/`)
Owns: Login, logout, token refresh, UserAccount, Role, Permission, password management, JWT configurations, and RBAC.

### 2. Organization Module (`modules/organization/`)
Owns: Organization config, divisions/branches, contact information, company branding, invoice configuration, and business configurations. Designed for single organization setup but conceptually separated.

### 3. Team Module (`modules/team/`)
Owns: TeamMember profiles, employee/team management, designations, reporting relationships, and employee information. Authentication credentials remain owned by `modules/auth/`. TeamMember and UserAccount remain separate concepts.

### 4. Master Module (`modules/master/`)
Contains only reusable static reference and configuration data:
- Geo data: Country, State, District, City, Destination
- Lookups: Currency, Payment Method, Meal Plan, Vehicle Type, Activity Type, Package Category, Hotel Category, Cancellation Policy, Tax Configuration

### 5. Vendor Module (`modules/vendor/`)
Owns: Vendor registration, contact details, services, GST/tax details, bank account details, and allocations. Vendor is a core business domain and is not placed under master reference data.

### 6. Package Module (`modules/package/`)
Owns: Package catalog, day plans, price configurations, highlights, inclusions, exclusions, and policies. Package is a business domain, not static reference data.

### 7. CRM Module (`modules/crm/`)
Owns: Lead, Lead Source, Lead Assignment, CRM Activity, Notes, Follow-Ups, and Tags.

### 8. Proposal Module (`modules/proposal/`)
Owns: Proposal, Proposal Version, Proposal Day, Proposal Hotels, Proposal Vehicles, Proposal Pricing, and Proposal Approval.

### 9. Booking Module (`modules/booking/`)
Owns customer commitments: Booking, Traveller, Documents, Payment Schedule, Booking Status, Snapshots (storing values at booking time), and Special Requests.

### 10. Operations Module (`modules/operations/`)
Manages everything after booking confirmation: Trip Plan, Trip Day, Vendor Allocation, Checklist, Tasks, Room/Vehicle/Guide allocations.

### 11. Finance Module (`modules/finance/`)
Owns financial flows: Customer Payments, Vendor Payments, Expenses, Profit/Loss calculations, Refunds, Invoices, and Receipts.

### 12. Notifications Module (`modules/notifications/`)
Exposes: Email, WhatsApp, SMS, In-App notification channels and templates.

### 13. Dashboard Module (`modules/dashboard/`)
Only aggregated queries for landing operational widgets. Strictly read-only; contains no business logic.

### 14. Reports Module (`modules/reports/`)
Analytical business reports. Strictly read-only; no writes.

---

## Dependency Graph & Rules

Modules must strictly follow top-down dependency rules. Reverse dependencies are prohibited.

### Dependency Graph

```text
       Master
       ▲  ▲  ▲
       │  │  │
Organization │ │
       ▲     │ │
       │     │ │
      Auth   │ │
       ▲     │ │
       │     │ │
     Team────┘ │
       ▲       │
       │       │
      CRM      │
       │       │
       ▼       │
    Proposal───┘
       │
       ▼
    Booking
     │   │
     │   ▼
     │  Vendor
     │   ▲
     ▼   │
  Operations
     │
     ▼
  Finance
```

### Allowed Module Dependencies

- **Team** $\rightarrow$ Master
- **Vendor** $\rightarrow$ Master
- **Package** $\rightarrow$ Master
- **CRM** $\rightarrow$ Auth, Team, Master
- **Proposal** $\rightarrow$ CRM, Package, Master
- **Booking** $\rightarrow$ Proposal, Master
- **Operations** $\rightarrow$ Booking, Vendor, Master
- **Finance** $\rightarrow$ Booking, Operations, Vendor

---

## Domain Events Workflow

Workflow coordination across module boundaries must occur exclusively through Domain Events:

```text
CRM (Lead Won)
     │
     ▼
Proposal (Proposal Finalized)
     │
     ▼
Booking (Booking Confirmed)
     │
     ▼
Operations (Trip Completed)
     │
     ▼
Finance (Payment Received)
     │
     ▼
Notifications
```

## Module Classification Matrix

| Module | Type | CRUD Only | Workflow | Domain Events | Complexity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth** | Core | ❌ | ✅ | ✅ | High |
| **Organization** | Configuration | ✅ | ❌ | ❌ | Medium |
| **Team** | Configuration | ✅ | ❌ | ❌ | Medium |
| **Master** | Reference Data | ✅ | ❌ | ❌ | Medium |
| **Vendor** | Business | ❌ | ✅ | ✅ | High |
| **Package** | Business | ❌ | ✅ | Future | High |
| **CRM** | Business | ❌ | ✅ | ✅ | High |
| **Proposal** | Business | ❌ | ✅ | ✅ | High |
| **Booking** | Business | ❌ | ✅ | ✅ | Very High |
| **Operations** | Business | ❌ | ✅ | ✅ | Very High |
| **Finance** | Business | ❌ | ✅ | ✅ | High |
| **Notifications** | Infrastructure | ❌ | Event-driven | ✅ | Medium |
| **Dashboard** | Read Model | Read Only | ❌ | ❌ | Low |
| **Reports** | Read Model | Read Only | ❌ | ❌ | Medium |

---

# Refined Development Roadmap

The development phases are organized sequentially based on the **dependency order** of the modular architecture.

## Phase 0 – Core Infrastructure [COMPLETED]

### Objective
Prepare the backend infrastructure.

### Deliverables
- Project structure (Completed)
- extensions.py (Completed)
- core/ (Completed)
- shared/ (Completed)
- utils/ (Completed)
- constants/ (Completed)
- permissions/ (Completed)
- integrations/ (Completed)
- Swagger/OpenAPI (Completed)
- Environment configuration (Completed)
- Logging (Completed)
- Error handling (Completed)
- Response wrappers (Completed)

### Acceptance
- Project boots successfully (Verified)
- Health endpoint works (Verified: `/api/v1/health` returns `200 OK`)

---

## Phase 1 – Authentication [COMPLETED]

### Objective
Secure the system and manage application credentials (JWT, RBAC).

### Deliverables
- Login (Completed under `app/modules/auth/`)
- JWT (Completed under `app/modules/auth/`)
- Refresh Tokens (Completed under `app/modules/auth/`)
- RBAC / Permissions (Completed under `app/modules/auth/` and `app/modules/auth/permissions.py`)
- Password Reset (Pending integration)

### Acceptance
- Protected endpoints secured (Verified)
- User accounts and session validation verified (Verified)

---

## Phase 2 – Organization [COMPLETED]

### Objective
Migrate company profile and business settings from the legacy codebase.

### Deliverables
- Organization profile CRUD (Completed under `app/modules/organization/`)
- Organization divisions/branches (Completed)
- Primary contact person association (Completed)
- Company branding and invoicing parameters (Completed)

### Acceptance
- CRUD complete (Verified)
- Business setup configurations verified (Verified)

---

## Phase 3 – Team [COMPLETED]

### Objective
Migrate TeamMember profile and employee/team management out of the legacy admin routes.

### Deliverables
- TeamMember profile CRUD (Completed under `app/modules/team/`)
- Designation and department lookup mappings (Completed)
- Reporting manager associations (Completed)
- Ensure credentials and profiles remain separate concepts (Completed)

### Acceptance
- CRUD complete (Verified)
- UserAccount separation verified (Verified)

---

## Phase 4 – Master Data [COMPLETED]

### Objective
Decompose static lookup tables and reference master data into the unified `master` module.

### Completed:
- **Geo Master Data**: Country, State, District, City, Destination (migrated to `app/modules/master/destination/`).
- **Consolidated Catalog Lookups**: 10 static/lookup entities (`PackageCategory`, `HotelCategory`, `MealPlan`, `VehicleType`, `ActivityType`, `Season`, `PaymentMethod`, `Currency`, `CancellationPolicy`, `TaxConfiguration`) implemented under `app/modules/master/routes.py` using `CatalogService`.

### Acceptance
- CRUD complete for all listed master modules (Verified)
- Soft delete implemented via `is_active = False` (Verified)
- Marshmallow validator schema validation complete (Verified)


---

## Phase 5 – Vendor [COMPLETED]

### Objective
Migrate Vendor profiles, rates, and contact details out of the legacy admin routes.

### Deliverables
- Vendor profile CRUD (Completed under `app/modules/vendor/`)
- Vendor contact details and type associations (Completed)
- Soft delete and optimistic locking validation (Completed)

### Acceptance
- CRUD complete (Verified)
- Separation from master data verified (Verified)

---

## Phase 6 – Package [COMPLETED]

### Objective
Deconstruct the Package catalog domain from the legacy codebase.

### Deliverables
- Package CRUD, highlights, inclusions, exclusions (Completed under `app/modules/package/`)
- Package images catalog (S3 upload ready) (Completed)
- Package destinations layout builder (Completed)
- Note: Public package listing endpoints in `public_routes.py` will remain unchanged. (Verified)

### Acceptance
- Packages build properly with correct associations and pricing rules (Verified)

#### Phase 7 – CRM [COMPLETED]
### Objective: Deconstruct the Lead and activity log workflows.
### Deliverables: Lead status, Lead Source, and Lead Assignment history logs. CRM activity follow-ups tracking. Public lead submission (`create_lead` in `public_routes.py`) remains unchanged.
### Acceptance: Leads track assignment history logs correctly. Lead status transitions validate properly. ✅ Verified.

## Phase 8 – Proposal [COMPLETED]
### Objective: Isolate proposal building, versioning, and pricing.
### Deliverables: Proposal versioning and day-by-day hotels/vehicles map. Immutability locking rules upon proposal approval.
### Acceptance: Lock is enforced successfully on final proposal versions. ✅ Verified.

## Phase 9 – Booking [COMPLETED]
### Objective: Implement split payment booking conversion transactions.
### Deliverables: Booking aggregate root, Traveler/Document/PaymentSchedule/BookingStatusHistory children, payment schedule generation, snapshot fields, full multi-table transaction rollback on error.
### Acceptance: Complete multi-table database transaction rollbacks validated on error. ✅ Verified. 413/413 tests passing.

---

## Phase 10 – Operations [PENDING]

### 10.1 Business Context
Operations is the execution backbone of Amigos Tourism. It starts **only** after a `Booking` is confirmed. It manages the daily logistics of every confirmed trip — from day-by-day routing and vendor allocation negotiations to checklist completion gates and task assignment.

The core business invariant is: **a booking cannot transition to `Ready` unless all checklist items are marked complete**. This prevents premature trip departures where logistics are unresolved.

### 10.2 Aggregate Root
- **Aggregate Root**: `TripPlan`
- **Children**: `TripDay`
- **Standalone Aggregates**: `VendorAllocation` (independent negotiation lifecycle), `Task` (independently assignable), `Checklist` (owned by Booking; completed through Operations)

**Aggregate Rules:**
- `TripPlan` is the Aggregate Root for trip execution planning.
- `TripDay` is a child entity; it cannot exist without a `TripPlan`.
- `VendorAllocation` belongs to a `TripDay` but operates as a standalone aggregate because vendor negotiations run independently.
- Endpoints for child entities must always be nested: `POST /trip-plans/{id}/days/{day_id}/allocations`, never standalone `POST /allocations`.
- All child mutations pass through `OperationsService`.
- Child repositories (`TripDayRepository`, `ChecklistRepository`) are internal implementation details and must not be exposed as standalone services.

### 10.3 TripPlan State Machine

```
Planning → Ready → Started → Ongoing → Completed → Closed
```

| Transition | Guard Condition |
| :--- | :--- |
| `Planning → Ready` | All `Checklist.is_completed = true`. All `VendorAllocation.is_locked = true`. |
| `Ready → Started` | Parent `Booking.status = Confirmed`. |
| `Ongoing → Completed` | No HIGH priority open Tasks. Manual trigger by Operations Owner. |
| `Completed → Closed` | `FinanceClosed` event received from Finance module. |

### 10.4 VendorAllocation State Machine

```
PENDING → NEGOTIATING → CONFIRMED → LOCKED → SETTLED
                                  ↘ FAILED
```

**Lock Rule:** Admin-level permission required to set `is_locked = true`. A locked allocation blocks all modifications without admin override.

### 10.5 Validation Rules

| Rule | Description | Error Code |
| :--- | :--- | :--- |
| Booking must be Confirmed | Cannot create TripPlan for unconfirmed booking | `BOOKING_NOT_CONFIRMED` |
| One active TripPlan per Booking | `UNIQUE INDEX` on `(booking_id, is_final=true)` | `TRIP_PLAN_ALREADY_EXISTS` |
| Service date within booking dates | `service_date` must fall within `trip_start_date` and `trip_end_date` | `SERVICE_DATE_OUT_OF_RANGE` |
| Confirmed price ≤ quoted × 1.10 | Anti-overrun guard (10% tolerance) | `ALLOCATION_PRICE_OVERRUN` |
| Locked allocation immutability | `is_locked = true` blocks all modifications | `VENDOR_ALLOCATION_LOCKED` |
| Checklist gating | Booking cannot be `Ready` unless all `Checklist.is_completed = true` | `CHECKLIST_INCOMPLETE` |
| Optimistic locking on TripPlan | `row_version` mismatch returns 409 | `CONCURRENT_UPDATE` |

### 10.6 Transaction Boundaries

| Transaction | Owner | Resources Modified | Published Event |
| :--- | :--- | :--- | :--- |
| Create TripPlan | OperationsService | `TripPlan`, `TripDay` (stubs) | None |
| Update TripDay | OperationsService | `TripDay` | None |
| Create VendorAllocation | OperationsService | `VendorAllocation` | None |
| Confirm VendorAllocation | OperationsService | `VendorAllocation.allocation_status_id`, `confirmed_price` | `VendorAllocationConfirmed` |
| Lock VendorAllocation | OperationsService | `VendorAllocation.is_locked` | None (admin-only) |
| Complete Checklist Item | OperationsService | `Checklist.is_completed`, `completed_at` | `ChecklistCompleted` (when all complete) |
| Complete Trip | OperationsService | `TripPlan.status_id`, `Booking.booking_status_id` | `TripCompleted` |

**Rollback Scope:** Each transaction is isolated to the Operation aggregate. Failure rolls back only the Operation aggregate changes. Finance and Booking modules are never in the same transaction.

### 10.7 Domain Events

**Published:**
- `TripCompleted` → Subscribers: Finance (lock expenses), Booking (update status), Notifications
- `ChecklistCompleted` → Subscribers: Notifications
- `VendorAllocationConfirmed` → Subscribers: Notifications

**Subscribed:**
- `BookingConfirmed` → Auto-create `TripPlan` stub; copy checklist items from `ChecklistTemplate`
- `FinanceClosed` → Transition `TripPlan` status to `CLOSED`

### 10.8 APIs

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/v1/operations/trip-plans` | List trip plans (filter: status, operations_owner_id) |
| `POST` | `/api/v1/operations/trip-plans` | Create trip plan for a confirmed booking |
| `GET` | `/api/v1/operations/trip-plans/{id}` | Get full trip plan detail with days and allocations |
| `PATCH` | `/api/v1/operations/trip-plans/{id}/days/{day_id}` | Update trip day details |
| `POST` | `/api/v1/operations/trip-plans/{id}/days/{day_id}/allocations` | Add vendor allocation to a day |
| `PATCH` | `/api/v1/operations/trip-plans/{id}/days/{day_id}/allocations/{alloc_id}/confirm` | Confirm vendor allocation |
| `PATCH` | `/api/v1/operations/trip-plans/{id}/days/{day_id}/allocations/{alloc_id}/lock` | Lock allocation (admin) |
| `POST` | `/api/v1/operations/trip-plans/{id}/complete` | Complete trip (publishes TripCompleted) |
| `GET` | `/api/v1/operations/trip-plans/{id}/checklist` | Get booking checklist with completion status |
| `PATCH` | `/api/v1/operations/trip-plans/{id}/checklist/{item_id}` | Mark checklist item complete/incomplete |
| `GET` | `/api/v1/operations/trip-plans/{id}/completion-check` | Validate if trip can be completed |
| `GET` | `/api/v1/operations/tasks` | List tasks (filter: booking_id, assignee, status) |
| `POST` | `/api/v1/operations/tasks` | Create task |
| `PATCH` | `/api/v1/operations/tasks/{id}/status` | Update task status |
| `POST` | `/api/v1/operations/tasks/bulk-assign` | Bulk assign tasks |

### 10.9 Error Catalogue

| Error Code | HTTP | Description |
| :--- | :--- | :--- |
| `TRIP_PLAN_ALREADY_EXISTS` | 409 | Second TripPlan attempted for booking with existing final plan |
| `BOOKING_NOT_CONFIRMED` | 409 | TripPlan creation for non-confirmed booking |
| `VENDOR_ALLOCATION_LOCKED` | 409 | Modification attempted on locked allocation |
| `CHECKLIST_INCOMPLETE` | 409 | Trip completion attempted with incomplete checklist |
| `ALLOCATION_PRICE_OVERRUN` | 422 | Confirmed price exceeds quoted × 1.10 |
| `SERVICE_DATE_OUT_OF_RANGE` | 422 | service_date outside booking trip dates |
| `CONCURRENT_UPDATE` | 409 | row_version mismatch on TripPlan |
| `TRIP_PLAN_NOT_FOUND` | 404 | UUID does not exist |
| `VENDOR_ALLOCATION_NOT_FOUND` | 404 | UUID does not exist |

### 10.10 Security Matrix

| Operation | Min Role |
| :--- | :--- |
| List/Get TripPlans | Operations Executive |
| Create TripPlan | Operations Executive |
| Update TripDay | Operations Executive (must be assigned owner) |
| Create/Confirm VendorAllocation | Operations Executive |
| Lock VendorAllocation | Admin only |
| Complete Trip | Operations Executive (assigned owner) |
| Complete Checklist Item | Trip Coordinator |
| Bulk Assign Tasks | Operations Executive |

### 10.11 Performance Considerations
- `TripPlanDetailResponse` includes trip days + allocations + checklist in a single response; use eager loading (`joinedload`) to avoid N+1 queries.
- Checklist completion rate is a derived count computed in the query; do not store it as a column.
- VendorAllocation `total_paid` and `balance_due` are computed properties on the model via relationship traversal; avoid calling them in list views — use a dedicated summary query instead.
- Add partial index: `WHERE is_final = TRUE` on `trip_plans(booking_id)` for fast active plan lookups.

### 10.12 Technical Debt
- **Checklist Templates**: Currently checklist items are manually created. Future: auto-copy from `ChecklistTemplate` when `BookingConfirmed` fires.
- **Trip Day Auto-Generation**: TripDays should be auto-scaffolded when TripPlan is created (one per night, based on `trip_start_date` to `trip_end_date`). Currently requires manual creation.
- **Vendor Overrun Alert**: The 10% overrun guard is a soft validation. Future: block entirely for non-admin users.

### 10.13 Definition of Done
- [ ] `app/modules/operations/` folder created
- [ ] `TripPlanRepository`, `VendorAllocationRepository`, `TaskRepository` completed
- [ ] `OperationsService` completed with all state machine transitions
- [ ] `ChecklistService` completed with gating logic
- [ ] `operations/routes.py` completed (`operations_bp`)
- [ ] `startup.py` registers `operations_bp`
- [ ] `TripCompleted` event published post-commit
- [ ] `BookingConfirmed` subscriber creates TripPlan stub
- [ ] Integration tests: 12+ test cases covering state machine, lock rules, checklist gating
- [ ] Swagger documented

---

## Phase 11 – Finance [PENDING]

### 11.1 Business Context
Finance manages all money flows for Amigos Tourism. It handles customer payment collection, vendor payment disbursements, on-trip expense logging, refund processing, and derived P&L calculations.

The central business invariant is: **expense records are locked from all modifications once the parent Booking status is `Completed` or `Closed`**. This creates an immutable financial ledger for completed trips, enabling accurate historical reporting.

Finance is also the trigger module for the `AdvanceReceived` event that initiates booking confirmation.

### 11.2 Aggregate Design

Finance uses **independent aggregate roots per financial record type**:

- **`Payment`** (Customer Payments) — Independent aggregate.
- **`VendorPayment`** (Vendor Disbursements) — Independent aggregate.
- **`Expense`** (Operational Expenses) — Independent aggregate.
- **`Refund`** (Customer Refunds) — Independent aggregate.

**Design Rationale:** Each money movement is an immutable ledger event. Bundling them into a single aggregate would create a massive, transaction-blocking aggregate that cannot scale. Independent aggregates allow concurrent recording without deadlocks.

**P&L Derivation:** Profit and Loss summaries are **never stored**. They are derived at query time from live ledger records.

### 11.3 Finance Lock State Machine

```
Booking Status: Completed / Closed
        ↓
Finance Lock: ACTIVE
        ↓
Expense Creation: BLOCKED (EXPENSE_LOCKED)
Expense Update:   BLOCKED (EXPENSE_LOCKED)
Expense Delete:   BLOCKED (EXPENSE_LOCKED)
VendorPayment:    BLOCKED (FINANCE_LOCKED)
Customer Payment: ✅ ALLOWED (outstanding balances may still be collected)
Refunds:          ✅ ALLOWED (post-trip refund processing continues)
```

### 11.4 Payment State Machine

```
PENDING → RECEIVED → VERIFIED
        ↘ FAILED
```

### 11.5 Refund State Machine

```
REQUESTED → APPROVED → PROCESSED → COMPLETED
          ↘ REJECTED
```

### 11.6 Validation Rules

| Rule | Description | Error Code |
| :--- | :--- | :--- |
| Expense lock on Completed/Closed | Block create/update/delete of expenses | `EXPENSE_LOCKED` |
| Finance lock on Completed/Closed | Block VendorPayment creation | `FINANCE_LOCKED` |
| Payment ≤ outstanding balance | Customer payment cannot exceed remaining balance | `PAYMENT_EXCEEDS_OUTSTANDING` |
| VendorPayment ≤ remaining balance | Vendor payment cannot exceed allocation balance due | `VENDOR_PAYMENT_EXCEEDS_BALANCE` |
| Refund ≤ total paid | Cumulative refunds cannot exceed total collected | `REFUND_EXCEEDS_PAID` |
| Finance close guard | No pending installments; no unsettled vendors | `PENDING_INSTALLMENTS_EXIST`, `VENDOR_PENDING_SETTLEMENTS` |
| Advance triggers Booking | First `RECEIVED` payment publishes `AdvanceReceived` | — |
| Payment amount > 0 | DB constraint: `CHECK (amount > 0)` | `INVALID_PAYMENT_AMOUNT` |
| Expense date not in future | `expense_date` must not be future-dated | `INVALID_EXPENSE_DATE` |
| Expense within booking dates | `expense_date >= trip_start_date` | `EXPENSE_DATE_OUT_OF_RANGE` |

### 11.7 Transaction Boundaries

| Transaction | Owner | Resources Modified | Published Event |
| :--- | :--- | :--- | :--- |
| Record Customer Payment | FinanceService | `Payment` | `AdvanceReceived` (first payment only) |
| Verify Payment | FinanceService | `Payment.payment_status_id`, `verified_by` | None |
| Record Vendor Payment | FinanceService | `VendorPayment` | None |
| Create Expense | FinanceService | `Expense` | None |
| Create Refund | FinanceService | `Refund` | None |
| Close Finance | FinanceService | `Booking.booking_status_id = CLOSED` | `FinanceClosed` |

**Rollback Scope:** Each financial transaction is independent. A VendorPayment rollback does not affect existing customer Payment records.

### 11.8 Domain Events

**Published:**
- `AdvanceReceived` → Subscribers: Booking (confirm booking), Notifications
- `FinanceClosed` → Subscribers: Operations (close TripPlan), Booking (status = Closed), Reports (sync read models), Notifications

**Subscribed:**
- `TripCompleted` → Activate Finance Lock (block new expenses and vendor payments)
- `BookingConfirmed` → Activate payment schedule tracking

### 11.9 APIs

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/v1/finance/bookings/{id}/payments` | List customer payments for a booking |
| `POST` | `/api/v1/finance/payments` | Record customer payment |
| `PATCH` | `/api/v1/finance/payments/{id}/verify` | Verify payment (admin) |
| `POST` | `/api/v1/finance/payments/{id}/receipt` | Upload payment receipt |
| `GET` | `/api/v1/finance/bookings/{id}/vendor-payments` | List vendor payments for a booking |
| `POST` | `/api/v1/finance/vendor-payments` | Record vendor payment disbursement |
| `GET` | `/api/v1/finance/bookings/{id}/expenses` | List expenses for a booking |
| `POST` | `/api/v1/finance/expenses` | Log operational expense |
| `DELETE` | `/api/v1/finance/expenses/{id}` | Delete expense (blocked if Finance Locked) |
| `GET` | `/api/v1/finance/bookings/{id}/refunds` | List refunds |
| `POST` | `/api/v1/finance/refunds` | Create refund |
| `GET` | `/api/v1/finance/bookings/{id}/profit-summary` | Get derived P&L summary |
| `GET` | `/api/v1/finance/bookings/{id}/installment-schedule` | Get installment schedule |
| `GET` | `/api/v1/finance/outstanding-payments` | List bookings with outstanding balances |
| `GET` | `/api/v1/finance/upcoming-installments` | List upcoming payment due dates |
| `GET` | `/api/v1/finance/pending-vendor-payments` | List pending vendor disbursements |
| `POST` | `/api/v1/finance/bookings/{id}/close` | Close finance (admin only) |

### 11.10 Error Catalogue

| Error Code | HTTP | Description |
| :--- | :--- | :--- |
| `EXPENSE_LOCKED` | 409 | Expense mutation when Booking is Completed/Closed |
| `FINANCE_LOCKED` | 409 | VendorPayment creation when Booking is Completed/Closed |
| `PAYMENT_EXCEEDS_OUTSTANDING` | 422 | Customer payment exceeds outstanding balance |
| `VENDOR_PAYMENT_EXCEEDS_BALANCE` | 422 | Vendor payment exceeds allocation balance due |
| `REFUND_EXCEEDS_PAID` | 422 | Cumulative refunds exceed total paid |
| `BOOKING_ALREADY_CLOSED` | 409 | Finance close on already-closed booking |
| `PENDING_INSTALLMENTS_EXIST` | 409 | Finance close with pending payment schedules |
| `VENDOR_PENDING_SETTLEMENTS` | 409 | Finance close with unsettled vendor allocations |
| `PAYMENT_NOT_FOUND` | 404 | UUID does not exist |
| `EXPENSE_NOT_FOUND` | 404 | UUID does not exist |

### 11.11 Security Matrix

| Operation | Min Role |
| :--- | :--- |
| Record Customer Payment | Finance Executive |
| Verify Payment | Admin |
| Upload Receipt | Finance Executive |
| Record Vendor Payment | Finance Executive |
| Create Expense | Trip Coordinator, Finance Executive |
| Delete Expense | Finance Executive (blocked if locked) |
| Create Refund | Admin |
| Get P&L Summary | Finance Executive, Admin |
| Close Finance | Admin only |

### 11.12 Performance Considerations
- P&L summary (`profit-summary` endpoint) joins Payment, VendorPayment, Expense, and Refund tables. Add `booking_id` indexes on all finance tables.
- Outstanding payments list must be paginated (max 200 per page). Do not return all rows in a single response.
- Upcoming installments: query `payment_schedules WHERE due_date >= today AND payment_status = PENDING` with an index on `due_date`.
- Finance summary endpoint result should be cached (5 minutes TTL, invalidated on `AdvanceReceived` or `TripCompleted`).

### 11.13 Technical Debt
- **Payment Receipt OCR**: Future improvement: OCR extraction from uploaded receipts for auto-verification.
- **Razorpay Integration**: Online payment collection is deferred to Phase 16 / Future Vision.
- **GST Calculation**: Tax handling on invoices and receipts is deferred to a future Finance 2.0 phase.
- **Automated Overdue Alerts**: Overdue payment schedule notifications require a scheduled Celery task (Phase 16 deliverable).

### 11.14 Definition of Done
- [ ] `app/modules/finance/` folder created
- [ ] `PaymentRepository`, `VendorPaymentRepository`, `ExpenseRepository`, `RefundRepository` completed
- [ ] `FinanceService` with Finance Lock enforcement, P&L derivation, finance close logic
- [ ] `finance/routes.py` completed (`finance_bp`)
- [ ] `startup.py` registers `finance_bp`
- [ ] `AdvanceReceived` event published post-commit
- [ ] `FinanceClosed` event published post-commit
- [ ] `TripCompleted` subscriber activates Finance Lock
- [ ] Integration tests: 15+ test cases covering lock rules, P&L derivation, guard conditions
- [ ] Swagger documented

---

## Phase 12 – Notifications [PENDING]

### 12.1 Business Context
The Notification module is a reactive infrastructure module. It never initiates business logic. It subscribes to Domain Events from business modules and delivers in-app notifications to the appropriate team members.

**Critical design rule:** Notification delivery failures (SMTP down, push token expired, WhatsApp API limit) must **never rollback parent business transactions**. The business transaction commits first; notifications are delivered asynchronously.

### 12.2 Module Classification
- **Type**: Infrastructure (Event-Driven, Reactive)
- **Aggregate Root**: `Notification` (each delivered notification is a stored record)
- **No business logic**: No state machines, no validation of business rules
- **No domain events published**: Consumes events, never produces them

### 12.3 Delivery Pipeline

```
Business Event → Workflow Engine → Notification Module
                                           ↓
                                   Template Resolution
                                           ↓
                                   Channel Selection
                                           ↓
                                   Delivery Attempt
                                           ↓
                                   Delivery History (stored in notifications table)
```

### 12.4 Delivery Channels

| Channel | Default | Notes |
| :--- | :--- | :--- |
| `IN_APP` | ✅ Always | Stored in `notifications` table; always delivered |
| `EMAIL` | ✅ Enabled | SMTP/SES; configurable per team member preference |
| `WHATSAPP` | ❌ Disabled | Requires WhatsApp Business API integration (Phase 16) |
| `SMS` | ❌ Disabled | Requires SMS gateway integration (Phase 16) |

### 12.5 Event Subscriptions

| Event | Source | Notification Generated |
| :--- | :--- | :--- |
| `LeadAssigned` | CRM | New lead assigned to team member |
| `ProposalFinalized` | Proposal | Proposal approved by customer |
| `AdvanceReceived` | Finance | Advance payment received |
| `BookingConfirmed` | Booking | Booking confirmed; operations can begin |
| `TripCompleted` | Operations | Trip completed; finance closure pending |
| `FinanceClosed` | Finance | Finance closed |
| `TaskAssigned` | Operations | Task assigned to team member |
| `ChecklistCompleted` | Operations | All checklist items completed |

### 12.6 APIs

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/v1/notifications` | List notifications for current user (paginated) |
| `GET` | `/api/v1/notifications/unread-count` | Get unread notification count |
| `PATCH` | `/api/v1/notifications/{id}/read` | Mark single notification as read |
| `POST` | `/api/v1/notifications/mark-all-read` | Mark all notifications as read |
| `DELETE` | `/api/v1/notifications/bulk` | Bulk dismiss notifications |
| `GET` | `/api/v1/notifications/preferences` | Get delivery preferences |
| `PATCH` | `/api/v1/notifications/preferences` | Update delivery preferences |

### 12.7 Definition of Done
- [ ] `app/modules/notifications/` folder created
- [ ] `NotificationRepository` completed (store, mark-read, bulk-dismiss)
- [ ] `NotificationService` with template resolution and channel routing
- [ ] All event subscribers registered and idempotent
- [ ] In-App delivery always succeeds synchronously
- [ ] Email delivery via async Celery task (fault-isolated)
- [ ] `notifications/routes.py` completed (`notifications_bp`)
- [ ] Integration tests: 8+ test cases
- [ ] Swagger documented

---

## Phase 13 – Dashboard [PENDING]

### 13.1 Business Context
The Dashboard module provides pre-aggregated, read-only operational widgets for the Amigos admin panel home page. It gives management a real-time snapshot of the business.

**Design constraints:**
- Strictly read-only: no writes, no domain events, no business logic.
- All queries must respond within **500ms** under normal load.
- Dashboard data has eventual consistency (acceptable 5–15 minute staleness for most widgets).

### 13.2 Module Classification
- **Type**: Read Model (Dashboard Consumer)
- **No Aggregate Root**: Pure query layer
- **No Domain Events**: No publications, no subscriptions (triggers via cache invalidation)
- **Data Source**: Reads from operational database or Redis-cached materialized summaries

### 13.3 Widget Inventory

| Widget | Endpoint | Cache TTL |
| :--- | :--- | :--- |
| Summary Cards | `GET /dashboard/widgets/summary-cards` | 5 min |
| Lead Pipeline | `GET /dashboard/widgets/lead-pipeline` | 5 min |
| Booking Pipeline | `GET /dashboard/widgets/booking-pipeline` | 5 min |
| Finance Summary | `GET /dashboard/widgets/finance-summary` | 5 min |
| Upcoming Trips | `GET /dashboard/widgets/upcoming-trips` | 15 min |
| Operations Overview | `GET /dashboard/widgets/operations-overview` | 10 min |
| Revenue Trend | `GET /dashboard/widgets/revenue-trend` | 30 min |

### 13.4 Performance Strategy
- All aggregate queries use pre-computed counts (never `SELECT *`).
- Complex widgets (revenue trend, operations overview) are computed asynchronously by Celery beat and cached in Redis.
- Simple counts (lead pipeline, booking pipeline) query directly with indexed filters.
- `as_of` timestamp in every response tells the client how fresh the data is.

### 13.5 APIs

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/v1/dashboard/widgets/summary-cards` | KPI summary cards |
| `GET` | `/api/v1/dashboard/widgets/lead-pipeline` | CRM funnel stages |
| `GET` | `/api/v1/dashboard/widgets/booking-pipeline` | Booking status distribution |
| `GET` | `/api/v1/dashboard/widgets/finance-summary` | Financial health overview |
| `GET` | `/api/v1/dashboard/widgets/upcoming-trips` | Trips starting in next 14 days |
| `GET` | `/api/v1/dashboard/widgets/operations-overview` | Coordinator workload |
| `GET` | `/api/v1/dashboard/widgets/revenue-trend` | Monthly revenue chart data |

### 13.6 Definition of Done
- [ ] `app/modules/dashboard/` folder created
- [ ] `DashboardService` with all widget query methods
- [ ] `dashboard/routes.py` completed (`dashboard_bp`)
- [ ] Redis caching integration for expensive widgets
- [ ] All widget responses include `as_of` timestamp
- [ ] Response time < 500ms verified under test load
- [ ] Integration tests: 7+ test cases (one per widget)
- [ ] Swagger documented

---

## Phase 14 – Reports [PENDING]

### 14.1 Business Context
The Reports module generates analytical summaries over historical business data. Unlike Dashboard widgets (real-time snapshots), reports operate over configurable date ranges and support CSV/PDF export for stakeholder review.

**Design constraints:**
- Strictly read-only: no writes, no business logic, no domain events.
- Date ranges bounded to 2 years maximum (performance limit).
- Simple reports (< 500 rows) respond synchronously.
- Large exports are generated asynchronously with a download link.
- No modification of operational data at any time.

### 14.2 Report Inventory

| Report | Endpoint | Audience |
| :--- | :--- | :--- |
| Finance P&L | `GET /reports/finance` | Admin, Finance Executive |
| CRM Conversion | `GET /reports/crm` | Admin, Sales Executive |
| Booking Trends | `GET /reports/bookings` | Admin |
| Customer History | `GET /reports/customer` | Admin, Sales Executive |
| Operations Efficiency | `GET /reports/operations` | Admin, Operations Executive |
| Vendor Payment | `GET /reports/vendor-payments` | Admin, Finance Executive |

### 14.3 APIs

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/v1/reports/finance` | Finance P&L report (date range) |
| `GET` | `/api/v1/reports/crm` | CRM lead conversion report |
| `GET` | `/api/v1/reports/bookings` | Booking trends by month/type |
| `GET` | `/api/v1/reports/customer` | Customer repeat booking analysis |
| `GET` | `/api/v1/reports/operations` | Checklist/coordinator efficiency |
| `GET` | `/api/v1/reports/vendor-payments` | Vendor disbursement tracking |

All endpoints accept query params: `date_from`, `date_to`, `format` (`json`/`csv`/`pdf`), `team_member_id`, `page`, `per_page`.

### 14.4 Export Strategy
- `format=json`: Standard JSON response.
- `format=csv`: `Content-Type: text/csv` with `Content-Disposition: attachment; filename=...`.
- `format=pdf`: Not implemented in Phase 14; returns `EXPORT_NOT_SUPPORTED`. Scheduled for Phase 16.

### 14.5 Definition of Done
- [ ] `app/modules/reports/` folder created
- [ ] `ReportsService` with all analytical query methods
- [ ] `reports/routes.py` completed (`reports_bp`)
- [ ] CSV export implemented for all report types
- [ ] Date range validation (max 2 years) enforced
- [ ] Role-based data scoping enforced (executives see own data; admin sees all)
- [ ] Integration tests: 6+ test cases (one per report type)
- [ ] Swagger documented

---

## Phase 15 – Historical Booking [PENDING]

### 15.1 Business Context
The Historical Booking module provides an admin-only mechanism to retrofit past bookings into the system. This is needed when the agency migrates from the old manual system and needs to backfill historical trip records without triggering active workflows.

**Critical design rules:**
- Historical bookings bypass the CRM → Proposal → Booking pipeline.
- They must **not** trigger `BookingConfirmed` events (no Operations tasks created).
- They must **not** trigger Notification events.
- They are created with `entry_mode = 'HISTORICAL'` on the `Booking` model.
- Admin-only endpoints.

### 15.2 Historical Booking Rules

| Rule | Constraint |
| :--- | :--- |
| Entry mode | `Booking.entry_mode = 'HISTORICAL'` |
| No proposal required | `proposal_version_id` may be null |
| No lead required | `lead_id` may be null |
| No workflow events | `BookingConfirmed` must not fire |
| No notifications | Notification module must not receive events |
| Admin only | Requires admin role |
| Manual status | Booking status set directly by admin |

### 15.3 APIs

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/api/v1/historical-bookings` | Create historical booking record |
| `GET` | `/api/v1/historical-bookings` | List historical bookings |
| `GET` | `/api/v1/historical-bookings/{id}` | Get historical booking detail |

### 15.4 Definition of Done
- [ ] `app/modules/historical_booking/` folder created
- [ ] `HistoricalBookingService` (no event publications)
- [ ] `historical_booking/routes.py` with admin-only guard
- [ ] `startup.py` registers `historical_booking_bp`
- [ ] Integration tests: 4+ test cases
- [ ] Swagger documented

---

## Phase 16 – Testing & Deployment [PENDING]

### 16.1 Objective
Conduct final quality assurance, achieve full test coverage, and prepare the production-ready containerized deployment stack.

### 16.2 Testing Deliverables

**Integration Test Suite (Target: 500+ total test cases)**
- Phase 10 (Operations): 12+ test cases (state machine transitions, lock rules, checklist gating, vendor allocation lifecycle)
- Phase 11 (Finance): 15+ test cases (Finance Lock enforcement, P&L derivation, payment guard conditions, refund limits)
- Phase 12 (Notifications): 8+ test cases (event subscription, delivery routing, preference filtering)
- Phase 13 (Dashboard): 7+ test cases (one per widget, performance timing)
- Phase 14 (Reports): 6+ test cases (one per report type, CSV export, date range validation)
- Phase 15 (Historical Booking): 4+ test cases (bypass pipeline, no event publication)

**End-to-End Pipeline Tests**
- Full workflow: Lead → Proposal → Booking → Operations → Finance (complete pipeline)
- Concurrency tests: Optimistic locking scenarios on `TripPlan` and `Booking`
- Finance Lock: Expense creation blocked after `TripCompleted` fires
- Domain Event propagation: `TripCompleted` → Finance Lock → `FinanceClosed` → Booking closed

### 16.3 Containerization Deliverables

**Dockerfile**
- Multi-stage build (builder + production image)
- Non-root user execution
- Health check endpoint configuration

**docker-compose.yml** — Services:
- `app` — Flask application (Gunicorn)
- `postgres` — PostgreSQL 15 with persistent volume
- `redis` — Redis 7 for caching and Celery broker
- `celery-worker` — Async notification delivery, expense jobs
- `celery-beat` — Scheduled tasks (overdue alerts, dashboard cache refresh)

### 16.4 Background Worker Tasks (Celery)

| Task | Schedule | Purpose |
| :--- | :--- | :--- |
| `refresh_dashboard_cache` | Every 5 minutes | Recompute summary cards, pipeline widgets |
| `send_overdue_payment_alerts` | Daily at 9AM | Notify finance team of overdue installments |
| `send_upcoming_installment_reminders` | Daily at 10AM | Remind customers of upcoming payment dues |
| `send_vendor_payment_reminders` | Daily at 10AM | Alert finance of pending vendor disbursements |
| `upcoming_trip_briefing` | Daily at 8AM | Send coordinator trip briefing for next 3 days |

### 16.5 Redis Integration

| Cache Key | TTL | Purpose |
| :--- | :--- | :--- |
| `dashboard:summary_cards:{org}` | 5 min | Summary cards widget |
| `dashboard:lead_pipeline:{org}` | 5 min | CRM funnel widget |
| `dashboard:booking_pipeline:{org}` | 5 min | Booking status widget |
| `dashboard:finance_summary:{org}` | 5 min | Finance overview widget |
| `dashboard:revenue_trend:{org}` | 30 min | Monthly revenue chart |
| `finance:profit_summary:{booking_id}` | 5 min | P&L summary per booking |

### 16.6 CI/CD Pipeline

- **Trigger**: Every pull request → Run full test suite
- **Merge to `main`** → Deploy to staging environment
- **Tagged release** (`v1.x.x`) → Deploy to production
- **Required checks**: All tests passing, zero critical vulnerabilities in dependency scan, Swagger valid

### 16.7 Acceptance Criteria
- All test cases passing (500+ total)
- Zero test failures in final integration run
- Container starts successfully with all services healthy
- All dashboard widget endpoints respond < 500ms
- Swagger documentation complete and accurate for all modules
- Staging deployment accessible and verified
- Production deployment completed on tagged release



# Workflow Engine Rules

Workflow handlers must:

- Validate event preconditions
- Call services only
- Never access repositories directly
- Never manipulate models directly
- Publish follow-up events where necessary

---

# Development Checklist (Every Feature)

1. Requirement Review
2. API Design
3. Schema Creation
4. Validator
5. Repository
6. Service
7. Route
8. Workflow Integration
9. Tests
10. Swagger Documentation
11. Code Review
12. Merge
