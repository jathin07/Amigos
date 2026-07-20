
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
- schemas/request.py
- schemas/response.py

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

# Development Roadmap

## Phase 0 – Foundation & Core Platform

### Objective

Prepare the backend infrastructure.

### Deliverables

- Project structure
- extensions.py
- core/
- shared/
- utils/
- constants/
- permissions/
- integrations/
- Swagger/OpenAPI
- Environment configuration
- Logging
- Error handling
- Response wrappers

Acceptance:
- Project boots successfully
- Health endpoint works

---

## Phase 1 – Authentication

Implement:

- Login
- JWT
- Refresh Tokens
- RBAC
- Password Reset

Acceptance:
- Protected endpoints secured
- Admin and Team Member roles verified

---

## Phase 2 – Master Data

Implement master modules:

- Package
- Destination
- Vendor
- Organization
- Team

Acceptance:
- CRUD complete
- Soft delete implemented
- Validation complete

---

## Phase 3 – CRM

Implement:

- Lead
- CRM Activity
- Follow-ups
- Lead Assignment

Acceptance:
- Assignment history tracked
- CRUD and lifecycle validated

---

## Phase 4 – Proposal

Implement:

- Proposal
- Proposal Versioning
- Proposal Destinations
- Final Proposal

Acceptance:
- One final proposal per lead
- Proposal locking implemented

---

## Phase 5 – Booking

Implement:

- Booking
- Travelers
- Documents
- Payment Schedule
- Booking Status

Workflow:

Proposal Approved
→ Advance Payment
→ Booking Created
→ Booking Confirmed

Acceptance:
- Transactional booking creation
- Payment schedule validation
- Snapshot fields stored

---

## Phase 6 – Operations

Implement:

- Trip Plan
- Trip Days
- Vendor Allocation
- Checklist
- Tasks

Acceptance:
- Ready status requires completed checklist
- Vendor allocation locking enforced

---

## Phase 7 – Finance

Implement:

- Customer Payments
- Vendor Payments
- Expenses
- Profit Calculation

Acceptance:
- Derived financial reports
- Expense locking after completion

---

## Phase 8 – Historical Booking

Implement dedicated historical booking flow.

Acceptance:
- Admin only
- CRM bypassed
- Historical data preserved

---

## Phase 9 – Notifications

Implement:

- In-App Notifications
- Email Notifications
- Workflow subscriptions

---

## Phase 10 – Assignment

Implement:

- Lead Owner
- Operations Owner
- Trip Coordinator
- Assignment History

---

## Phase 11 – Dashboard

Implement operational dashboards.

---

## Phase 12 – Reports

Implement analytical reports.

---

## Phase 13 – Infrastructure

Implement:

- Redis
- Celery
- Docker
- Background Jobs

---

## Phase 14 – Testing & Deployment

Complete:

- Unit Tests
- Integration Tests
- Workflow Tests
- Deployment
- Production validation

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
