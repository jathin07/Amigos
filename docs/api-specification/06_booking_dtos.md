# 06 Booking DTOs
## Operational Booking Aggregate Schemas

---

## 1. Request DTOs

### 1.1 `CreateBookingRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `proposal_id` | string | Yes | No | Format: UUID | None | `uuid-proposal-1` |
| `travelers` | list | Yes | No | List of travelers | None | `[]` |
| `installments` | list | Yes | No | Sum == 100% | None | `[]` |

```json
{
  "proposal_id": "uuid-proposal-1",
  "travelers": [
    {
      "name": "Arjun",
      "age": 28,
      "gender": "Male"
    }
  ],
  "installments": [
    {
      "percentage": 50.0,
      "due_date": "2026-08-01"
    },
    {
      "percentage": 50.0,
      "due_date": "2026-09-01"
    }
  ]
}
```

### 1.2 `UpdateBookingRequest`
- All fields from `CreateBookingRequest` are supported but marked as optional.

### 1.3 `TravelerRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `name` | string | Yes | No | Max length: 100 | None | `Arjun` |
| `age` | integer | Yes | No | `> 0` | None | 28 |
| `gender` | string | Yes | No | Enum: Gender | None | `Male` |

```json
{
  "name": "Arjun",
  "age": 28,
  "gender": "Male"
}
```

---

## 2. Response DTOs

### 2.1 `BookingSummaryResponse`
```json
{
  "id": "uuid-booking-1",
  "booking_code": "AMT-2026-0001",
  "status": "Waiting Confirmation"
}
```

### 2.2 `BookingDetailResponse`
```json
{
  "id": "uuid-booking-1",
  "booking_code": "AMT-2026-0001",
  "proposal_id": "uuid-proposal-1",
  "status": "Waiting Confirmation",
  "travelers": [
    { "id": "uuid-trv-1", "name": "Arjun", "age": 28, "gender": "Male" }
  ],
  "payment_schedule": [
    { "id": "uuid-inst-1", "percentage": 50.0, "due_date": "2026-08-01", "is_paid": false }
  ],
  "created_at": "2026-07-16T14:48:59Z"
}
```

### 2.3 `BookingTimelineResponse`
```json
{
  "booking_id": "uuid-booking-1",
  "timeline_events": [
    {
      "event_type": "BOOKING_CREATED",
      "timestamp": "2026-07-16T14:48:59Z",
      "description": "Booking created after advance deposit confirmation."
    }
  ]
}
```
