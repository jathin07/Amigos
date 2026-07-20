# 05 Proposal DTOs
## Custom Itinerary Proposal and Versions History Schemas

---

## 1. Request DTOs

### 1.1 `CreateProposalRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `lead_id` | string | Yes | No | Format: UUID | None | `uuid-lead-1` |
| `title` | string | Yes | No | Max length: 100 | None | `Custom Munnar Trip` |
| `price_quoted` | decimal | Yes | No | `> 0` | None | `12500.00` |
| `destinations` | list | Yes | No | List of destinations | None | `[]` |

```json
{
  "lead_id": "uuid-lead-1",
  "title": "Custom Munnar Trip",
  "price_quoted": 12500.00,
  "destinations": [
    {
      "destination_id": "uuid-dest-1",
      "day_number": 1,
      "overnight_stay": true
    }
  ]
}
```

### 1.2 `UpdateProposalRequest`
- All fields from `CreateProposalRequest` are supported but marked as optional.

---

## 2. Response DTOs

### 2.1 `ProposalSummaryResponse`
```json
{
  "id": "uuid-proposal-1",
  "lead_id": "uuid-lead-1",
  "title": "Custom Munnar Trip",
  "price_quoted": 12500.00,
  "is_final": false
}
```

### 2.2 `ProposalDetailResponse`
```json
{
  "id": "uuid-proposal-1",
  "lead_id": "uuid-lead-1",
  "title": "Custom Munnar Trip",
  "price_quoted": 12500.00,
  "is_final": false,
  "status": "Draft",
  "destinations": [
    {
      "id": "uuid-proposal-dest-1",
      "destination_id": "uuid-dest-1",
      "name": "Munnar",
      "day_number": 1,
      "overnight_stay": true
    }
  ],
  "created_at": "2026-07-16T14:48:59Z"
}
```

### 2.3 `ProposalVersionResponse`
```json
{
  "version": 1,
  "proposal_id": "uuid-proposal-1",
  "price_quoted": 12500.00,
  "created_at": "2026-07-16T14:48:59Z",
  "created_by": "uuid-tm-1"
}
```
