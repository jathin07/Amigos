# 08 Finance DTOs
## Cash Flow tracking: Expense logs, vendor payments, and derived margins

---

## 1. Request DTOs

### 1.1 `CreateExpenseRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `booking_id` | string | Yes | No | Format: UUID | None | `uuid-booking-1` |
| `category_id` | string | Yes | No | Format: UUID | None | `uuid-category-1` |
| `amount` | decimal | Yes | No | `> 0` | None | `1500.00` |
| `remarks` | string | No | Yes | Max length: 255 | None | `Fuel refill` |

```json
{
  "booking_id": "uuid-booking-1",
  "category_id": "uuid-category-1",
  "amount": 1500.00,
  "remarks": "Fuel refill"
}
```

### 1.2 `PaymentRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `booking_id` | string | Yes | No | Format: UUID | None | `uuid-booking-1` |
| `amount` | decimal | Yes | No | `> 0` | None | `5000.00` |
| `payment_mode` | string | Yes | No | Enum: PaymentMode | None | `UPI` |
| `transaction_reference` | string | Yes | No | Max length: 100 | None | `TXN12345` |

```json
{
  "booking_id": "uuid-booking-1",
  "amount": 5000.00,
  "payment_mode": "UPI",
  "transaction_reference": "TXN12345"
}
```

---

## 2. Response DTOs

### 2.1 `ProfitSummaryResponse`
```json
{
  "booking_id": "uuid-booking-1",
  "revenue": 12500.00,
  "operational_expenses": 1500.00,
  "vendor_allocations_cost": 5500.00,
  "refund_amount": 0.00,
  "net_profit": 5500.00,
  "profit_margin_percentage": 44.00,
  "outstanding_balance": 0.00
}
```

### 2.2 `OutstandingPaymentResponse`
```json
{
  "booking_id": "uuid-booking-1",
  "total_revenue": 12500.00,
  "total_paid": 5000.00,
  "outstanding_balance": 7500.00
}
```
