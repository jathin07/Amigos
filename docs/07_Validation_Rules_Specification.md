# 07 Validation & Business Rules Specification
## Unified Business Rules and Validation Invariant Specifications

This document defines the strict validation gates, business invariant rules, and transaction boundaries across all modules of the Amigos Tourism application.

---

## 1. CRM Lead Validation Rules

### 1.1 Active Lead Deduplication
- **Rule**: A new Lead cannot be created if an active Lead (status other than `Won` or `Lost`) already exists with the same phone number.
- **Validation Error Code**: `ERR_DUPLICATE_RESOURCE` (400 Bad Request)

### 1.2 Lead Assignment Invariants
- **Rule**: When a lead is assigned or taken by a Sales Executive, the change must write to `AssignmentHistory` in the same database transaction.
- **Rule**: Self-assignment (`POST /leads/{id}/take`) is only allowed if the lead's current status is `New` and `lead_handler_id` is null.

---

## 2. Proposal Validation Rules

### 2.1 Single Final Proposal
- **Rule**: A Lead can have multiple draft proposals, but only one proposal version may be marked as final (`is_final = True`) at any given time.
- **Validation Error Code**: `ERR_DUPLICATE_RESOURCE` (400 Bad Request)

### 2.2 Proposal Modification Boundaries
- **Rule**: A proposal cannot be modified, duplicated, or deleted once it is referenced by a confirmed Booking.
- **Validation Error Code**: `ERR_IMMUTABLE_PROPOSAL` (400 Bad Request)

### 2.3 Itinerary Day Progression
- **Rule**: Destination mappings inside a proposal must have `day_number` starting at 1 and incrementing sequentially (1, 2, 3...) without gaps or duplicates.

---

## 3. Booking Validation Rules

### 3.1 Advance Payment Lock
- **Rule**: A Booking cannot be created or confirmed until the first payment transaction has been logged and verified by the Finance module.
- **Validation Error Code**: `ERR_VALIDATION_FAILED` (400 Bad Request)

### 3.2 Installment Schedule Percentages
- **Rule**: The sum of all percentage values in the booking installment schedule must equal exactly `100.00%`.
- **Validation Error Code**: `ERR_VALIDATION_FAILED` (400 Bad Request)

---

## 4. Operations Validation Rules

### 4.1 Preparation Checklist Completion
- **Rule**: A booking status cannot be set to `Ready` or `Ongoing` unless every checklist item associated with the operational trip has `is_completed = True`.
- **Validation Error Code**: `ERR_CHECKLIST_INCOMPLETE` (400 Bad Request)

### 4.2 Vendor Allocations Modifications
- **Rule**: Confirmed vendor allocations (`is_locked = True`) cannot be modified or deleted without Admin role credentials.
- **Validation Error Code**: `ERR_ALLOCATION_LOCKED` (400 Bad Request)

---

## 5. Finance Validation Rules

### 5.1 Completed Trip Lock
- **Rule**: No expenses can be added, edited, or deleted under a Booking once the trip status is marked `Completed` or `Closed`.
- **Validation Error Code**: `ERR_FINANCE_LOCKED` (400 Bad Request)

### 5.2 Vendor Payment Caps
- **Rule**: Total vendor payments logged under a trip plan day allocation cannot exceed the `confirmed_price` set in the `VendorAllocation` record.
