# 12 Proposal DTOs
## Custom Itinerary Proposal and Versioning Schemas

> **Status: FROZEN — Implementation Ready (Phase 6)**
> This document defines the frozen API contracts, validation rules, field types, and lifecycle expectations for the Proposal module.
> Last updated: 2026-08-02

The Proposal module is the commercial bridge between CRM and Booking. It manages versioned trip quotations, itinerary designs, and the finalization gate that unlocks Booking creation.

All Proposal endpoints are located under the route prefix: `/api/v1/proposals`.

---

# 1. Business Context

A Proposal is a sales document combining:
- A customized travel itinerary (`structured_itinerary` JSONB)
- Pricing per person and total amount
- A list of destinations with day-by-day plans
- Commercial terms (valid-until date, inclusions, revision reason)

### Key Business Rules

1. Multiple proposal versions may exist per Lead (`version` column, auto-incremented per `lead_id`).
2. Only **one** proposal may be marked `is_final = true` per Lead (enforced by DB partial unique index + service guard).
3. A finalized proposal is **completely immutable** — no updates, deletes, archives, destination edits, or version changes are permitted once `is_final = true`.
4. Finalization transitions status to `WAITING_FOR_ADVANCE` and emits `ProposalFinalized`.
5. A Booking links to exactly one finalized Proposal via `proposal_version_id`.
6. Proposal creation is blocked on `LOST` or `WON` leads.
7. `destinations` collections follow three-state update semantics (absent = unchanged, `[]` = clear, `[...]` = replace).

### Aggregate Boundary

`Proposal` is the aggregate root. `ProposalDestination` is a child entity.

> **Architectural Rule**: `ProposalDestination` must **never** be created, updated, or deleted directly. All creates, updates, and deletes to `ProposalDestination` must go through `ProposalService`. `ProposalDestinationRepository` is an internal implementation detail and must never be exposed outside the Proposal module.

### Proposal Status Lifecycle

```
DRAFT --> UNDER_DISCUSSION --> APPROVED --> WAITING_FOR_ADVANCE --> CONVERTED (terminal)
  |              |
  |           REVISED --> UNDER_DISCUSSION (loop)
  |
  +-----> ARCHIVED (terminal — any non-final, non-converted status)
```

| Status | Code | Description |
| :--- | :--- | :--- |
| Draft | `DRAFT` | Internal working document |
| Under Discussion | `UNDER_DISCUSSION` | Shared with client, actively negotiating |
| Revised | `REVISED` | Client requested changes, new iteration in progress |
| Approved | `APPROVED` | Client formally approved pricing |
| Waiting for Advance | `WAITING_FOR_ADVANCE` | Finalized; awaiting advance payment |
| Converted | `CONVERTED` | Advance received; Booking created from this Proposal |
| Archived | `ARCHIVED` | Superseded or deprecated |

### Finalization Immutability Lock

Once `is_final = true`, the Proposal enters a permanent lock state:

```
Finalized Proposal
  ├── PUT    /proposals/<id>          → 422 ERR_PROPOSAL_IMMUTABLE
  ├── DELETE /proposals/<id>          → 422 ERR_PROPOSAL_IMMUTABLE
  ├── POST   /proposals/<id>/finalize → 422 ERR_PROPOSAL_IMMUTABLE (already final)
  └── Destination edits              → 422 ERR_PROPOSAL_IMMUTABLE
```

No unlock mechanism exists. A new proposal version must be created instead.

### Version Race Condition Handling

Proposal versions are generated as `MAX(version) + 1` per `lead_id`. Under concurrent inserts, two requests may calculate the same version number. The unique constraint `uq_proposal_lead_version (lead_id, version)` on the database will cause a collision to fail with `IntegrityError`. The service retries up to **3 times** on collision before raising `ERR_PROPOSAL_VERSION_GENERATION` (HTTP 500).

---

# 2. Domain Models (DB Reference)

```
proposals
  id                          UUID PK
  lead_id                     UUID FK -> leads.id CASCADE
  version                     Integer NOT NULL              -- proposal sequence (1, 2, 3...) per lead
  row_version                 Integer NOT NULL DEFAULT 1   -- optimistic lock counter
  proposal_title              VARCHAR(200) NOT NULL
  price_per_person            NUMERIC(12,2)
  total_amount                NUMERIC(12,2)
  pdf_url                     TEXT
  internal_notes              TEXT
  structured_itinerary        JSONB
  revision_reason             TEXT
  sent_date                   DATE
  approved_date               DATE
  valid_until                 DATE
  approved_by_team_member_id  UUID FK -> team_members.id SET NULL
  is_final                    BOOLEAN NOT NULL DEFAULT FALSE
  status_id                   UUID FK -> proposal_statuses.id RESTRICT
  is_deleted                  BOOLEAN NOT NULL DEFAULT FALSE
  -- TimestampMixin: created_at, updated_at
  -- AuditMixin: created_by_team_member_id, updated_by_team_member_id

  UNIQUE (lead_id, version)
  PARTIAL UNIQUE INDEX (lead_id) WHERE is_final = TRUE

proposal_destinations
  id              UUID PK
  proposal_id     UUID FK -> proposals.id CASCADE
  destination_id  UUID FK -> destinations.id RESTRICT
  day_order       Integer
  sequence_no     Integer
  overnight_stay  BOOLEAN NOT NULL DEFAULT FALSE
  day_title       VARCHAR(150)
  travel_time     VARCHAR(100)
  travel_mode     VARCHAR(100)
  distance        NUMERIC(12,2)
  notes           TEXT
```

### DB Field Disambiguation

| Field | Role | Exposed in DTO as |
| :--- | :--- | :--- |
| `version` | Proposal sequence number (1, 2, 3...) | `version` |
| `row_version` | Optimistic lock counter | `row_version` |

---

# 3. Cross-Module Dependency Matrix

| Module | Access Type | Reason |
| :--- | :--- | :--- |
| CRM (`Lead`) | Read Only | Validate lead eligibility on proposal creation |
| Master (`Destination`) | Read Only | Validate `destination_id` in `ProposalDestination` |
| Team (`TeamMember`) | Read Only | Validate `approved_by_team_member_id` |
| Booking | Event Only | `ProposalFinalized` event unlocks Booking creation |
| Package | Optional Read | May reference a package from lead context (display only) |
| Finance | None | No direct interaction |

---

# 4. Domain Events

## `ProposalCreated` *(informational)*

Published after a new proposal version is committed to the database.

| Field | Type | Description |
| :--- | :--- | :--- |
| `proposal_id` | UUID | ID of the newly created proposal |
| `lead_id` | UUID | Associated lead |
| `version` | Integer | Proposal version number |
| `created_by` | UUID | Team member who created the proposal |
| `occurred_at` | ISO DateTime | UTC timestamp of event |

*Subscribers (future)*: Analytics, Audit, Notification

---

## `ProposalFinalized` *(critical)*

Published after `is_final = true` and status transition to `WAITING_FOR_ADVANCE` are committed. **Always published after commit, never before.**

| Field | Type | Description |
| :--- | :--- | :--- |
| `proposal_id` | UUID | ID of the finalized proposal |
| `lead_id` | UUID | Associated lead |
| `version` | Integer | Proposal version number |
| `approved_by` | UUID (nullable) | Team member who approved |
| `approved_date` | Date (nullable) | Date of approval |
| `total_amount` | Decimal | Agreed trip total |
| `occurred_at` | ISO DateTime | UTC timestamp of event |

*Subscribers*:
- **CRM**: Update lead status to `PROPOSAL_SENT` (future Phase 7 handler)
- **Booking**: Unlock booking creation against this proposal
- **Notification**: Trigger client notification workflow
- **Audit**: Log proposal approval audit trail

---

# 5. API Endpoints Overview

| Method | URI Path | Permission | Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/proposals` | `proposal.read` | List all proposals (paginated, filterable) |
| **GET** | `/api/v1/proposals/{id}` | `proposal.read` | Retrieve a specific proposal with destinations |
| **GET** | `/api/v1/leads/{lead_id}/proposals` | `proposal.read` | All proposal versions for a lead |
| **POST** | `/api/v1/proposals` | `proposal.create` | Create a new proposal version |
| **PUT** | `/api/v1/proposals/{id}` | `proposal.update` | Update a non-finalized proposal |
| **DELETE** | `/api/v1/proposals/{id}` | `proposal.delete` | Soft-delete a non-finalized proposal |
| **POST** | `/api/v1/proposals/{id}/finalize` | `proposal.finalize` | Finalize and lock the proposal |
| **GET** | `/api/v1/crm/lookups/proposal_statuses` | `proposal.read` | Proposal status lookup values |

### Permission Matrix

| Endpoint | Required Permission |
| :--- | :--- |
| `GET /proposals` | `proposal.read` |
| `GET /proposals/{id}` | `proposal.read` |
| `GET /leads/{id}/proposals` | `proposal.read` |
| `POST /proposals` | `proposal.create` |
| `PUT /proposals/{id}` | `proposal.update` |
| `DELETE /proposals/{id}` | `proposal.delete` |
| `POST /proposals/{id}/finalize` | `proposal.finalize` |

---

# 6. Request DTOs

## 6.1 `CreateProposalRequest`

| Field | Type | Required | Nullable | Validation | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `lead_id` | UUID | Yes | No | Active `Lead`. Not `LOST` or `WON` | Associated lead |
| `proposal_title` | String | Yes | No | Max 200 | Descriptive title |
| `price_per_person` | Decimal | No | Yes | Min: 0, 12 digits, 2 decimals | Per-person cost |
| `total_amount` | Decimal | No | Yes | Min: 0, 12 digits, 2 decimals | Total trip cost |
| `status_id` | UUID | No | No | Active `ProposalStatus`. Default: `DRAFT` | Initial status |
| `valid_until` | Date | No | Yes | `YYYY-MM-DD`. Must be >= today | Proposal expiry |
| `revision_reason` | String | No | Yes | Max 1000 | Why this version was created (for v2+) |
| `internal_notes` | String | No | Yes | Max 2000 | Agent-only notes |
| `structured_itinerary` | Object | No | Yes | Freeform JSON (see schema below) | Day-by-day itinerary |
| `destinations` | Array | No | Yes | List of `ProposalDestinationRequest` | Planned destinations |

### Nested: `ProposalDestinationRequest`

| Field | Type | Required | Nullable | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `destination_id` | UUID | Yes | No | Active `Destination` | Destination reference |
| `day_order` | Integer | No | Yes | Min: 1 | Which day this belongs to |
| `sequence_no` | Integer | No | Yes | Min: 1 | Order within a multi-stop day |
| `overnight_stay` | Boolean | No | No | Default: `false` | Client stays overnight |
| `day_title` | String | No | Yes | Max 150 | e.g. "Day 1: Munnar Arrival" |
| `travel_time` | String | No | Yes | Max 100 | e.g. "3 hours" |
| `travel_mode` | String | No | Yes | Max 100 | e.g. "Private Vehicle" |
| `distance` | Decimal | No | Yes | Min: 0 | Distance in km |
| `notes` | String | No | Yes | -- | Notes for this leg |

### Nested: `structured_itinerary` (Recommended Format)

```json
{
  "days": [
    {
      "day_number": 1,
      "title": "Arrival in Munnar",
      "date": "2026-10-15",
      "hotel": "Munnar Grand Resort",
      "meal_plan": "CP",
      "activities": [
        { "time": "10:00", "description": "Check-in at hotel", "type": "CHECK_IN" },
        { "time": "14:00", "description": "Visit Tea Museum", "type": "SIGHTSEEING" }
      ],
      "notes": "Client prefers ground floor room."
    }
  ],
  "inclusions": ["Hotel accommodation", "Private vehicle", "Driver allowance"],
  "exclusions": ["Flight tickets", "Personal expenses"],
  "terms": "50% advance required to confirm booking."
}
```

### Example Request

```json
{
  "lead_id": "7a3b68fc-9102-4d2a-b78f-ef81cc8a4123",
  "proposal_title": "Munnar Deluxe Escape - 3N/4D",
  "price_per_person": 12500.00,
  "total_amount": 62500.00,
  "valid_until": "2026-09-15",
  "internal_notes": "Client wants 4-star properties only.",
  "destinations": [
    {
      "destination_id": "00000000-0000-0000-0000-000000000005",
      "day_order": 1,
      "overnight_stay": true,
      "day_title": "Day 1: Arrival in Munnar",
      "travel_mode": "Private Vehicle"
    }
  ],
  "structured_itinerary": {
    "days": [{ "day_number": 1, "title": "Arrival in Munnar", "hotel": "Munnar Grand Resort", "meal_plan": "CP" }],
    "inclusions": ["Hotel", "Vehicle"],
    "exclusions": ["Flights"]
  }
}
```

---

## 6.2 `UpdateProposalRequest`

**Blocked if `is_final = true`** → `ERR_PROPOSAL_IMMUTABLE` (422).
Requires `row_version` for optimistic locking.

| Field | Type | Required | Nullable | Validation | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `row_version` | Integer | **Yes** | No | Must match DB `row_version`. Mismatch → `ERR_CONCURRENT_MODIFICATION` (409) | Optimistic lock |
| `proposal_title` | String | No | Yes | Max 200 | Updated title |
| `price_per_person` | Decimal | No | Yes | Min: 0 | Updated per-person price |
| `total_amount` | Decimal | No | Yes | Min: 0 | Updated total |
| `status_id` | UUID | No | Yes | Active `ProposalStatus`. Validates transition matrix | Status update |
| `valid_until` | Date | No | Yes | `YYYY-MM-DD`. Must be >= today | Expiry date |
| `revision_reason` | String | No | Yes | Max 1000 | Reason for revision |
| `internal_notes` | String | No | Yes | Max 2000 | Internal notes |
| `structured_itinerary` | Object | No | Yes | Freeform JSON | Full replacement |
| `destinations` | Array | No | Yes | See three-state rule below | Destination list |

### Destination Update Semantics (Three-State Rule)

| `destinations` value in request | Behavior |
| :--- | :--- |
| Key **absent** from body | Existing destinations remain unchanged |
| `[]` (empty array) | All existing destinations are cleared |
| `[...]` (non-empty array) | All existing destinations replaced |

> **Implementation Note**: The route must capture `request.json.keys()` **before** schema deserialization to detect key absence (same pattern as Package module).

---

## 6.3 `FinalizeProposalRequest`

| Field | Type | Required | Nullable | Validation | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `row_version` | Integer | **Yes** | No | Must match DB `row_version` | Optimistic lock |
| `approved_by_team_member_id` | UUID | No | Yes | Active `TeamMember` | Internal approver |
| `approved_date` | Date | No | Yes | `YYYY-MM-DD` | Date of formal approval |

**Finalization preconditions (all enforced by service before commit):**
1. Proposal must not already be `is_final = true` → `ERR_PROPOSAL_IMMUTABLE` (422)
2. `row_version` must match → `ERR_CONCURRENT_MODIFICATION` (409)
3. Status must be `APPROVED` → `ERR_INVALID_STATUS_TRANSITION` (422)
4. No other `is_final = true` proposal for same `lead_id` → `ERR_FINALIZATION_CONFLICT` (409)

**Post-commit actions (after successful commit):**
- `is_final` set to `true`
- Status transitions to `WAITING_FOR_ADVANCE`
- `ProposalFinalized` domain event published

---

# 7. Response DTOs

## 7.1 `ProposalSummaryResponse`

```json
{
  "id": "aa1c9bfa-1122-4a3b-b890-012abc3456de",
  "lead_id": "7a3b68fc-9102-4d2a-b78f-ef81cc8a4123",
  "version": 2,
  "proposal_title": "Munnar Deluxe Escape - 3N/4D (Revised)",
  "price_per_person": 12500.00,
  "total_amount": 62500.00,
  "is_final": false,
  "status": { "id": "...", "code": "UNDER_DISCUSSION", "name": "Under Discussion" },
  "valid_until": "2026-09-15",
  "sent_date": null,
  "approved_date": null,
  "row_version": 3,
  "audit_info": {
    "created_at": "2026-08-01T12:00:00Z",
    "created_by_team_member_id": "11a8b9f0-22c1-4d11-8fa2-3c88b4f12d09"
  }
}
```

---

## 7.2 `ProposalDetailResponse`

```json
{
  "id": "aa1c9bfa-1122-4a3b-b890-012abc3456de",
  "lead_id": "7a3b68fc-9102-4d2a-b78f-ef81cc8a4123",
  "version": 2,
  "proposal_title": "Munnar Deluxe Escape - 3N/4D (Revised)",
  "price_per_person": 12500.00,
  "total_amount": 62500.00,
  "is_final": false,
  "status": { "id": "...", "code": "UNDER_DISCUSSION", "name": "Under Discussion" },
  "valid_until": "2026-09-15",
  "sent_date": null,
  "approved_date": null,
  "approved_by_team_member_id": null,
  "revision_reason": "Client requested 4-star hotels.",
  "internal_notes": "Check hotel availability before sending.",
  "pdf_url": null,
  "structured_itinerary": {
    "days": [{ "day_number": 1, "title": "Arrival in Munnar", "hotel": "Munnar Grand Resort", "meal_plan": "CP" }],
    "inclusions": ["Hotel", "Vehicle"],
    "exclusions": ["Flights"],
    "terms": "50% advance required."
  },
  "destinations": [
    {
      "id": "bb2d0cfa-2233-4b4c-c901-123bcd4567ef",
      "destination_id": "00000000-0000-0000-0000-000000000005",
      "destination_name": "Munnar",
      "day_order": 1,
      "sequence_no": 1,
      "overnight_stay": true,
      "day_title": "Day 1: Arrival in Munnar",
      "travel_time": null,
      "travel_mode": "Private Vehicle",
      "distance": null,
      "notes": null
    }
  ],
  "row_version": 3,
  "audit_info": {
    "created_at": "2026-08-01T12:00:00Z",
    "created_by_team_member_id": "11a8b9f0-22c1-4d11-8fa2-3c88b4f12d09",
    "updated_at": "2026-08-02T09:30:00Z",
    "updated_by_team_member_id": "11a8b9f0-22c1-4d11-8fa2-3c88b4f12d09"
  }
}
```

---

## 7.3 `ProposalVersionListResponse`

Compact version history list for a given lead.

```json
[
  {
    "id": "aa1c9bfa-1122-4a3b-b890-012abc3456de",
    "version": 2,
    "proposal_title": "Munnar Deluxe Escape - 3N/4D (Revised)",
    "total_amount": 62500.00,
    "status": { "code": "UNDER_DISCUSSION", "name": "Under Discussion" },
    "is_final": false,
    "created_at": "2026-08-02T09:00:00Z"
  },
  {
    "id": "zz9f8eba-0011-4a3b-b890-009xyz1234ab",
    "version": 1,
    "proposal_title": "Munnar Deluxe Escape - 3N/4D",
    "total_amount": 55000.00,
    "status": { "code": "ARCHIVED", "name": "Archived" },
    "is_final": false,
    "created_at": "2026-08-01T12:00:00Z"
  }
]
```

---

# 8. Error Codes

| Code | HTTP | Trigger |
| :--- | :--- | :--- |
| `ERR_CONCURRENT_MODIFICATION` | 409 | `row_version` mismatch on update or finalize |
| `ERR_PROPOSAL_IMMUTABLE` | 422 | Any mutation attempted on a finalized proposal |
| `ERR_INVALID_STATUS_TRANSITION` | 422 | Illegal status transition, or finalize on non-APPROVED proposal |
| `ERR_FINALIZATION_CONFLICT` | 409 | Another `is_final=true` proposal already exists for this lead |
| `ERR_LEAD_INELIGIBLE` | 422 | Proposal creation on a `LOST` or `WON` lead |
| `ERR_PROPOSAL_VERSION_GENERATION` | 500 | Version number collision after 3 retries |
| `ERR_NOT_FOUND` | 404 | Proposal or ProposalDestination does not exist |
| `ERR_VALIDATION` | 422 | Schema validation failure |

---

# 9. Status Transition Matrix

| From | Allowed To |
| :--- | :--- |
| `DRAFT` | `UNDER_DISCUSSION`, `ARCHIVED` |
| `UNDER_DISCUSSION` | `REVISED`, `APPROVED`, `ARCHIVED` |
| `REVISED` | `UNDER_DISCUSSION`, `ARCHIVED` |
| `APPROVED` | `UNDER_DISCUSSION` (un-approve), `WAITING_FOR_ADVANCE` (via finalize only) |
| `WAITING_FOR_ADVANCE` | `CONVERTED` (via Booking creation — not a direct API action) |
| `CONVERTED` | *(terminal)* |
| `ARCHIVED` | *(terminal)* |
