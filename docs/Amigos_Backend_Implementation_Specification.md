
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

---

## Phase 7 – CRM [PENDING]

### Objective
Deconstruct the Lead and activity log workflows.

### Deliverables
- Lead status, Lead Source, and Lead Assignment history logs
- CRM activity follow-ups tracking
- Note: Public lead submission (`create_lead` in `public_routes.py`) will remain unchanged.

### Acceptance
- Leads track assignment history logs correctly
- Lead status transitions validate properly

---

## Phase 8 – Proposal [PENDING]

### Objective
Isolate proposal building, versioning, and pricing.

### Deliverables
- Proposal versioning and day-by-day hotels/vehicles map
- Immutability locking rules upon proposal approval

### Acceptance
- Lock is enforced successfully on final proposal versions

---

## Phase 9 – Booking [PENDING]

### Objective
Implement split payment booking conversion transactions.

### Deliverables
- Booking, Traveler registration, and document uploads
- Payment schedule generation and validations (installments sum to 100%)
- Snapshot fields stored at booking creation time

### Acceptance
- Complete multi-table database transaction rollbacks validated on error

---

## Phase 10 – Operations [PENDING]

### Objective
Implement post-booking coordination and trip logistical checklists.

### Deliverables
- Trip Plan, Trip Day routing
- Vendor Allocation with active locks
- Operational Tasks checklist gating (booking completion blocked by checklist)

### Acceptance
- Check constraints and allocation locking verified

---

## Phase 11 – Finance [PENDING]

### Objective
Implement expense ledger tracking and dynamic P&L calculations.

### Deliverables
- Customer payments, vendor payments, and expense logs
- Expense mutability checks (deletions blocked when trip is completed)

### Acceptance
- Expenses lock correctly when booking status is marked closed

---

## Phase 12 – Notifications [PENDING]

### Objective
Deploy automated alerting channels.

### Deliverables
- Event-driven notifications (Email, WhatsApp, In-App alerts) triggered by Domain Event handlers

### Acceptance
- System alerts fire and log successfully when events are dispatched

---

## Phase 13 – Dashboard [PENDING]

### Objective
Expose operational overview metrics.

### Deliverables
- Pre-aggregated dashboard views (strictly read-only)

### Acceptance
- Sub-second load times for dashboard statistics

---

## Phase 14 – Reports [PENDING]

### Objective
Expose analytical report summaries.

### Deliverables
- CSV/PDF reporting engines for CRM, Finance, and Operations

### Acceptance
- Data export generation works on verified ranges

---

## Phase 15 – Historical Booking [PENDING]

### Objective
Isolate historical booking flows.

### Deliverables
- Dedicated historical service bypassing CRM and Proposal pipelines for retrofitting data

### Acceptance
- Admin-only historical entries save cleanly without triggering active notifications or tasks

---

## Phase 16 – Testing & Deployment [PENDING]

### Objective
Conduct final quality assurance and containerized deployment.

### Deliverables
- Dockerization (Dockerfile and docker-compose.yml configuration)
- Celery background workers setup
- Redis caching integration
- CI/CD deployment pipelines

### Acceptance
- 100% test coverage budget passing
- System deployed and accessible in staging/production

---

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
