# 07 Operations DTOs
## Operational Trip Planning, Vendor Allocation, and Checklist Schemas

---

## 1. Request DTOs

### 1.1 `CreateTripPlanRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `booking_id` | string | Yes | No | Format: UUID | None | `uuid-booking-1` |
| `start_date` | string | Yes | No | Format: Date | None | `2026-08-10` |
| `end_date` | string | Yes | No | Format: Date | None | `2026-08-13` |

```json
{
  "booking_id": "uuid-booking-1",
  "start_date": "2026-08-10",
  "end_date": "2026-08-13"
}
```

### 1.2 `VendorAllocationRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `vendor_id` | string | Yes | No | Format: UUID | None | `uuid-vendor-1` |
| `trip_day_id` | string | Yes | No | Format: UUID | None | `uuid-trip-day-1` |
| `quoted_amount` | decimal | Yes | No | `> 0` | None | 6000.00 |
| `confirmed_price`| decimal | Yes | No | `> 0` | None | 5500.00 |

```json
{
  "vendor_id": "uuid-vendor-1",
  "trip_day_id": "uuid-trip-day-1",
  "quoted_amount": 6000.00,
  "confirmed_price": 5500.00
}
```

---

## 2. Response DTOs

### 2.1 `TripPlanDetailResponse`
```json
{
  "id": "uuid-trip-plan-1",
  "booking_id": "uuid-booking-1",
  "trip_status": "Planning",
  "operations_owner_id": "uuid-tm-1",
  "start_date": "2026-08-10",
  "end_date": "2026-08-13",
  "days": [
    { "id": "uuid-trip-day-1", "day_number": 1, "description": "Arrive at hotel, evening tea valley trekking" }
  ],
  "checklist": [
    { "id": "uuid-chk-1", "task_name": "Verify driver details", "is_completed": false }
  ]
}
```

### 2.2 `VendorAllocationResponse`
```json
{
  "id": "uuid-alloc-1",
  "vendor_id": "uuid-vendor-1",
  "vendor_name": "Hotel Coorg View",
  "trip_day_id": "uuid-trip-day-1",
  "quoted_amount": 6000.00,
  "confirmed_price": 5500.00,
  "is_locked": false
}
```
