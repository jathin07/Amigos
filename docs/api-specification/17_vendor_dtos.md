# 17 Vendor DTOs
## Vendor Profiles, Commercial Details, and Account Information DTOs

This document defines the API contracts, validation rules, lifecycle
behavior, field requirements, and JSON types for the Vendor domain.

Vendor is an independent business domain under:

app/modules/vendor/

Vendor is NOT part of Master reference data.

---

# 1. Vendor DTOs

## 1.1 API Implementation Guidelines

### Endpoints

- `GET /api/v1/vendors`
- `GET /api/v1/vendors/{id}`
- `POST /api/v1/vendors`
- `PUT /api/v1/vendors/{id}`
- `DELETE /api/v1/vendors/{id}`

### Permissions

- `vendor.read`
- `vendor.create`
- `vendor.update`
- `vendor.delete`

### Searchable Fields

Case-insensitive search is supported for:

- `vendor_name`
- `contact_person`
- `phone`
- `email`
- `gst_number`

### Filtering Rules

Supported filters:

- `is_active`
- `vendor_type_id`
- `is_verified`

Example:

GET /api/v1/vendors?is_active=true&vendor_type_id={uuid}

### Sorting Rules

Supported sorting fields:

- `vendor_name`
- `internal_rating`
- `created_at`
- `updated_at`

Default:

- `sort_by = vendor_name`
- `sort_order = asc`

### Pagination

Default:

- `page = 1`
- `page_size = 20`

### Duplicate Validation

Vendor name is NOT globally unique.

When `gst_number` is provided:

- Normalize to uppercase.
- Ignore surrounding whitespace.
- Another active Vendor must not have the same GST number.
- Duplicate GST number returns `409 Conflict`.

### Soft Delete

`DELETE /api/v1/vendors/{id}` performs a soft delete.

The record must NOT be physically deleted.

Instead:

`is_active = false`

Historical references from Booking, Operations, Finance, Reports,
or other modules must remain valid.

### Optimistic Locking

Vendor updates use optimistic locking.

`UpdateVendorRequest.version` is required.

If:

`request.version != vendor.version`

return:

- HTTP `409 Conflict`
- `ERR_CONCURRENT_MODIFICATION`

After successful modification:

`version = version + 1`

---

# 2. CreateVendorRequest

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| vendor_name | string | Yes | No | Max 200 | None | Grand Hyatt |
| vendor_type_id | uuid | Yes | No | Valid active FK | None | UUID |
| contact_person | string | No | Yes | Max 150 | null | Manager |
| phone | string | Yes | No | Max 20 | None | +919876543220 |
| email | string | No | Yes | Email, Max 150 | null | info@grandhyatt.com |
| address | string | No | Yes | Text | null | Kochi, Kerala |
| city | string | No | Yes | Max 100 | null | Kochi |
| state | string | No | Yes | Max 100 | null | Kerala |
| service_area | string | No | Yes | Max 255 | null | Accommodation |
| internal_rating | integer | No | Yes | 1–5 | null | 5 |
| bank_account_name | string | No | Yes | Max 150 | null | Hyatt Hotels Ltd |
| bank_account_number | string | No | Yes | Max 50 | null | 123456789 |
| ifsc | string | No | Yes | Max 20 | null | HDFC0001234 |
| gst_number | string | No | Yes | Max 20 | null | 32AAAAA1111A1Z1 |
| notes | string | No | Yes | Text | null | Preferred vendor |
| is_active | boolean | No | No | Boolean | true | true |

### Example

```json
{
    "vendor_name": "Grand Hyatt",
    "vendor_type_id": "UUID v4",
    "contact_person": "Hyatt Manager",
    "phone": "+919876543220",
    "email": "info@grandhyatt.com",
    "address": "Kochi, Kerala",
    "city": "Kochi",
    "state": "Kerala",
    "service_area": "Accommodation",
    "internal_rating": 5,
    "gst_number": "32AAAAA1111A1Z1",
    "notes": "Preferred vendor",
    "is_active": true
}
```

---

# 3. UpdateVendorRequest

All mutable Vendor fields are optional.

`version` is REQUIRED.

### Example

```json
{
    "phone": "+919876543221",
    "internal_rating": 4,
    "notes": "Updated vendor details",
    "version": 1
}
```

The following fields are system-managed and cannot be supplied by clients:

* `id`
* `created_by`
* `created_at`
* `updated_by`
* `updated_at`
* `verified_at`

---

# 4. Vendor Verification Rules

Vendor verification is a lifecycle/business operation.

The following fields are system-managed:

* `is_verified`
* `verified_at`

They must NOT be directly writable through
`CreateVendorRequest` or normal `UpdateVendorRequest`.

When a Vendor is verified:

```text
is_verified = true
verified_at = current UTC timestamp
```

When verification is revoked:

```text
is_verified = false
verified_at = null
```

Dedicated verification endpoints may be introduced later if required.

Until such endpoints exist, these fields remain response-only.

---

# 5. VendorSummaryResponse

```json
{
    "id": "UUID v4",
    "vendor_name": "Grand Hyatt",
    "vendor_type_id": "UUID v4",
    "phone": "+919876543220",
    "email": "info@grandhyatt.com",
    "is_verified": false,
    "is_active": true
}
```

---

# 6. VendorDetailResponse

```json
{
    "id": "UUID v4",
    "vendor_name": "Grand Hyatt",
    "vendor_type_id": "UUID v4",
    "contact_person": "Hyatt Manager",
    "phone": "+919876543220",
    "email": "info@grandhyatt.com",
    "address": "Kochi, Kerala",
    "city": "Kochi",
    "state": "Kerala",
    "service_area": "Accommodation",
    "internal_rating": 5,
    "bank_account_name": "Hyatt Hotels Ltd",
    "bank_account_number": "123456789",
    "ifsc": "HDFC0001234",
    "gst_number": "32AAAAA1111A1Z1",
    "is_verified": false,
    "verified_at": null,
    "notes": "Preferred vendor",
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:00:00Z"
    }
}
```

---

# 7. VendorListResponse

```json
{
    "items": [
        {
            "id": "UUID v4",
            "vendor_name": "Grand Hyatt",
            "vendor_type_id": "UUID v4",
            "phone": "+919876543220",
            "email": "info@grandhyatt.com",
            "is_verified": false,
            "is_active": true
        }
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 100,
        "total_pages": 5
    }
}
```

---

# 8. Field Validation Rules

## vendor_name

* Required
* Trim whitespace
* Cannot be blank
* Maximum 200 characters

## vendor_type_id

* Required
* Valid UUID
* Must reference an existing active Vendor Type

## phone

* Required
* Maximum 20 characters
* Trim whitespace

## email

When provided:

* Must be valid email syntax
* Maximum 150 characters
* Normalize to lowercase

## internal_rating

When provided:

`1 <= internal_rating <= 5`

## gst_number

When provided:

* Maximum 20 characters
* Trim whitespace
* Normalize to uppercase
* Must not duplicate another active Vendor's GST number

## bank details

Bank details are optional.

Sensitive financial fields must never be written to application logs.

---

# 9. Error Rules

## Vendor Not Found

HTTP 404

Code:

`ERR_VENDOR_NOT_FOUND`

## Invalid Vendor Type

HTTP 400 or domain-standard validation response.

Code:

`ERR_INVALID_VENDOR_TYPE`

## Duplicate GST

HTTP 409

Code:

`ERR_VENDOR_DUPLICATE_GST`

## Concurrent Modification

HTTP 409

Code:

`ERR_CONCURRENT_MODIFICATION`

---

# 10. Cross-Module Rules

Vendor may be referenced by:

* Booking
* Operations
* Vendor Allocation
* Finance
* Vendor Payments
* Expenses
* Reports

Vendor deletion must never destroy historical references.

The Vendor module must not directly modify another module's models
or repositories.

Cross-module business operations must use:

* public service contracts, or
* Domain Events

according to the established backend architecture.

---

# 11. Audit Information

Audit information is system-managed.

```json
{
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:00:00Z"
    }
}
```

Clients cannot directly supply audit fields.
