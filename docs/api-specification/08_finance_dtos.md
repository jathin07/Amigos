# 08 Finance DTOs
## Customer Payments, Vendor Payments, Expenses, Refunds, and P&L Schemas

> **Aggregate Roots**: `Payment`, `VendorPayment`, `Expense`, `Refund`
> **Design Note**: Each financial record is an independent aggregate because money movements are immutable events. They must never be bundled into a single massive transaction.
> **Finance Lock Rule**: Expense and VendorPayment records are locked from modifications once the parent `Booking` status is `Completed` or `Closed`.

---

## Aggregate Rules

- `Payment` records are owned exclusively by Finance module.
- `VendorPayment` records are tied to `VendorAllocation` in Operations but owned by Finance.
- `Expense` records belong to a `Booking`; they cannot be created/modified/deleted when `Booking.status` is `Completed` or `Closed`.
- `Refund` is an independent aggregate. Refunds do not automatically update `Payment` records — they are standalone entries.
- Finance never creates `Booking` or `VendorAllocation` records directly. It reads them via service endpoints.
- P&L summaries are **derived** computed views — they are never stored or mutated.

---

## Payment State Machine

```
PENDING → RECEIVED → VERIFIED
        ↘ FAILED
```

| Status Code | Meaning |
| :--- | :--- |
| `PENDING` | Payment recorded; awaiting verification |
| `RECEIVED` | Payment confirmed received (triggers `AdvanceReceived` event) |
| `VERIFIED` | Payment independently verified against bank records |
| `FAILED` | Transaction failed or reversed |

---

## Refund State Machine

```
REQUESTED → APPROVED → PROCESSED → COMPLETED
          ↘ REJECTED
```

| Status Code | Meaning |
| :--- | :--- |
| `REQUESTED` | Refund application submitted |
| `APPROVED` | Approved by admin |
| `PROCESSED` | Payment disbursed |
| `COMPLETED` | Customer acknowledges receipt |
| `REJECTED` | Refund denied with reason |

---

## Finance Lock Rules

| Action | Allowed when Booking is `Completed` / `Closed` | Notes |
| :--- | :--- | :--- |
| Create `Expense` | ❌ Blocked | `EXPENSE_LOCKED` error returned |
| Update `Expense` | ❌ Blocked | `EXPENSE_LOCKED` error returned |
| Delete `Expense` | ❌ Blocked | `EXPENSE_LOCKED` error returned |
| Create `VendorPayment` | ❌ Blocked | `FINANCE_LOCKED` error returned |
| Create `Payment` (customer) | ✅ Allowed | Outstanding balances may still be collected |
| Create `Refund` | ✅ Allowed | Refunds are post-trip business operations |

---

## 1. Request DTOs

---

### 1.1 `RecordCustomerPaymentRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `booking_id` | string | Yes | No | Format: UUID | — | `uuid-booking-1` |
| `payment_schedule_id` | string | No | Yes | Format: UUID | — | `uuid-sched-1` |
| `payment_date` | string | Yes | No | Format: ISO Date; not future | — | `2026-07-20` |
| `amount` | decimal | Yes | No | `> 0`, Max: 9,999,999.99 | — | `25000.00` |
| `payment_method_id` | string | Yes | No | Format: UUID (PaymentMethod) | — | `uuid-pm-upi` |
| `payment_type_id` | string | Yes | No | Format: UUID (PaymentType) | — | `uuid-pt-advance` |
| `installment_no` | integer | No | Yes | `>= 1` | — | `1` |
| `transaction_reference` | string | No | Yes | Max: 100 chars | — | `TXN202607201234` |
| `remarks` | string | No | Yes | Max: 500 chars | — | `Advance payment via UPI` |

```json
{
  "booking_id": "uuid-booking-1",
  "payment_schedule_id": "uuid-sched-1",
  "payment_date": "2026-07-20",
  "amount": 25000.00,
  "payment_method_id": "uuid-pm-upi",
  "payment_type_id": "uuid-pt-advance",
  "installment_no": 1,
  "transaction_reference": "TXN202607201234",
  "remarks": "Advance payment via UPI. Reference confirmed by customer WhatsApp."
}
```

**Validation Rules:**
- `booking_id` must reference an existing, non-deleted booking.
- `payment_date` must not be in the future.
- `amount` must not exceed the outstanding balance for the booking.
- If `payment_schedule_id` provided, the installment must be in `PENDING` status.
- First payment (advance) triggers `AdvanceReceived` domain event → Booking module creates/confirms Booking.

---

### 1.2 `VerifyPaymentRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `verified_by_team_member_id` | string | Yes | No | Format: UUID | — | `uuid-tm-admin` |
| `verification_notes` | string | No | Yes | Max: 500 chars | — | `Verified against bank statement` |

```json
{
  "verified_by_team_member_id": "uuid-tm-admin",
  "verification_notes": "Verified against HDFC bank statement dated 2026-07-21."
}
```

---

### 1.3 `UploadPaymentReceiptRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `receipt_url` | string | Yes | No | Valid URL, Max: 2000 chars | — | `https://s3.../receipt-1.pdf` |
| `storage_provider` | string | No | Yes | Enum: `S3`, `LOCAL` | `S3` | `S3` |

```json
{
  "receipt_url": "https://s3.ap-south-1.amazonaws.com/amigos-docs/receipts/receipt-1.pdf",
  "storage_provider": "S3"
}
```

---

### 1.4 `RecordVendorPaymentRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `vendor_allocation_id` | string | Yes | No | Format: UUID | — | `uuid-alloc-1` |
| `payment_date` | string | Yes | No | Format: ISO Date; not future | — | `2026-08-12` |
| `amount` | decimal | Yes | No | `> 0`; must not exceed remaining balance | — | `4750.00` |
| `payment_method_id` | string | Yes | No | Format: UUID (PaymentMethod) | — | `uuid-pm-bank-transfer` |
| `transaction_reference` | string | No | Yes | Max: 100 chars | — | `NEFT20260812` |
| `internal_notes` | string | No | Yes | Max: 500 chars | — | `Partial payment. Balance on trip return` |

```json
{
  "vendor_allocation_id": "uuid-alloc-1",
  "payment_date": "2026-08-12",
  "amount": 4750.00,
  "payment_method_id": "uuid-pm-bank-transfer",
  "transaction_reference": "NEFT20260812",
  "internal_notes": "50% advance to vendor. Balance ₹4750 to be paid on trip return."
}
```

**Validation Rules:**
- `vendor_allocation_id` must reference a `CONFIRMED` or `LOCKED` allocation.
- `amount` must not exceed `confirmed_price - total_already_paid`.
- Booking must not be in `Completed` or `Closed` status (Finance Lock).
- Parent `Booking` must not be `Cancelled`.

---

### 1.5 `CreateExpenseRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `booking_id` | string | Yes | No | Format: UUID | — | `uuid-booking-1` |
| `vendor_allocation_id` | string | No | Yes | Format: UUID | — | `null` |
| `expense_category_id` | string | Yes | No | Format: UUID (ExpenseCategory) | — | `uuid-cat-fuel` |
| `expense_type_id` | string | Yes | No | Format: UUID (ExpenseType) | — | `uuid-type-operational` |
| `amount` | decimal | Yes | No | `> 0`, Max: 9,999,999.99 | — | `1500.00` |
| `expense_date` | string | Yes | No | Format: ISO Date; not future | — | `2026-08-11` |
| `expense_description` | string | No | Yes | Max: 255 chars | — | `Diesel refill at Madikeri` |
| `remarks` | string | No | Yes | Max: 500 chars | — | `Highway fuel top-up` |

```json
{
  "booking_id": "uuid-booking-1",
  "vendor_allocation_id": null,
  "expense_category_id": "uuid-cat-fuel",
  "expense_type_id": "uuid-type-operational",
  "amount": 1500.00,
  "expense_date": "2026-08-11",
  "expense_description": "Diesel refill at Madikeri fuel station",
  "remarks": "Fuel for return trip. Receipt attached."
}
```

**Validation Rules:**
- `booking_id` must reference a non-deleted booking.
- Booking must not be in `Completed` or `Closed` status (Finance Lock).
- `expense_date` must fall within or after the booking's `trip_start_date`.
- `expense_date` must not be in the future.

---

### 1.6 `CreateRefundRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `booking_id` | string | Yes | No | Format: UUID | — | `uuid-booking-1` |
| `amount` | decimal | Yes | No | `> 0`; must not exceed total paid | — | `5000.00` |
| `refund_date` | string | No | Yes | Format: ISO Date | — | `2026-08-15` |
| `payment_method_id` | string | Yes | No | Format: UUID (PaymentMethod) | — | `uuid-pm-bank-transfer` |
| `transaction_reference` | string | No | Yes | Max: 100 chars | — | `REFUND20260815` |
| `remarks` | string | No | Yes | Max: 500 chars | — | `Customer cancelled Day 3` |

```json
{
  "booking_id": "uuid-booking-1",
  "amount": 5000.00,
  "refund_date": "2026-08-15",
  "payment_method_id": "uuid-pm-bank-transfer",
  "transaction_reference": "REFUND20260815",
  "remarks": "Customer cancelled Day 3 activities. Partial refund as per cancellation policy."
}
```

**Validation Rules:**
- `amount` must not exceed total amount paid by the customer for this booking.
- Refund amount must account for existing approved refunds (cumulative total must not exceed total paid).

---

### 1.7 `CloseBookingFinanceRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `closing_notes` | string | No | Yes | Max: 1000 chars | — | `All payments settled` |

```json
{
  "closing_notes": "All vendor payments settled. Customer outstanding balance collected. Finance closed."
}
```

**Guard Conditions:**
- `Booking.status` must be `Completed`.
- No pending `PaymentSchedule` items with status `PENDING`.
- No `VendorAllocation` with `settlement_status = PENDING`.

---

## 2. Response DTOs

---

### 2.1 `PaymentDetailResponse`

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | Payment UUID |
| `booking_id` | string | No | Parent Booking UUID |
| `booking_number` | string | No | e.g., `AMT-2026-00001` |
| `payment_schedule_id` | string | Yes | Linked schedule installment |
| `payment_date` | string | No | ISO Date |
| `amount` | decimal | No | Payment amount |
| `payment_method` | object | No | `{ id, code, name }` |
| `payment_type` | object | No | `{ id, code, name }` |
| `payment_status` | object | No | `{ id, code, name }` |
| `installment_no` | integer | Yes | Which installment number |
| `transaction_reference` | string | Yes | Bank / UPI reference |
| `receipt_url` | string | Yes | S3 receipt URL |
| `received_by` | object | Yes | `{ id, display_name }` |
| `verified_by` | object | Yes | `{ id, display_name }` |
| `remarks` | string | Yes | Notes |
| `created_at` | string | No | ISO DateTime |

```json
{
  "id": "uuid-payment-1",
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "payment_schedule_id": "uuid-sched-1",
  "payment_date": "2026-07-20",
  "amount": 25000.00,
  "payment_method": { "id": "uuid-pm-1", "code": "UPI", "name": "UPI" },
  "payment_type": { "id": "uuid-pt-1", "code": "ADVANCE", "name": "Advance" },
  "payment_status": { "id": "uuid-ps-1", "code": "RECEIVED", "name": "Received" },
  "installment_no": 1,
  "transaction_reference": "TXN202607201234",
  "receipt_url": "https://s3.ap-south-1.amazonaws.com/amigos-docs/receipts/receipt-1.pdf",
  "received_by": { "id": "uuid-tm-1", "display_name": "Ravi Kumar" },
  "verified_by": null,
  "remarks": "Advance payment via UPI.",
  "created_at": "2026-07-20T11:00:00Z"
}
```

---

### 2.2 `VendorPaymentDetailResponse`

```json
{
  "id": "uuid-vp-1",
  "vendor_allocation_id": "uuid-alloc-1",
  "vendor_name": "Hotel Coorg View",
  "service_name": "Room Accommodation - 5 Rooms",
  "payment_date": "2026-08-12",
  "amount": 4750.00,
  "payment_method": { "id": "uuid-pm-2", "code": "BANK_TRANSFER", "name": "Bank Transfer" },
  "payment_status": { "id": "uuid-ps-1", "code": "RECEIVED", "name": "Received" },
  "transaction_reference": "NEFT20260812",
  "receipt_url": null,
  "internal_notes": "50% advance to vendor.",
  "created_at": "2026-08-12T09:00:00Z"
}
```

---

### 2.3 `ExpenseDetailResponse`

```json
{
  "id": "uuid-exp-1",
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "vendor_allocation_id": null,
  "expense_category": { "id": "uuid-cat-fuel", "code": "FUEL", "name": "Fuel" },
  "expense_type": { "id": "uuid-type-ops", "code": "OPERATIONAL", "name": "Operational" },
  "amount": 1500.00,
  "expense_date": "2026-08-11",
  "expense_description": "Diesel refill at Madikeri fuel station",
  "remarks": "Fuel for return trip. Receipt attached.",
  "approved_by": null,
  "created_at": "2026-08-11T16:30:00Z"
}
```

---

### 2.4 `RefundDetailResponse`

```json
{
  "id": "uuid-refund-1",
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "refund_status": { "id": "uuid-rs-1", "code": "COMPLETED", "name": "Completed" },
  "amount": 5000.00,
  "refund_date": "2026-08-15",
  "payment_method": { "id": "uuid-pm-2", "code": "BANK_TRANSFER", "name": "Bank Transfer" },
  "transaction_reference": "REFUND20260815",
  "remarks": "Customer cancelled Day 3 activities. Partial refund as per cancellation policy.",
  "created_at": "2026-08-15T10:00:00Z"
}
```

---

### 2.5 `BookingFinanceSummaryResponse`

The core P&L view. All values are **derived** — computed at query time from actual ledger records. Never stored.

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `booking_id` | string | No | Booking UUID |
| `booking_number` | string | No | Human-readable booking reference |
| `total_amount` | decimal | No | Agreed booking value (contract) |
| `total_paid` | decimal | No | Sum of `RECEIVED` customer payments |
| `outstanding_balance` | decimal | No | `total_amount - total_paid` |
| `vendor_cost` | decimal | No | Sum of confirmed VendorAllocation costs |
| `vendor_amount_paid` | decimal | No | Sum of settled VendorPayments |
| `vendor_balance_due` | decimal | No | `vendor_cost - vendor_amount_paid` |
| `operational_expenses` | decimal | No | Sum of non-vendor Expense records |
| `refunds_issued` | decimal | No | Sum of `COMPLETED` Refunds |
| `net_revenue` | decimal | No | `total_paid - refunds_issued` |
| `total_cost` | decimal | No | `vendor_cost + operational_expenses` |
| `gross_profit` | decimal | No | `net_revenue - total_cost` |
| `profit_margin_percentage` | decimal | No | `(gross_profit / net_revenue) * 100` |
| `finance_status` | string | No | `OPEN`, `CLOSED` |

```json
{
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "total_amount": 85000.00,
  "total_paid": 60000.00,
  "outstanding_balance": 25000.00,
  "vendor_cost": 38000.00,
  "vendor_amount_paid": 19000.00,
  "vendor_balance_due": 19000.00,
  "operational_expenses": 4500.00,
  "refunds_issued": 0.00,
  "net_revenue": 60000.00,
  "total_cost": 42500.00,
  "gross_profit": 17500.00,
  "profit_margin_percentage": 29.17,
  "finance_status": "OPEN"
}
```

---

### 2.6 `InstallmentScheduleResponse`

```json
{
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "total_amount": 85000.00,
  "total_paid": 60000.00,
  "outstanding_balance": 25000.00,
  "schedules": [
    {
      "id": "uuid-sched-1",
      "installment_no": 1,
      "due_date": "2026-07-20",
      "amount": 25000.00,
      "percentage": 29.41,
      "payment_status": { "code": "RECEIVED", "name": "Received" },
      "remarks": "Advance payment"
    },
    {
      "id": "uuid-sched-2",
      "installment_no": 2,
      "due_date": "2026-08-05",
      "amount": 35000.00,
      "percentage": 41.18,
      "payment_status": { "code": "RECEIVED", "name": "Received" },
      "remarks": "Second installment"
    },
    {
      "id": "uuid-sched-3",
      "installment_no": 3,
      "due_date": "2026-08-10",
      "amount": 25000.00,
      "percentage": 29.41,
      "payment_status": { "code": "PENDING", "name": "Pending" },
      "remarks": "Final payment on trip start"
    }
  ]
}
```

---

### 2.7 `OutstandingPaymentResponse` (List item)

Used for the outstanding payments dashboard view.

```json
{
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "customer_name": "Raj Enterprises (Raju Naik)",
  "trip_start_date": "2026-08-10",
  "total_amount": 85000.00,
  "total_paid": 60000.00,
  "outstanding_balance": 25000.00,
  "next_installment_due_date": "2026-08-10",
  "next_installment_amount": 25000.00,
  "booking_status": { "code": "CONFIRMED", "name": "Confirmed" }
}
```

---

### 2.8 `PendingVendorPaymentResponse` (List item)

Used for the pending vendor disbursements view.

```json
{
  "vendor_allocation_id": "uuid-alloc-1",
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "vendor_name": "Hotel Coorg View",
  "service_name": "Room Accommodation - 5 Rooms",
  "service_date": "2026-08-10",
  "quoted_amount": 10000.00,
  "confirmed_price": 9500.00,
  "total_paid": 4750.00,
  "balance_due": 4750.00,
  "settlement_status": "PARTIAL"
}
```

---

### 2.9 `UpcomingInstallmentResponse` (List item)

Used for the upcoming installments dashboard.

```json
{
  "payment_schedule_id": "uuid-sched-3",
  "booking_id": "uuid-booking-1",
  "booking_number": "AMT-2026-00001",
  "customer_name": "Raj Enterprises (Raju Naik)",
  "installment_no": 3,
  "due_date": "2026-08-10",
  "amount": 25000.00,
  "days_until_due": 7,
  "payment_status": { "code": "PENDING", "name": "Pending" }
}
```

---

## 3. Error Catalogue

| Error Code | HTTP Status | Trigger | Message |
| :--- | :--- | :--- | :--- |
| `EXPENSE_LOCKED` | 409 | Creating/updating expense when Booking is `Completed`/`Closed` | Expenses cannot be modified once the booking is completed |
| `FINANCE_LOCKED` | 409 | Creating VendorPayment when Booking is `Completed`/`Closed` | Vendor payments cannot be recorded once the booking is closed |
| `PAYMENT_EXCEEDS_OUTSTANDING` | 422 | Payment amount exceeds outstanding balance | Payment amount exceeds the booking outstanding balance |
| `VENDOR_PAYMENT_EXCEEDS_BALANCE` | 422 | VendorPayment exceeds remaining allocation balance | Payment exceeds the remaining vendor allocation balance |
| `REFUND_EXCEEDS_PAID` | 422 | Cumulative refunds exceed total amount paid | Total refund amount cannot exceed total amount collected |
| `BOOKING_ALREADY_CLOSED` | 409 | Trying to close already-closed finance | Booking finance is already closed |
| `PENDING_INSTALLMENTS_EXIST` | 409 | Closing finance with pending schedules | All payment installments must be settled before closing finance |
| `VENDOR_PENDING_SETTLEMENTS` | 409 | Closing finance with unsettled vendor allocations | All vendor allocations must be settled before closing finance |
| `PAYMENT_NOT_FOUND` | 404 | Payment UUID does not exist | Payment record not found |
| `EXPENSE_NOT_FOUND` | 404 | Expense UUID does not exist | Expense record not found |
| `CONCURRENT_UPDATE` | 409 | Booking row_version mismatch during status update | Concurrent modification detected. Please refresh and retry |

---

## 4. Security Matrix

| Operation | Min Role | Notes |
| :--- | :--- | :--- |
| `POST /finance/payments` | Finance Executive | Record customer payment |
| `POST /finance/payments/{id}/verify` | Admin | Payment verification is admin-only |
| `POST /finance/payments/{id}/receipt` | Finance Executive | Upload receipt |
| `POST /finance/vendor-payments` | Finance Executive | Record vendor disbursement |
| `POST /finance/expenses` | Trip Coordinator | On-trip expenses recorded by coordinator |
| `DELETE /finance/expenses/{id}` | Finance Executive | Blocked if booking is Completed |
| `GET /finance/bookings/{id}/profit-summary` | Finance Executive, Admin | P&L view |
| `POST /finance/bookings/{id}/close` | Admin | Finance closure is admin-only |
| `POST /finance/refunds` | Admin | Refunds require admin approval |

---

## 5. Domain Events Published

| Event | Trigger | Payload |
| :--- | :--- | :--- |
| `AdvanceReceived` | First customer payment recorded with `RECEIVED` status | `{ booking_id, payment_id, amount, payment_date, occurred_at }` |
| `FinanceClosed` | `POST /finance/bookings/{id}/close` succeeds | `{ booking_id, closed_at, closed_by_team_member_id }` |

---

## 6. Domain Events Subscribed

| Event | Source | Action |
| :--- | :--- | :--- |
| `TripCompleted` | Operations Module | Lock all `Expense` and `VendorPayment` creation (set Finance lock) |
| `BookingConfirmed` | Booking Module | Activate payment schedule tracking |
