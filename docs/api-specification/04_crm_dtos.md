# 04 CRM DTOs
## CRM Leads, Activities, and Follow-Up Lifecycle Schemas

> **Status: FROZEN — Implementation Complete (Phase 5)**
> This document defines the frozen API contracts, validation rules, field types, and lifecycle expectations for the CRM module.
> Last updated: 2026-08-02 to reflect completed implementation.

CRM is an independent business domain managing customer enquiries (Leads), client discussions (CRM Activities), scheduling next steps (Follow-ups), and auditing ownership changes (Assignment History).

All CRM endpoints are located under the route prefix: `/api/v1/leads` or `/api/v1/crm`.

---

# 1. API Endpoints Overview

| Method | URI Path | Role/Permission | Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/leads` | `crm.read` | List leads (paginated, sortable, filterable) |
| **GET** | `/api/v1/leads/{id}` | `crm.read` | Retrieve full detail of a specific lead |
| **POST** | `/api/v1/leads` | `crm.create` | Create a new lead (optionally creating contact person) |
| **PUT** | `/api/v1/leads/{id}` | `crm.update` | Update lead properties (requires `version` for optimistic lock) |
| **DELETE** | `/api/v1/leads/{id}` | `crm.delete` | Soft-delete a lead (`is_deleted = true`, pending followups cancelled) |
| **POST** | `/api/v1/leads/{id}/convert` | `crm.convert` | Convert Lead to a confirmed Booking |
| **GET** | `/api/v1/leads/{id}/activities` | `crm.read` | List all activities logged for a lead |
| **POST** | `/api/v1/leads/{id}/activities` | `crm.create` | Log a new client interaction activity |
| **GET** | `/api/v1/leads/{id}/followups` | `crm.read` | List all scheduled follow-ups for a lead |
| **POST** | `/api/v1/leads/{id}/followups` | `crm.create` | Schedule a new follow-up task |
| **PUT** | `/api/v1/leads/{id}/followups/{f_id}/complete` | `crm.update` | Mark a scheduled follow-up as completed |
| **GET** | `/api/v1/leads/{id}/assignments` | `crm.read` | Retrieve assignment history logs for a lead |
| **GET** | `/api/v1/contact-persons` | `crm.read` | List contact persons |
| **GET** | `/api/v1/contact-persons/{id}` | `crm.read` | Retrieve a specific contact person |
| **POST** | `/api/v1/contact-persons` | `crm.create` | Create or resolve a contact person (with deduplication) |
| **PUT** | `/api/v1/contact-persons/{id}` | `crm.update` | Update contact person details |
| **GET** | `/api/v1/crm/lookups/{lookup_type}` | `crm.read` | Fetch dropdown lookup values (Statuses, Sources, etc.) |

### Lookup Types
`/api/v1/crm/lookups/{lookup_type}` accepts any of:
- `statuses` -> `LeadStatus`
- `sources` -> `LeadSource`
- `priorities` -> `LeadPriority`
- `lost_reasons` -> `LeadLostReason`
- `activity_types` -> `CRMActivityType`
- `followup_types` -> `FollowUpType`

---

# 2. Lead Lifecycle Request DTOs

## 2.1 `CreateLeadRequest`

Ingested during manual lead creation by admin/agents.

> **Public Route Adapter**: For public lead submissions via `POST /api/v1/lead` (unauthenticated), a simplified flat payload mapping is performed inside `public_routes.py` to populate these fields without breaking the existing public contract.

| Field | Type | Required | Nullable | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `contact_person_id` | UUID | No* | Yes | Must reference active `ContactPerson` | Reference an existing contact person |
| `contact_person` | Object | No* | Yes | Nested object structure (see below) | Details to create a new `ContactPerson` |
| `lead_source_id` | UUID | Yes | No | Must reference active `LeadSource` | Where the lead originated from |
| `organization_division_id` | UUID | No | Yes | Must reference active `OrganizationDivision` | Linked division (for institutional clients) |
| `package_id` | UUID | No | Yes | Must reference active `Package` | Reference package from catalog |
| `trip_type_id` | UUID | No | Yes | Must reference active `TripType` | e.g. Couple, IV, Family |
| `priority_id` | UUID | No | Yes | Must reference active `LeadPriority` | e.g. High, Medium, Low |
| `travel_start_date` | Date | No | Yes | Format: `YYYY-MM-DD`. Must be >= today | Intended travel start |
| `travel_end_date` | Date | No | Yes | Format: `YYYY-MM-DD`. Must be >= start | Intended travel end |
| `estimated_trip_days` | Integer | No | Yes | Min: 1 | Number of days |
| `estimated_trip_nights` | Integer | No | Yes | Min: 0 | Number of nights |
| `traveler_count` | Integer | No | No | Min: 1. Default: 1 | Total number of travelers |
| `male_count` | Integer | No | Yes | Min: 0 | Number of male travelers |
| `female_count` | Integer | No | Yes | Min: 0 | Number of female travelers |
| `faculty_count` | Integer | No | Yes | Min: 0 | Number of faculty/teachers (for group tours) |
| `budget` | Decimal | No | Yes | Min: 0. Max: 12 digits, 2 decimals | Estimated budget |
| `notes` | String | No | Yes | Max length: 2000 | Custom notes/requirements |
| `expected_travel_date` | Date | No | Yes | Format: `YYYY-MM-DD` | If start/end dates are not fixed |
| `current_status_id` | UUID | No | No | Must reference active `LeadStatus` | Default is the ID for status `NEW` |
| `owner_team_member_id` | UUID | No | Yes | Must reference active `TeamMember` | Lead owner/handler |
| `destinations` | Array | No | No | List of `LeadDestinationRequest` items | Planned destinations (see below) |

> *Rule: Exactly one of `contact_person_id` OR `contact_person` must be specified.*

### Nested: `contact_person` Object

| Field | Type | Required | Nullable | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `name` | String | Yes | No | Max 150 |
| `phone` | String | Yes | No | Max 20, phone format |
| `email` | String | No | Yes | Email format |
| `designation` | String | No | Yes | Max 100 |
| `alternate_phone` | String | No | Yes | Max 20 |
| `preferred_contact_method` | String | No | Yes | Max 30 |
| `notes` | String | No | Yes | -- |

> **Deduplication Rule**: When resolving `ContactPerson` by phone, the service matches on the **last 10 digits** of normalized phone numbers. If a match is found, the existing contact person is linked without overwriting existing data (only filling in missing fields). A new `ContactPerson` record is created only if no match is found.

### Nested: `LeadDestinationRequest` Object

| Field | Type | Required | Nullable | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `destination_id` | UUID | Yes | No | Must reference active `Destination` |
| `priority` | String | No | Yes | Max 50, e.g., "High", "Medium", "Low" |
| `day_preference` | String | No | Yes | Max 50, e.g., "Day 1-2", "Last Day" |

```json
{
  "contact_person": {
    "name": "Jathin",
    "phone": "+919876543210",
    "email": "jathin@example.com",
    "designation": "Group Coordinator"
  },
  "lead_source_id": "00000000-0000-0000-0000-000000000001",
  "travel_start_date": "2026-10-15",
  "travel_end_date": "2026-10-18",
  "estimated_trip_days": 3,
  "estimated_trip_nights": 2,
  "traveler_count": 5,
  "budget": 25000.00,
  "notes": "Interested in premium hotels and a private vehicle.",
  "destinations": [
    {
      "destination_id": "00000000-0000-0000-0000-000000000005",
      "priority": "High"
    }
  ]
}
```

---

## 2.2 `UpdateLeadRequest`

Used to modify details or record lifecycle status updates. Requires the current `version` parameter for optimistic concurrency locking.

| Field | Type | Required | Nullable | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `version` | Integer | **Yes** | No | Must match database record `version`. Mismatch -> `ERR_CONCURRENT_MODIFICATION` (409) | Enforces optimistic locking |
| `contact_person_id` | UUID | No | Yes | Must reference active `ContactPerson` | Re-bind lead to another contact person |
| `lead_source_id` | UUID | No | No | Must reference active `LeadSource` | Modify source channel |
| `organization_division_id` | UUID | No | Yes | Must reference active `OrganizationDivision` | Linked division |
| `package_id` | UUID | No | Yes | Must reference active `Package` | Select different catalog package |
| `trip_type_id` | UUID | No | Yes | Must reference active `TripType` | Change trip type |
| `priority_id` | UUID | No | Yes | Must reference active `LeadPriority` | Adjust lead priority |
| `travel_start_date` | Date | No | Yes | Format: `YYYY-MM-DD` | Start date |
| `travel_end_date` | Date | No | Yes | Format: `YYYY-MM-DD` | End date |
| `estimated_trip_days` | Integer | No | Yes | Min: 1 | Days |
| `estimated_trip_nights` | Integer | No | Yes | Min: 0 | Nights |
| `traveler_count` | Integer | No | No | Min: 1 | Total count |
| `male_count` | Integer | No | Yes | Min: 0 | Male count |
| `female_count` | Integer | No | Yes | Min: 0 | Female count |
| `faculty_count` | Integer | No | Yes | Min: 0 | Faculty count |
| `budget` | Decimal | No | Yes | Min: 0 | Budget |
| `notes` | String | No | Yes | Max 2000 | Notes |
| `expected_travel_date` | Date | No | Yes | Format: `YYYY-MM-DD` | Expected date |
| `current_status_id` | UUID | No | No | Must reference active `LeadStatus`. Validates transition matrix | Update status |
| `owner_team_member_id` | UUID | No | Yes | Must reference active `TeamMember` | Re-assign ownership (triggers assignment log) |
| `destinations` | Array | No | No | Full replacement list (if provided) | Replaces all existing `LeadDestination` records |
| `lost_reason_id` | UUID | No | Yes | Required only if transitioning to `LOST` status | Reason why the lead was lost |
| `lost_date` | Date | No | Yes | Required only if transitioning to `LOST` status | Date the lead was lost |
| `assignment_reason` | String | No | Yes | Max 500. Logged in `AssignmentHistory` | Reason for reassignment |

### Status Transition Matrix

Valid transitions enforced by `CRMService`. Invalid transition -> `ERR_INVALID_LEAD_TRANSITION` (422).

```
NEW -> ASSIGNED -> CONTACTED -> REQUIREMENT_GATHERING -> PROPOSAL_SENT -> NEGOTIATION -> WON
                                                                                       -> LOST (from any state, with lost_reason_id)
```

---

## 2.3 `ConvertLeadRequest`

Used to convert a lead to a booking. Lead status transitions to `WON` inside the same transaction.

| Field | Type | Required | Nullable | Validation | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `trip_start_date` | Date | Yes | No | `YYYY-MM-DD`, must be future | Trip start date |
| `trip_end_date` | Date | Yes | No | `YYYY-MM-DD`, >= start | Trip end date |
| `total_amount` | Decimal | Yes | No | Min: 0, 12 digits, 2 decimals | Confirmed trip price |
| `booking_source_id` | UUID | Yes | No | Must reference active `BookingSource` | How the booking is sourced |
| `booking_type_id` | UUID | Yes | No | Must reference active `BookingType` | Trip category type |

---

# 3. Contact Person Request DTOs

## 3.1 `CreateContactPersonRequest`

| Field | Type | Required | Nullable | Validation | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `name` | String | Yes | No | Max 150 | Full name |
| `phone` | String | Yes | No | Max 20 | Primary phone number |
| `email` | String | No | Yes | Email format | Email address |
| `designation` | String | No | Yes | Max 100 | Job title / role |
| `alternate_phone` | String | No | Yes | Max 20 | Secondary contact number |
| `preferred_contact_method` | String | No | Yes | Max 30 | e.g. WhatsApp, Call, Email |
| `notes` | String | No | Yes | -- | Free-form notes |

## 3.2 `UpdateContactPersonRequest`

All fields from `CreateContactPersonRequest` are optional. No optimistic locking on `ContactPerson`.

---

# 4. CRM Activity and Follow-Up Request DTOs

## 4.1 `CreateCRMActivityRequest`

| Field | Type | Required | Nullable | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `activity_type_id` | UUID or String | Yes | No | UUID or type code (e.g. `"CALL"`) | Activity type |
| `activity_date` | DateTime | No | No | ISO UTC. Defaults to current server time | When the interaction occurred |
| `discussion_summary` | String | Yes | No | Max length: 2000 | Summary of the conversation |
| `outcome` | String | No | Yes | Max length: 500 | Result of the discussion |
| `next_action` | String | No | Yes | Max length: 500 | Next action item agreed |
| `next_followup_date` | Date | No | Yes | `YYYY-MM-DD`. Must be >= today | Scheduled followup date |

---

## 4.2 `CreateFollowUpRequest`

| Field | Type | Required | Nullable | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `followup_type_id` | UUID or String | Yes | No | UUID or type code (e.g. `"EMAIL"`) | Followup type |
| `scheduled_date` | DateTime | Yes | No | ISO UTC. Must be in the future | Date/time of the reminder |
| `notes` | String | No | Yes | Max length: 1000 | Instructions or context |
| `owner_team_member_id` | UUID | No | Yes | Must reference active `TeamMember` | Defaults to authenticated user |

---

## 4.3 `CompleteFollowUpRequest`

| Field | Type | Required | Nullable | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `completion_notes` | String | No | Yes | Max length: 1000. Also accepted as `notes` key | Concluding notes on execution |

> **Implementation Note**: The service accepts either `completion_notes` or `notes`. Completion text is appended to the notes column as `\n[Completed Notes]: <text>`. The response schema parses this suffix back into `completion_notes`.

---

# 5. Response DTOs

All responses use the standard envelope:
```json
{ "success": true, "message": "...", "data": { ... } }
```

Paginated list responses use:
```json
{ "success": true, "data": [...], "meta": { "page": 1, "page_size": 20, "total_records": 120, "total_pages": 6 }, "error": null, "validation_errors": [] }
```

## 5.1 `LeadSummaryResponse`

```json
{
  "id": "7a3b68fc-9102-4d2a-b78f-ef81cc8a4123",
  "lead_number": "AM-LD-2026-00045",
  "contact_person": { "id": "...", "name": "Jathin", "phone": "+919876543210", "email": "jathin@example.com" },
  "lead_source": { "id": "...", "code": "INSTAGRAM", "name": "Instagram" },
  "current_status": { "id": "...", "code": "ASSIGNED", "name": "Assigned" },
  "priority": { "id": "...", "code": "HIGH", "name": "High" },
  "travel_start_date": "2026-10-15",
  "travel_end_date": "2026-10-18",
  "traveler_count": 5,
  "budget": 25000.00,
  "owner_team_member_id": "11a8b9f0-22c1-4d11-8fa2-3c88b4f12d09",
  "created_at": "2026-08-01T12:00:00Z",
  "version": 1
}
```

## 5.2 `LeadDetailResponse`

```json
{
  "id": "7a3b68fc-9102-4d2a-b78f-ef81cc8a4123",
  "lead_number": "AM-LD-2026-00045",
  "contact_person": {
    "id": "...", "name": "Jathin", "designation": "Group Coordinator",
    "phone": "+919876543210", "alternate_phone": "+919876543211",
    "email": "jathin@example.com", "preferred_contact_method": "WhatsApp"
  },
  "lead_source": { "id": "...", "code": "INSTAGRAM", "name": "Instagram" },
  "package": { "id": "...", "title": "Munnar Deluxe Escape" },
  "trip_type": { "id": "...", "code": "FRIENDS_GROUP", "name": "Friends Group" },
  "priority": { "id": "...", "code": "HIGH", "name": "High" },
  "current_status": { "id": "...", "code": "ASSIGNED", "name": "Assigned" },
  "travel_start_date": "2026-10-15",
  "travel_end_date": "2026-10-18",
  "estimated_trip_days": 3,
  "estimated_trip_nights": 2,
  "traveler_count": 5,
  "male_count": 3,
  "female_count": 2,
  "faculty_count": 0,
  "budget": 25000.00,
  "notes": "Interested in premium hotels and a private vehicle.",
  "expected_travel_date": null,
  "lost_reason": null,
  "lost_date": null,
  "owner_team_member_id": "11a8b9f0-22c1-4d11-8fa2-3c88b4f12d09",
  "destinations": [
    { "id": "...", "destination_id": "...", "name": "Munnar", "priority": "High", "day_preference": "Day 1-2" }
  ],
  "version": 2,
  "audit_info": {
    "created_at": "2026-08-01T12:00:00Z",
    "created_by_team_member_id": "...",
    "updated_at": "2026-08-01T12:30:00Z",
    "updated_by_team_member_id": "..."
  }
}
```

## 5.3 `CRMActivityResponse`

```json
{
  "id": "d82ab91a-b31a-4dff-aa0f-c191a9bf139a",
  "lead_id": "7a3b68fc-9102-4d2a-b78f-ef81cc8a4123",
  "activity_type": { "id": "...", "code": "CALL", "name": "Phone Call" },
  "activity_date": "2026-08-01T12:15:00Z",
  "discussion_summary": "Followed up on Munnar hotel options.",
  "outcome": "Budget increased.",
  "next_action": "Send revised proposal.",
  "next_followup_date": "2026-08-03",
  "audit_info": { "created_at": "2026-08-01T12:15:00Z", "created_by_team_member_id": "..." }
}
```

## 5.4 `FollowUpResponse`

```json
{
  "id": "e2ba82fa-11ba-4f2a-89aa-92ba2cfa0901",
  "lead_id": "7a3b68fc-9102-4d2a-b78f-ef81cc8a4123",
  "followup_type": { "id": "...", "code": "CALL_BACK", "name": "Call Back" },
  "scheduled_date": "2026-08-03T10:00:00Z",
  "notes": "Call client to confirm hotel booking availability.",
  "is_completed": true,
  "completed_at": "2026-08-03T10:30:00Z",
  "completion_notes": "Confirmed availability. Will send updated quote.",
  "status": "completed",
  "owner_team_member_id": "11a8b9f0-22c1-4d11-8fa2-3c88b4f12d09",
  "audit_info": { "created_at": "2026-08-01T12:15:00Z", "created_by_team_member_id": "..." }
}
```

> **Virtual Fields**:
> - `status`: Derived from `is_completed` and `is_deleted` -> one of `"pending"`, `"completed"`, `"cancelled"`.
> - `completion_notes`: Parsed from the `[Completed Notes]: <text>` suffix appended to `notes` at completion time.

## 5.5 `AssignmentHistoryResponse`

```json
{
  "id": "8fa2bb2a-b11a-4cfa-ba0e-92c1fa0e21a2",
  "entity_type": "Lead",
  "entity_id": "7a3b68fc-9102-4d2a-b78f-ef81cc8a4123",
  "assignment_type": "Lead Owner",
  "previous_team_member": { "id": "...", "display_name": "Unassigned" },
  "new_team_member": { "id": "11a8b9f0-22c1-4d11-8fa2-3c88b4f12d09", "display_name": "Sales Executive A" },
  "reason": "Initial manual allocation upon intake",
  "effective_from": "2026-08-01T12:00:00Z",
  "effective_to": null,
  "entity_status": "Assigned"
}
```

---

# 6. Error Codes

| Code | HTTP | Trigger |
| :--- | :--- | :--- |
| `ERR_CONCURRENT_MODIFICATION` | 409 | `version` mismatch on update |
| `ERR_INVALID_LEAD_TRANSITION` | 422 | Illegal status transition attempted |
| `ERR_LEAD_NUMBER_GENERATION` | 500 | Sequential lead number generation failed after 3 retries |
| `ERR_NOT_FOUND` | 404 | Lead, ContactPerson, or FollowUp does not exist |
| `ERR_BAD_REQUEST` | 400 | Completing an already-completed followup |
| `ERR_VALIDATION` | 422 | Marshmallow schema validation failure |

---

# 7. Lead Numbering Convention

Sequential lead numbers are generated in the format: **`AM-LD-YYYY-XXXXX`**

- `AM` -- Application prefix
- `LD` -- Lead entity
- `YYYY` -- 4-digit calendar year
- `XXXXX` -- Zero-padded 5-digit sequence scoped per calendar year

On `IntegrityError` collision, the service retries up to **3 times**. If exhausted, `ERR_LEAD_NUMBER_GENERATION` (HTTP 500) is raised.
