# 04 CRM DTOs
## CRM Leads, Activities, and Task Followup Schemas

---

## 1. Request DTOs

### 1.1 `CreateLeadRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_name` | string | Yes | No | Max length: 100 | None | `Jathin` |
| `phone` | string | Yes | No | Format: Phone | None | `9876543210` |
| `email` | string | No | Yes | Format: Email | None | `jathin@example.com` |
| `lead_source` | string | Yes | No | Enum: LeadSource (See 07 Enums Specification) | None | `Instagram` |

```json
{
  "customer_name": "Jathin",
  "phone": "9876543210",
  "email": "jathin@example.com",
  "lead_source": "Instagram"
}
```

### 1.2 `UpdateLeadRequest`
- Same fields as `CreateLeadRequest` but optional.

### 1.3 `CreateCRMActivityRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `activity_type` | string | Yes | No | Enum: ActivityType | None | `Call` |
| `remarks` | string | Yes | No | Max length: 500 | None | `Followed up on Munnar itinerary details` |

```json
{
  "activity_type": "Call",
  "remarks": "Followed up on Munnar itinerary details"
}
```

---

## 2. Response DTOs

### 2.1 `LeadSummaryResponse`
```json
{
  "id": "uuid-lead-1",
  "customer_name": "Jathin",
  "phone": "9876543210",
  "status": "New",
  "created_at": "2026-07-16T14:48:59Z"
}
```

### 2.2 `LeadDetailResponse`
```json
{
  "id": "uuid-lead-1",
  "customer_name": "Jathin",
  "phone": "9876543210",
  "email": "jathin@example.com",
  "lead_source": "Instagram",
  "status": "New",
  "created_at": "2026-07-16T14:48:59Z"
}
```

### 2.3 `CRMActivityResponse`
```json
{
  "id": "uuid-act-1",
  "lead_id": "uuid-lead-1",
  "activity_type": "Call",
  "remarks": "Followed up on Munnar itinerary details",
  "created_at": "2026-07-16T14:48:59Z"
}
```
