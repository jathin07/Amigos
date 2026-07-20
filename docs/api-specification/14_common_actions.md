# 14 Common Action DTOs
## Non-CRUD State Action Transition Payload Schemas

These DTOs map inputs for business state alteration triggers.

---

## 1. Request DTOs

### 1.1 `ConfirmBookingRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `operations_owner_id` | string | Yes | No | Format: UUID | None | `uuid-tm-2` |
| `remarks` | string | No | Yes | None | None | `Verified payment deposit` |

```json
{
  "operations_owner_id": "uuid-tm-2",
  "remarks": "Verified payment deposit"
}
```

### 1.2 `CancelBookingRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `cancellation_reason` | string | Yes | No | Max length: 255 | None | `Customer health issue` |
| `refund_amount` | decimal | Yes | No | `>= 0` | None | `2500.00` |

```json
{
  "cancellation_reason": "Customer health issue",
  "refund_amount": 2500.00
}
```

### 1.3 `MarkTripReadyRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `coordinator_id` | string | Yes | No | Format: UUID | None | `uuid-tm-3` |
| `checklist_remarks` | string | No | Yes | None | None | `Checked transport details` |

```json
{
  "coordinator_id": "uuid-tm-3",
  "checklist_remarks": "Checked transport details"
}
```
