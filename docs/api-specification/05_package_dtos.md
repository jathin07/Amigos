# 05 Package DTOs
## Package Catalog, Pricing, Destinations, Inclusions, and Exclusions DTOs

This document defines the API contracts, validation rules, lifecycle
behavior, nested collection behavior, field requirements, and JSON
representations for the Package domain.

Package is an independent business domain under:

    app/modules/package/

Package is NOT Master reference data.

---

# 1. Package DTOs

## 1.1 API Implementation Guidelines

### Administrative Endpoints

- `GET /api/v1/packages`
- `GET /api/v1/packages/{id}`
- `POST /api/v1/packages`
- `PUT /api/v1/packages/{id}`
- `DELETE /api/v1/packages/{id}`

These endpoints represent administrative Package management.

Existing public package endpoints in `public_routes.py` remain unchanged
during the legacy migration.

### Permissions

- `package.read`
- `package.create`
- `package.update`
- `package.delete`

### Searchable Fields

Case-insensitive:

- `title`

### Filtering Rules

Supported filters:

- `is_active`
- `is_featured`
- `duration_days`

### Sorting Rules

Supported:

- `title`
- `duration_days`
- `starting_price`
- `created_at`
- `updated_at`

Default:

- `sort_by = title`
- `sort_order = asc`

### Pagination

Default:

- `page = 1`
- `page_size = 20`

---

# 2. Package Domain Rules

## 2.1 Aggregate Ownership

Package is the aggregate root.

The following child records belong to Package:

- PackageHighlight
- PackageInclusion
- PackageExclusion
- PackageDestination

Creation and modification of these child records must occur through
PackageService.

Routes must not directly manipulate child repositories.

---

## 2.2 Duplicate Validation

Package title must be normalized before duplicate checking:

- trim surrounding whitespace
- compare case-insensitively

Another active Package must not have the same normalized title.

Duplicate active title:

    HTTP 409 Conflict
    ERR_PACKAGE_DUPLICATE_TITLE

If the existing database/business rules permit duplicate package titles,
this rule must be preserved instead of introducing a new database
constraint during migration.

---

## 2.3 Soft Delete

`DELETE /api/v1/packages/{id}` performs a soft delete:

    is_active = false

Package records must not be physically deleted.

A Package cannot be deactivated when prohibited by active downstream
business dependencies defined by the existing Booking/Proposal workflow.

Historical references must remain valid.

Dependency validation must occur through the appropriate service
contract and must not access another module's repository directly.

---

## 2.4 Optimistic Locking

Package updates require optimistic locking.

`UpdatePackageRequest.version` is REQUIRED.

If:

    request.version != package.version

return:

    HTTP 409 Conflict
    ERR_CONCURRENT_MODIFICATION

After successful modification:

    version = version + 1

The Package and all nested collection modifications must be committed
within the same transaction.

---

## 2.5 DB Compatibility Notes

These notes document the difference between the existing DB schema and
the frozen DTO contract. Implementations must adapt at the repository
layer, NOT alter the schema during this migration.

### display_order on PackageInclusion / PackageExclusion

The existing `package_inclusions` and `package_exclusions` tables do NOT
have a `display_order` column.

Implementation approach during migration:

- Accept `display_order` in request DTOs for future readiness.
- Do NOT persist `display_order` to `PackageInclusion` or `PackageExclusion`
  during this migration (column does not exist).
- Serialize `display_order` as `null` in response DTOs for those two types.
- Document this gap in the DTO spec comments.

A future schema migration to add `display_order` to those tables is
recommended but is OUT OF SCOPE for this migration step.

---

# 3. CreatePackageRequest

| Field           | Type    | Required | Nullable | Validation           | Default |
|-----------------|---------|----------|----------|----------------------|---------|
| title           | string  | Yes      | No       | Max 200              | —       |
| description     | string  | No       | Yes      | Text                 | null    |
| duration_days   | integer | Yes      | No       | >= 1                 | —       |
| duration_nights | integer | Yes      | No       | >= 0                 | —       |
| starting_price  | decimal | No       | Yes      | >= 0                 | null    |
| starting_city   | string  | No       | Yes      | Max 100              | null    |
| thumbnail_url   | string  | No       | Yes      | Text                 | null    |
| terms           | string  | No       | Yes      | Text                 | null    |
| is_featured     | boolean | No       | No       | Boolean              | false   |
| is_active       | boolean | No       | No       | Boolean              | true    |
| highlights      | array   | No       | No       | Highlight objects    | []      |
| inclusions      | array   | No       | No       | Inclusion objects    | []      |
| exclusions      | array   | No       | No       | Exclusion objects    | []      |
| destinations    | array   | No       | No       | Destination objects  | []      |

---

# 4. Nested Create DTOs

## 4.1 PackageHighlightRequest

| Field          | Type    | Required | Validation  |
|----------------|---------|----------|-------------|
| highlight_text | string  | Yes      | Non-empty   |
| display_order  | integer | No       | >= 1        |

Example:

    {
        "highlight_text": "Munnar hills sightseeing",
        "display_order": 1
    }

---

## 4.2 PackageInclusionRequest

| Field          | Type    | Required | Validation  |
|----------------|---------|----------|-------------|
| inclusion_text | string  | Yes      | Non-empty   |
| display_order  | integer | No       | >= 1 (accepted, not persisted in this migration) |

Note: `display_order` is accepted for forward-compatibility but is NOT
persisted during this migration because the `package_inclusions` table
does not have this column yet.

---

## 4.3 PackageExclusionRequest

| Field          | Type    | Required | Validation  |
|----------------|---------|----------|-------------|
| exclusion_text | string  | Yes      | Non-empty   |
| display_order  | integer | No       | >= 1 (accepted, not persisted in this migration) |

Note: `display_order` is accepted for forward-compatibility but is NOT
persisted during this migration because the `package_exclusions` table
does not have this column yet.

---

## 4.4 PackageDestinationRequest

| Field             | Type    | Required | Validation                     |
|-------------------|---------|----------|--------------------------------|
| destination_id    | uuid    | Yes      | Valid active Destination       |
| day_order         | integer | Yes      | >= 1                           |
| sequence          | integer | Yes      | >= 1                           |
| overnight_stay    | boolean | No       | Default false                  |
| default_duration  | string  | No       | Max 50                         |

Example:

    {
        "destination_id": "UUID v4",
        "day_order": 1,
        "sequence": 1,
        "overnight_stay": true,
        "default_duration": "1 Day"
    }

Destination ordering must be deterministic.

Within a Package, `(day_order, sequence)` must uniquely identify
the ordering position of a destination entry.

---

# 5. CreatePackageRequest Example

    {
        "title": "Kerala Delight",
        "description": "5 Days tour of Kerala",
        "duration_days": 5,
        "duration_nights": 4,
        "starting_price": 15000.00,
        "starting_city": "Kochi",
        "thumbnail_url": "https://cloudinary.com/kerala.jpg",
        "terms": "Valid till Sept 2026",
        "is_featured": false,
        "is_active": true,

        "highlights": [
            { "highlight_text": "Munnar hills sightseeing", "display_order": 1 },
            { "highlight_text": "Alleppey houseboat cruise", "display_order": 2 }
        ],

        "inclusions": [
            { "inclusion_text": "4 Nights hotel accommodation", "display_order": 1 },
            { "inclusion_text": "Daily breakfast", "display_order": 2 }
        ],

        "exclusions": [
            { "exclusion_text": "Lunch & dinner", "display_order": 1 }
        ],

        "destinations": [
            {
                "destination_id": "UUID v4",
                "day_order": 1,
                "sequence": 1,
                "overnight_stay": true,
                "default_duration": "1 Day"
            }
        ]
    }

---

# 6. UpdatePackageRequest

All mutable scalar Package fields are optional.

`version` is REQUIRED.

Nested collections are optional.

If a nested collection is omitted, the existing collection remains
unchanged.

If a nested collection is explicitly provided, PackageService
synchronizes that collection as part of the Package update transaction.

Example:

    {
        "starting_price": 16500.00,

        "highlights": [
            { "highlight_text": "Munnar hills sightseeing", "display_order": 1 },
            { "highlight_text": "Tea plantation visit", "display_order": 2 }
        ],

        "version": 3
    }

System-managed fields cannot be supplied:

- `id`
- `created_by`
- `created_at`
- `updated_by`
- `updated_at`

---

# 7. Nested Collection Update Semantics

PackageService owns synchronization of:

- highlights
- inclusions
- exclusions
- destinations

Rules:

### Collection omitted

Existing collection remains unchanged.

### Collection supplied as empty array

Existing collection is cleared.

Example:

    "exclusions": []

means remove all existing exclusions.

### Collection supplied with values

The supplied collection becomes the desired Package configuration.

Synchronization must occur inside the same transaction as the Package
update.

No partially updated Package aggregate may be committed.

---

# 8. PackageSummaryResponse

    {
        "id": "UUID v4",
        "title": "Kerala Delight",
        "duration_days": 5,
        "duration_nights": 4,
        "starting_price": 15000.00,
        "is_featured": false,
        "is_active": true
    }

---

# 9. PackageDetailResponse

    {
        "id": "UUID v4",
        "title": "Kerala Delight",
        "description": "5 Days tour of Kerala",
        "duration_days": 5,
        "duration_nights": 4,
        "starting_price": 15000.00,
        "starting_city": "Kochi",
        "thumbnail_url": "https://cloudinary.com/kerala.jpg",
        "terms": "Valid till Sept 2026",
        "is_featured": false,
        "is_active": true,

        "highlights": [
            {
                "id": "UUID v4",
                "highlight_text": "Munnar hills sightseeing",
                "display_order": 1
            }
        ],

        "inclusions": [
            {
                "id": "UUID v4",
                "inclusion_text": "4 Nights hotel accommodation",
                "display_order": null
            }
        ],

        "exclusions": [
            {
                "id": "UUID v4",
                "exclusion_text": "Lunch & dinner",
                "display_order": null
            }
        ],

        "destinations": [
            {
                "id": "UUID v4",
                "destination_id": "UUID v4",
                "day_order": 1,
                "sequence": 1,
                "overnight_stay": true,
                "default_duration": "1 Day"
            }
        ],

        "version": 1,

        "audit_info": {
            "created_by": "UUID v4",
            "created_at": "2026-07-20T12:00:00Z",
            "updated_by": "UUID v4",
            "updated_at": "2026-07-20T12:30:00Z"
        }
    }

Note: `display_order` is `null` for inclusions and exclusions because
the `package_inclusions` and `package_exclusions` tables do not have
that column yet. Highlights DO have `display_order` because
`package_highlights` has the column.

---

# 10. PackageListResponse

    {
        "items": [
            {
                "id": "UUID v4",
                "title": "Kerala Delight",
                "duration_days": 5,
                "duration_nights": 4,
                "starting_price": 15000.00,
                "is_featured": false,
                "is_active": true
            }
        ],

        "pagination": {
            "page": 1,
            "page_size": 20,
            "total_records": 250,
            "total_pages": 13
        }
    }

---

# 11. Validation Rules

## Title

- Required
- Trim whitespace
- Cannot be blank
- Maximum 200 characters

## Duration

    duration_days >= 1
    duration_nights >= 0

## Starting Price

When provided:

    starting_price >= 0

Money must use Decimal-compatible handling in Python/database logic.
The DB column is `Numeric(12, 2)`. Serialize as a decimal number, NOT a float.

## starting_city

Must remain a plain string (max 100). Do not introduce `city_id` FK during
this migration even though City master records exist.

## Destination

Every `destination_id` must:

- be a valid UUID
- reference an existing Destination
- reference an active Destination when creating/updating a Package

Destination validation must use the established module/service
boundary rather than directly accessing another module's repository.

## Nested Text Values

Highlight, inclusion, and exclusion text:

- trim whitespace
- cannot be blank

---

# 12. Error Rules

| Condition                          | HTTP | Error Code                      |
|------------------------------------|------|---------------------------------|
| Package not found                  | 404  | ERR_PACKAGE_NOT_FOUND           |
| Duplicate active title             | 409  | ERR_PACKAGE_DUPLICATE_TITLE     |
| Invalid or inactive destination    | 400  | ERR_INVALID_DESTINATION         |
| Active dependency prevents delete  | 409  | ERR_PACKAGE_IN_USE              |
| Concurrent modification            | 409  | ERR_CONCURRENT_MODIFICATION     |

---

# 13. Cross-Module Rules

Package may be referenced by:

- CRM
- Proposal
- Booking
- Reports

PackageService must not directly access repositories belonging to
these domains.

Cross-module validation or business effects must use:

- public service contracts, or
- Domain Events

according to the established architecture.

Existing public Package APIs remain unchanged during the v3 migration.

---

# 14. Audit Information

Audit fields are system-managed.

    {
        "audit_info": {
            "created_by": "UUID v4",
            "created_at": "2026-07-20T12:00:00Z",
            "updated_by": "UUID v4",
            "updated_at": "2026-07-20T12:30:00Z"
        }
    }

Clients cannot directly supply audit fields.
