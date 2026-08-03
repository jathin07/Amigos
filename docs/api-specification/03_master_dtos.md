# 03 Master DTOs
## Reusable Configurations, Catalogs, and Reference Data

The Master module stores reusable reference data shared across multiple business modules.

These entities are maintained by administrators and referenced by CRM, Package, Proposal, Booking, Operations, Finance, and Reports.

---

# Architectural Guidelines & Standardization Rules

To ensure an enterprise-ready architecture, all Master entities strictly follow these standardized rules. 

### 1. Standardize Every Master Entity
Every master entity must expose exactly these DTOs:
- `Create<Entity>Request`
- `Update<Entity>Request`
- `<Entity>SummaryResponse`
- `<Entity>DetailResponse`
- `<Entity>ListResponse`

No entity should miss one of these DTOs.

### 2. Common Request Fields
Where applicable, every `CreateRequest` should support:
- `code`
- `name`
- `description`
- `display_order`
- `is_active`

### 3. Common Response Fields
Every `SummaryResponse` should contain exactly:
- `id`
- `code`
- `name`
- `is_active`

*Rule: Summary DTOs contain only commonly displayed fields. Do not include additional business fields.*

Every `DetailResponse` should additionally contain:
- `description`
- `display_order`
- `version`
- `audit_info`
- Any entity-specific fields

### 4. Common Pagination
Every `ListResponse` must use the exact same format for pagination:
```json
{
    "items": [],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

### 5. Soft Delete Support
Master records are **never physically deleted**. Deletion should only set `is_active = false`. Business modules must ignore inactive master records. Repositories must not physically delete records.

### 6. Uniqueness Rules
The following business constraints apply globally across the platform. Return HTTP 409 for duplicate business keys.
- **Destination**: Duplicate `code`, Duplicate `slug`
- **Package Category**: Duplicate `code`
- **Vehicle Type**: Duplicate `code`
- **Meal Plan**: Duplicate `code`
- **Country**: Duplicate ISO `code`
- **Currency**: Duplicate currency `code`
- **Tax Configuration**: Duplicate Tax `code`
- **State**: Duplicate `code` within the same country

### 7. Lookup Support
Every master entity automatically supports lightweight lookup APIs:
- `GET /lookup/destinations`
- `GET /lookup/vehicle-types`
- `GET /lookup/meal-plans`
- `GET /lookup/countries`

All lookup APIs return a standardized `MasterLookupResponse` DTO:
```json
{
    "items": [
        {
            "id": "UUID v4",
            "name": "Entity Name",
            "code": "ENTITY_CODE"
        }
    ]
}
```
Lookup responses only return `id`, `name`, and `code`. Nothing else. Only active records are returned. Full details belong to `DetailResponse`. Lookup endpoints should use lightweight queries.

### 8. Sorting Rules
Default sorting across all list and lookup APIs:
1. `display_order ASC`
2. `name ASC`

Allowed sort fields:
- `name`
- `code`
- `created_at`
- `updated_at`
- `display_order`

### 9. Filtering Rules
Supported generic filters across all list APIs:
- `page`, `page_size`
- `search` (case-insensitive)
- `is_active` (Only active records are returned by default)
- `sort_by`, `sort_order`

### 10. Audit Rules
Audit fields are **read-only**. Clients must never send audit fields (`created_by`, `created_at`, `updated_by`, `updated_at`). Only `DetailResponse` includes `audit_info`.
Currently, `created_by` and `updated_by` use simple UUIDs. Do not expand them into nested user objects.
Automatic audit updates:
- **Create**: `created_by`, `created_at`
- **Update**: `updated_by`, `updated_at`
- **Delete**: `updated_by`, `updated_at`, `is_active=false`

### 11. Validation Rules
Common validations apply across all modules:
- **code**: uppercase, unique, letters/numbers/underscore only. No spaces.
- **name**: required, max length 100
- **description**: optional, max length 255
- **display_order**: >=0
- **percentage**: 0–100
- **month**: 1–12
- **capacity**: >=1

### 12. API Behavior
- **Create**: returns `DetailResponse`
- **Update**: returns `DetailResponse`
- **Delete**: returns success response payload: `{"success": true, "message": "<Entity> deactivated successfully."}`
- **List**: returns `ListResponse`
- **Get**: returns `DetailResponse`

### 13. API Response Standards
Every endpoint returns the Standard API Response Envelope.

**Success**
```json
{
    "success": true,
    "message": "Destination created successfully.",
    "data": { ... }
}
```

**Failure**
```json
{
    "success": false,
    "message": "Validation failed.",
    "errors": [
        {
            "code": "ERR_DUPLICATE_CODE",
            "field": "code",
            "message": "Destination code already exists."
        }
    ]
}
```

### 14. HTTP Status Codes
Standard responses used across Master APIs:
- **GET**: 200
- **POST**: 201 (Returns HTTP 201 Created with a `Location` header pointing to `/api/v1/masters/<entity>/{id}`)
- **PUT**: 200
- **DELETE**: 200
- **Validation Error**: 400
- **Unauthorized**: 401
- **Forbidden**: 403
- **Not Found**: 404
- **Duplicate Business Key**: 409
- **Unexpected Error**: 500

### 15. Versioning Policy
Master APIs are versioned.
Example: `/api/v1/masters/destinations`
Future breaking changes require `/api/v2`. DTOs must remain backward compatible within the same API version.

### 16. Idempotency Rules
- **GET** is idempotent
- **PUT** is idempotent (Note: In this system, PUT is used with partial update semantics where all request fields are optional)
- **DELETE** (soft delete) is idempotent
- **POST** is **not** idempotent

### 17. Transaction Rules
Every Create, Update, and Delete operation executes inside a database transaction. Rollback on validation or persistence failure.

### 18. Repository Rules
Repositories are responsible only for:
- CRUD
- Filtering
- Pagination
- Sorting

Repositories **must not** contain business logic.

### 19. Service Rules
Services are responsible for:
- Business validation
- Duplicate validation
- Dependency validation
- Audit updates
- Event publishing (future)
- Permission checks (where applicable)

### 20. Controller Rules
Controllers only:
- Validate request DTO
- Authorize request
- Call service
- Return API response

No business logic inside controllers.

### 21. Error Codes
Common business errors to be reused across all Master entities:
- `ERR_DUPLICATE_CODE`
- `ERR_DUPLICATE_NAME`
- `ERR_INVALID_REFERENCE`
- `ERR_ENTITY_IN_USE`
- `ERR_INVALID_MONTH`
- `ERR_INVALID_PERCENTAGE`
- `ERR_INVALID_CAPACITY`
- `ERR_MASTER_NOT_FOUND`

### 22. Event Hooks (Future)
Future domain events to be published (Future Enhancements):
- `DestinationCreated`
- `DestinationUpdated`
- `DestinationDeactivated`
- `VehicleTypeCreated`
- `MealPlanUpdated`
- `PackageCategoryUpdated`
- `TaxConfigurationChanged`

### 23. Caching Strategy
- **Lookup APIs**: Cacheable
- **Master Lists**: Cacheable
- **Detail APIs**: Cacheable
- **Create/Update/Delete**: Invalidate cache
Mark cache implementation as a future enhancement.

### 24. Import / Export Rules
Bulk data management support (Future Enhancements):
- CSV Import
- Excel Import
- CSV Export
- Excel Export
- Validation report for failed rows
- Partial success support

### 25. Localization Support
Fields such as `name` and `description` may support multilingual translations in future versions. DTO structure should remain unchanged.

### 26. Security Notes
- Every endpoint requires authentication.
- Write permissions require authorization.
- Audit fields cannot be modified by clients.
- Soft-deleted entities cannot be updated.
- Inactive records cannot appear in lookup APIs.

### 27. Performance Guidelines
- Lookup APIs should only select: `id`, `name`, `code`.
- List APIs must always paginate.
- Avoid loading unnecessary related entities.
- Use indexes on: `code`, `name`, `display_order`, `is_active`.

### 28. Testing Requirements
Every Master entity should have tests for:
- Create
- Update
- Delete
- Get
- List
- Search
- Filtering
- Sorting
- Duplicate validation
- Permission validation
- Dependency validation
- Soft delete
- Lookup endpoint

### 29. Bulk APIs
Optional future endpoints for bulk operations (Future Enhancements):
- `POST /masters/<entity>/bulk`
- `PUT /masters/<entity>/bulk`
- `POST /masters/import`
- `POST /masters/export`

### 30. Future Extensibility
New master entities (e.g., Airline, Airport, Room Type, Vendor Category, Supplier Type, Tour Theme, Language, Travel Insurance) **must follow exactly the same DTO structure**. No new DTO pattern should be introduced.

### 31. Implementation Notes & Module Responsibility
- The Master module **only stores reusable reference data**. 
- Business modules must reference Master IDs instead of storing duplicate values. 
- The Master module must never contain business transactions or business workflow logic.

### 32. Optimistic Locking
To prevent concurrent update conflicts, every master entity must support optimistic locking using a `version` integer field or checking `updated_at`. For phase 1, we include `version` in DetailResponses.

---

# Master Modules

1. Destination
2. Package Category
3. Hotel Category
4. Vehicle Type
5. Meal Plan
6. Activity Type
7. Season
8. Cancellation Policy
9. Payment Method
10. Currency
11. Country
12. State
13. Tax Configuration

---

# Common Audit Information

Almost every master table supports these standard audit fields in its `DetailResponse`:

```json
{
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T15:30:00Z"
    }
}
```

---

# 1. Destination DTOs

### 1.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/destinations`
  - `GET /masters/destinations/{id}`
  - `POST /masters/destinations`
  - `PUT /masters/destinations/{id}`
  - `DELETE /masters/destinations/{id}`
- **Permissions**:
  - `master.destination.read`
  - `master.destination.create`
  - `master.destination.update`
  - `master.destination.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`, `state` (via join), `country` (via join)
- **Filtering Rules**: `is_active`, `country_id`, `state`
- **Duplicate Validation**: Duplicate `code`, Duplicate `slug`
- **Dependency Rules**: Cannot deactivate if referenced by Packages or Proposals. Return validation error.

### 1.2 CreateDestinationRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Munnar |
| code | string | Yes | Uppercase | MUNNAR |
| slug | string | Yes | URL Slug | munnar |
| state_id | uuid | Yes | Valid FK | uuid |
| country_id | uuid | Yes | Valid FK | uuid |
| description | string | No | Max 1000 | Hill station |
| cover_image | string | No | URL | https://... |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Munnar",
    "code": "MUNNAR",
    "slug": "munnar",
    "state_id": "UUID v4",
    "country_id": "UUID v4",
    "description": "Beautiful hill station",
    "cover_image": "https://cloudinary.com/munnar.jpg",
    "display_order": 1,
    "is_active": true
}
```

### 1.3 UpdateDestinationRequest

All fields from CreateDestinationRequest are optional.

### 1.4 DestinationSummaryResponse

```json
{
    "id": "UUID v4",
    "name": "Munnar",
    "code": "MUNNAR",
    "is_active": true
}
```

### 1.5 DestinationDetailResponse

```json
{
    "id": "UUID v4",
    "name": "Munnar",
    "code": "MUNNAR",
    "slug": "munnar",
    "state_id": "UUID v4",
    "country_id": "UUID v4",
    "description": "Beautiful hill station",
    "cover_image": "https://cloudinary.com/munnar.jpg",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T15:30:00Z"
    }
}
```

### 1.6 DestinationListResponse

```json
{
    "items": [
        {
            "id": "UUID v4",
            "name": "Munnar",
            "code": "MUNNAR",
            "state": "Kerala",
            "country": "India",
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
```

---

# 2. Package Category DTOs

### 2.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/package-categories`
  - `GET /masters/package-categories/{id}`
  - `POST /masters/package-categories`
  - `PUT /masters/package-categories/{id}`
  - `DELETE /masters/package-categories/{id}`
- **Permissions**:
  - `master.package-category.read`
  - `master.package-category.create`
  - `master.package-category.update`
  - `master.package-category.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Packages. Return validation error.

### 2.2 CreatePackageCategoryRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Adventure |
| code | string | Yes | Uppercase | ADVENTURE |
| description | string | No | Max 255 | Adventure Tours |
| icon | string | No | Max 100 | mountain |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Adventure",
    "code": "ADVENTURE",
    "description": "Adventure Tours",
    "icon": "mountain",
    "display_order": 1,
    "is_active": true
}
```

### 2.3 UpdatePackageCategoryRequest

All fields from CreatePackageCategoryRequest are optional.

### 2.4 PackageCategorySummaryResponse

```json
{
    "id": "UUID v4",
    "name": "Adventure",
    "code": "ADVENTURE",
    "is_active": true
}
```

### 2.5 PackageCategoryDetailResponse

```json
{
    "id": "UUID v4",
    "name": "Adventure",
    "code": "ADVENTURE",
    "description": "Adventure Tours",
    "icon": "mountain",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 2.6 PackageCategoryListResponse

```json
{
    "items": [
        // PackageCategorySummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 3. Hotel Category DTOs

### 3.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/hotel-categories`
  - `GET /masters/hotel-categories/{id}`
  - `POST /masters/hotel-categories`
  - `PUT /masters/hotel-categories/{id}`
  - `DELETE /masters/hotel-categories/{id}`
- **Permissions**:
  - `master.hotel-category.read`
  - `master.hotel-category.create`
  - `master.hotel-category.update`
  - `master.hotel-category.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Hotels. Return validation error.

### 3.2 CreateHotelCategoryRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Resort |
| code | string | Yes | Uppercase | RESORT |
| description | string | No | Max 255 | Resort style |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Resort",
    "code": "RESORT",
    "description": "Resort style",
    "display_order": 1,
    "is_active": true
}
```

### 3.3 UpdateHotelCategoryRequest

All fields are optional.

### 3.4 HotelCategorySummaryResponse

```json
{
    "id": "UUID v4",
    "name": "Resort",
    "code": "RESORT",
    "is_active": true
}
```

### 3.5 HotelCategoryDetailResponse

```json
{
    "id": "UUID v4",
    "name": "Resort",
    "code": "RESORT",
    "description": "Resort style",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 3.6 HotelCategoryListResponse

```json
{
    "items": [
        // HotelCategorySummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 4. Vehicle Type DTOs

### 4.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/vehicle-types`
  - `GET /masters/vehicle-types/{id}`
  - `POST /masters/vehicle-types`
  - `PUT /masters/vehicle-types/{id}`
  - `DELETE /masters/vehicle-types/{id}`
- **Permissions**:
  - `master.vehicle-type.read`
  - `master.vehicle-type.create`
  - `master.vehicle-type.update`
  - `master.vehicle-type.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`, `description`
- **Filtering Rules**: `is_active`, `capacity`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if used in active Bookings. Return validation error.

### 4.2 CreateVehicleTypeRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | SUV |
| code | string | Yes | Uppercase | SUV |
| description | string | No | Max 255 | Sport Utility |
| capacity | integer | Yes | >=1 | 6 |
| luggage_capacity | integer | Yes | >=0 | 4 |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "SUV",
    "code": "SUV",
    "description": "Sport Utility",
    "capacity": 6,
    "luggage_capacity": 4,
    "display_order": 1,
    "is_active": true
}
```

### 4.3 UpdateVehicleTypeRequest

All fields are optional.

### 4.4 VehicleTypeSummaryResponse

```json
{
    "id": "UUID v4",
    "name": "SUV",
    "code": "SUV",
    "is_active": true
}
```

### 4.5 VehicleTypeDetailResponse

```json
{
    "id": "UUID v4",
    "name": "SUV",
    "code": "SUV",
    "description": "Sport Utility",
    "capacity": 6,
    "luggage_capacity": 4,
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 4.6 VehicleTypeListResponse

```json
{
    "items": [
        // VehicleTypeSummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 5. Meal Plan DTOs

### 5.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/meal-plans`
  - `GET /masters/meal-plans/{id}`
  - `POST /masters/meal-plans`
  - `PUT /masters/meal-plans/{id}`
  - `DELETE /masters/meal-plans/{id}`
- **Permissions**:
  - `master.meal-plan.read`
  - `master.meal-plan.create`
  - `master.meal-plan.update`
  - `master.meal-plan.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Packages. Return validation error.

### 5.2 CreateMealPlanRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | MAP |
| code | string | Yes | Uppercase | MAP |
| description | string | No | Max 255 | Breakfast and Dinner |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "MAP",
    "code": "MAP",
    "description": "Breakfast and Dinner",
    "display_order": 1,
    "is_active": true
}
```

### 5.3 UpdateMealPlanRequest

All fields are optional.

### 5.4 MealPlanSummaryResponse

```json
{
    "id": "UUID v4",
    "name": "MAP",
    "code": "MAP",
    "is_active": true
}
```

### 5.5 MealPlanDetailResponse

```json
{
    "id": "UUID v4",
    "name": "MAP",
    "code": "MAP",
    "description": "Breakfast and Dinner",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 5.6 MealPlanListResponse

```json
{
    "items": [
        // MealPlanSummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 6. Activity Type DTOs

### 6.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/activity-types`
  - `GET /masters/activity-types/{id}`
  - `POST /masters/activity-types`
  - `PUT /masters/activity-types/{id}`
  - `DELETE /masters/activity-types/{id}`
- **Permissions**:
  - `master.activity-type.read`
  - `master.activity-type.create`
  - `master.activity-type.update`
  - `master.activity-type.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Activities. Return validation error.

### 6.2 CreateActivityTypeRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Trekking |
| code | string | Yes | Uppercase | TREKKING |
| description | string | No | Max 255 | Trekking |
| icon | string | No | Max 100 | mountain |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Trekking",
    "code": "TREKKING",
    "description": "Trekking",
    "icon": "mountain",
    "display_order": 1,
    "is_active": true
}
```

### 6.3 UpdateActivityTypeRequest

All fields are optional.

### 6.4 ActivityTypeSummaryResponse

```json
{
    "id": "UUID v4",
    "name": "Trekking",
    "code": "TREKKING",
    "is_active": true
}
```

### 6.5 ActivityTypeDetailResponse

```json
{
    "id": "UUID v4",
    "name": "Trekking",
    "code": "TREKKING",
    "description": "Trekking",
    "icon": "mountain",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 6.6 ActivityTypeListResponse

```json
{
    "items": [
        // ActivityTypeSummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 7. Season DTOs

### 7.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/seasons`
  - `GET /masters/seasons/{id}`
  - `POST /masters/seasons`
  - `PUT /masters/seasons/{id}`
  - `DELETE /masters/seasons/{id}`
- **Permissions**:
  - `master.season.read`
  - `master.season.create`
  - `master.season.update`
  - `master.season.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`, `start_month`, `end_month`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Pricing/Rates. Return validation error.

### 7.2 CreateSeasonRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Peak Season |
| code | string | Yes | Uppercase | PEAK_SEASON |
| description | string | No | Max 255 | Peak Tourism |
| start_month | integer | Yes | 1-12 | 10 |
| end_month | integer | Yes | 1-12 | 2 |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Peak Season",
    "code": "PEAK_SEASON",
    "description": "Peak Tourism",
    "start_month": 10,
    "end_month": 2,
    "display_order": 1,
    "is_active": true
}
```

### 7.3 UpdateSeasonRequest

All fields are optional.

### 7.4 SeasonSummaryResponse

```json
{
    "id": "UUID v4",
    "name": "Peak Season",
    "code": "PEAK_SEASON",
    "is_active": true
}
```

### 7.5 SeasonDetailResponse

```json
{
    "id": "UUID v4",
    "name": "Peak Season",
    "code": "PEAK_SEASON",
    "description": "Peak Tourism",
    "start_month": 10,
    "end_month": 2,
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 7.6 SeasonListResponse

```json
{
    "items": [
        // SeasonSummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 8. Cancellation Policy DTOs

### 8.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/cancellation-policies`
  - `GET /masters/cancellation-policies/{id}`
  - `POST /masters/cancellation-policies`
  - `PUT /masters/cancellation-policies/{id}`
  - `DELETE /masters/cancellation-policies/{id}`
- **Permissions**:
  - `master.cancellation-policy.read`
  - `master.cancellation-policy.create`
  - `master.cancellation-policy.update`
  - `master.cancellation-policy.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Bookings. Return validation error.

### 8.2 CreateCancellationPolicyRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Standard |
| code | string | Yes | Uppercase | STANDARD |
| description | string | No | Max 255 | Standard Cancellation |
| refund_before_days | integer | Yes | >=0 | 7 |
| refund_percentage | float | Yes | 0-100 | 100 |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Standard",
    "code": "STANDARD",
    "description": "Standard Cancellation",
    "refund_before_days": 7,
    "refund_percentage": 100,
    "display_order": 1,
    "is_active": true
}
```

### 8.3 UpdateCancellationPolicyRequest

All fields are optional.

### 8.4 CancellationPolicySummaryResponse

```json
{
    "id": "UUID v4",
    "name": "Standard",
    "code": "STANDARD",
    "is_active": true
}
```

### 8.5 CancellationPolicyDetailResponse

```json
{
    "id": "UUID v4",
    "name": "Standard",
    "code": "STANDARD",
    "description": "Standard Cancellation",
    "refund_before_days": 7,
    "refund_percentage": 100,
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 8.6 CancellationPolicyListResponse

```json
{
    "items": [
        // CancellationPolicySummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 9. Payment Method DTOs

### 9.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/payment-methods`
  - `GET /masters/payment-methods/{id}`
  - `POST /masters/payment-methods`
  - `PUT /masters/payment-methods/{id}`
  - `DELETE /masters/payment-methods/{id}`
- **Permissions**:
  - `master.payment-method.read`
  - `master.payment-method.create`
  - `master.payment-method.update`
  - `master.payment-method.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Payments. Return validation error.

### 9.2 CreatePaymentMethodRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | UPI |
| code | string | Yes | Uppercase | UPI |
| description | string | No | Max 255 | UPI Transfer |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "UPI",
    "code": "UPI",
    "description": "UPI Transfer",
    "display_order": 1,
    "is_active": true
}
```

### 9.3 UpdatePaymentMethodRequest

All fields are optional.

### 9.4 PaymentMethodSummaryResponse

```json
{
    "id": "UUID v4",
    "name": "UPI",
    "code": "UPI",
    "is_active": true
}
```

### 9.5 PaymentMethodDetailResponse

```json
{
    "id": "UUID v4",
    "name": "UPI",
    "code": "UPI",
    "description": "UPI Transfer",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 9.6 PaymentMethodListResponse

```json
{
    "items": [
        // PaymentMethodSummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 10. Currency DTOs

### 10.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/currencies`
  - `GET /masters/currencies/{id}`
  - `POST /masters/currencies`
  - `PUT /masters/currencies/{id}`
  - `DELETE /masters/currencies/{id}`
- **Permissions**:
  - `master.currency.read`
  - `master.currency.create`
  - `master.currency.update`
  - `master.currency.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Finances. Return validation error.

### 10.2 CreateCurrencyRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Indian Rupee |
| code | string | Yes | Uppercase | INR |
| symbol | string | Yes | Max 10 | ₹ |
| description | string | No | Max 255 | Indian Currency |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Indian Rupee",
    "code": "INR",
    "symbol": "₹",
    "description": "Indian Currency",
    "display_order": 1,
    "is_active": true
}
```

### 10.3 UpdateCurrencyRequest

All fields are optional.

### 10.4 CurrencySummaryResponse

```json
{
    "id": "UUID v4",
    "name": "Indian Rupee",
    "code": "INR",
    "is_active": true
}
```

### 10.5 CurrencyDetailResponse

```json
{
    "id": "UUID v4",
    "name": "Indian Rupee",
    "code": "INR",
    "symbol": "₹",
    "description": "Indian Currency",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 10.6 CurrencyListResponse

```json
{
    "items": [
        // CurrencySummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 11. Country DTOs

### 11.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/countries`
  - `GET /masters/countries/{id}`
  - `POST /masters/countries`
  - `PUT /masters/countries/{id}`
  - `DELETE /masters/countries/{id}`
- **Permissions**:
  - `master.country.read`
  - `master.country.create`
  - `master.country.update`
  - `master.country.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`
- **Duplicate Validation**: Duplicate ISO `code`
- **Dependency Rules**: Cannot deactivate if States exist. Return validation error.

### 11.2 CreateCountryRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | India |
| code | string | Yes | Uppercase | IN |
| phone_code | string | Yes | Max 10 | +91 |
| description | string | No | Max 255 | India |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "India",
    "code": "IN",
    "phone_code": "+91",
    "description": "India",
    "display_order": 1,
    "is_active": true
}
```

### 11.3 UpdateCountryRequest

All fields are optional.

### 11.4 CountrySummaryResponse

```json
{
    "id": "UUID v4",
    "name": "India",
    "code": "IN",
    "is_active": true
}
```

### 11.5 CountryDetailResponse

```json
{
    "id": "UUID v4",
    "name": "India",
    "code": "IN",
    "phone_code": "+91",
    "description": "India",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 11.6 CountryListResponse

```json
{
    "items": [
        // CountrySummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 12. State DTOs

### 12.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/states`
  - `GET /masters/states/{id}`
  - `POST /masters/states`
  - `PUT /masters/states/{id}`
  - `DELETE /masters/states/{id}`
- **Permissions**:
  - `master.state.read`
  - `master.state.create`
  - `master.state.update`
  - `master.state.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`, `country_id`
- **Duplicate Validation**: Duplicate `code` within same country
- **Dependency Rules**: Cannot deactivate if Destinations exist. Return validation error.

### 12.2 CreateStateRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Kerala |
| code | string | Yes | Uppercase | KL |
| country_id | uuid | Yes | Valid FK | uuid |
| description | string | No | Max 255 | Kerala State |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Kerala",
    "code": "KL",
    "country_id": "UUID v4",
    "description": "Kerala State",
    "display_order": 1,
    "is_active": true
}
```

### 12.3 UpdateStateRequest

All fields are optional.

### 12.4 StateSummaryResponse

```json
{
    "id": "UUID v4",
    "name": "Kerala",
    "code": "KL",
    "is_active": true
}
```

### 12.5 StateDetailResponse

```json
{
    "id": "UUID v4",
    "name": "Kerala",
    "code": "KL",
    "country_id": "UUID v4",
    "description": "Kerala State",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 12.6 StateListResponse

```json
{
    "items": [
        // StateSummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```

---

# 13. Tax Configuration DTOs

### 13.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /masters/tax-configurations`
  - `GET /masters/tax-configurations/{id}`
  - `POST /masters/tax-configurations`
  - `PUT /masters/tax-configurations/{id}`
  - `DELETE /masters/tax-configurations/{id}`
- **Permissions**:
  - `master.tax-configuration.read`
  - `master.tax-configuration.create`
  - `master.tax-configuration.update`
  - `master.tax-configuration.delete`
- **Searchable Fields** (case-insensitive): `name`, `code`
- **Filtering Rules**: `is_active`, `percentage`
- **Duplicate Validation**: Duplicate `code`
- **Dependency Rules**: Cannot deactivate if referenced by Invoices. Return validation error.

### 13.2 CreateTaxConfigurationRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | GST |
| code | string | Yes | Uppercase | GST |
| percentage | float | Yes | 0-100 | 5 |
| description | string | No | Max 255 | Goods & Services |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "GST",
    "code": "GST",
    "percentage": 5,
    "description": "Goods & Services",
    "display_order": 1,
    "is_active": true
}
```

### 13.3 UpdateTaxConfigurationRequest

All fields are optional.

### 13.4 TaxConfigurationSummaryResponse

```json
{
    "id": "UUID v4",
    "name": "GST",
    "code": "GST",
    "is_active": true
}
```

### 13.5 TaxConfigurationDetailResponse

```json
{
    "id": "UUID v4",
    "name": "GST",
    "code": "GST",
    "percentage": 5,
    "description": "Goods & Services",
    "display_order": 1,
    "is_active": true,
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 13.6 TaxConfigurationListResponse

```json
{
    "items": [
        // TaxConfigurationSummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 250,
        "total_pages": 13
    }
}
```
