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
Every `SummaryResponse` should contain:
- `id`
- `code`
- `name`
- `is_active`

Every `DetailResponse` should additionally contain:
- `description`
- `display_order`
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
Master records are **never physically deleted**. Deletion should only set `is_active = false`. Business modules must ignore inactive master records.

### 6. Uniqueness Rules
The following business constraints apply globally across the platform:
- **Destination**: `code` unique, `slug` unique
- **Package Category**: `code` unique
- **Vehicle Type**: `code` unique
- **Meal Plan**: `code` unique
- **Country**: `iso_code` unique
- **Currency**: `code` unique
- **Tax Configuration**: `code` unique
- **State**: `(country_id, code)` composite unique

### 7. Lookup Support
Every master entity automatically supports lightweight lookup APIs (e.g. `GET /lookup/destinations`, `GET /lookup/vehicle-types`). Lookup responses only return `id`, `name`, and `code`. Nothing else. Full details belong to `DetailResponse`.

### 8. Sorting
Default sorting across all list and lookup APIs:
1. `display_order ASC`
2. `name ASC`

### 9. Filtering
Supported filters across all list APIs:
- `page`, `page_size`
- `search` (checks name/code)
- `is_active` (Only active records are returned by default)
- `sort_by`, `sort_order`

### 10. Audit Rules
Audit fields are **read-only**. Clients must never send audit fields (`created_by`, `created_at`, `updated_by`, `updated_at`). Only `DetailResponse` includes `audit_info`.

### 11. Validation Rules
Common validations apply across all modules:
- **code**: uppercase, unique, letters/numbers/underscore only
- **name**: required, max length 100
- **description**: optional, max length 255
- **display_order**: >=0
- **percentage**: 0–100
- **month**: 1–12
- **capacity**: >=1

### 12. API Behavior
- **Create**: returns `DetailResponse`
- **Update**: returns `DetailResponse`
- **Delete**: returns success response
- **List**: returns `ListResponse`
- **Get**: returns `DetailResponse`

### 13. Future Extensibility
New master entities (e.g., Airline, Airport, Room Type, Vendor Category, Supplier Type, Tour Theme, Language, Travel Insurance) **must follow exactly the same DTO structure**. No new DTO pattern should be introduced.

### 14. Module Responsibility
The Master module **only stores reusable reference data**. Business modules must reference Master IDs. The Master module must never contain business transactions or business workflow logic.

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
    "audit_info": {
        "created_by": "uuid-user",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid-user",
        "updated_at": "2026-07-20T15:30:00Z"
    }
}
```

---

# 1. Destination DTOs

### 1.1 CreateDestinationRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Munnar |
| code | string | Yes | Uppercase | MUNNAR |
| slug | string | Yes | URL Slug | munnar |
| state | string | Yes | Max 100 | Kerala |
| country | string | Yes | Max 100 | India |
| description | string | No | Max 1000 | Hill station |
| cover_image | string | No | URL | https://... |
| display_order | integer | No | >=0 | 1 |
| is_active | boolean | No | Default true | true |

```json
{
    "name": "Munnar",
    "code": "MUNNAR",
    "slug": "munnar",
    "state": "Kerala",
    "country": "India",
    "description": "Beautiful hill station",
    "cover_image": "https://cloudinary.com/munnar.jpg",
    "display_order": 1,
    "is_active": true
}
```

### 1.2 UpdateDestinationRequest

All fields from CreateDestinationRequest are optional.

### 1.3 DestinationSummaryResponse

```json
{
    "id": "uuid-destination",
    "name": "Munnar",
    "code": "MUNNAR",
    "state": "Kerala",
    "country": "India",
    "is_active": true
}
```

### 1.4 DestinationDetailResponse

```json
{
    "id": "uuid-destination",
    "name": "Munnar",
    "code": "MUNNAR",
    "slug": "munnar",
    "state": "Kerala",
    "country": "India",
    "description": "Beautiful hill station",
    "cover_image": "https://cloudinary.com/munnar.jpg",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid-user",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid-user",
        "updated_at": "2026-07-20T15:30:00Z"
    }
}
```

### 1.5 DestinationListResponse

```json
{
    "items": [
        {
            "id": "uuid-destination",
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

### 2.1 CreatePackageCategoryRequest

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

### 2.2 UpdatePackageCategoryRequest

All fields from CreatePackageCategoryRequest are optional.

### 2.3 PackageCategorySummaryResponse

```json
{
    "id": "uuid",
    "name": "Adventure",
    "code": "ADVENTURE",
    "is_active": true
}
```

### 2.4 PackageCategoryDetailResponse

```json
{
    "id": "uuid",
    "name": "Adventure",
    "code": "ADVENTURE",
    "description": "Adventure Tours",
    "icon": "mountain",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 2.5 PackageCategoryListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Adventure",
            "code": "ADVENTURE",
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

# 3. Hotel Category DTOs

### 3.1 CreateHotelCategoryRequest

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

### 3.2 UpdateHotelCategoryRequest

All fields are optional.

### 3.3 HotelCategorySummaryResponse

```json
{
    "id": "uuid",
    "name": "Resort",
    "code": "RESORT",
    "is_active": true
}
```

### 3.4 HotelCategoryDetailResponse

```json
{
    "id": "uuid",
    "name": "Resort",
    "code": "RESORT",
    "description": "Resort style",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 3.5 HotelCategoryListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Resort",
            "code": "RESORT",
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

# 4. Vehicle Type DTOs

### 4.1 CreateVehicleTypeRequest

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

### 4.2 UpdateVehicleTypeRequest

All fields are optional.

### 4.3 VehicleTypeSummaryResponse

```json
{
    "id": "uuid",
    "name": "SUV",
    "code": "SUV",
    "capacity": 6,
    "is_active": true
}
```

### 4.4 VehicleTypeDetailResponse

```json
{
    "id": "uuid",
    "name": "SUV",
    "code": "SUV",
    "description": "Sport Utility",
    "capacity": 6,
    "luggage_capacity": 4,
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 4.5 VehicleTypeListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "SUV",
            "code": "SUV",
            "capacity": 6,
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

# 5. Meal Plan DTOs

### 5.1 CreateMealPlanRequest

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

### 5.2 UpdateMealPlanRequest

All fields are optional.

### 5.3 MealPlanSummaryResponse

```json
{
    "id": "uuid",
    "name": "MAP",
    "code": "MAP",
    "is_active": true
}
```

### 5.4 MealPlanDetailResponse

```json
{
    "id": "uuid",
    "name": "MAP",
    "code": "MAP",
    "description": "Breakfast and Dinner",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 5.5 MealPlanListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "MAP",
            "code": "MAP",
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

# 6. Activity Type DTOs

### 6.1 CreateActivityTypeRequest

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

### 6.2 UpdateActivityTypeRequest

All fields are optional.

### 6.3 ActivityTypeSummaryResponse

```json
{
    "id": "uuid",
    "name": "Trekking",
    "code": "TREKKING",
    "is_active": true
}
```

### 6.4 ActivityTypeDetailResponse

```json
{
    "id": "uuid",
    "name": "Trekking",
    "code": "TREKKING",
    "description": "Trekking",
    "icon": "mountain",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 6.5 ActivityTypeListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Trekking",
            "code": "TREKKING",
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

# 7. Season DTOs

### 7.1 CreateSeasonRequest

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

### 7.2 UpdateSeasonRequest

All fields are optional.

### 7.3 SeasonSummaryResponse

```json
{
    "id": "uuid",
    "name": "Peak Season",
    "code": "PEAK_SEASON",
    "is_active": true
}
```

### 7.4 SeasonDetailResponse

```json
{
    "id": "uuid",
    "name": "Peak Season",
    "code": "PEAK_SEASON",
    "description": "Peak Tourism",
    "start_month": 10,
    "end_month": 2,
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 7.5 SeasonListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Peak Season",
            "code": "PEAK_SEASON",
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

# 8. Cancellation Policy DTOs

### 8.1 CreateCancellationPolicyRequest

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

### 8.2 UpdateCancellationPolicyRequest

All fields are optional.

### 8.3 CancellationPolicySummaryResponse

```json
{
    "id": "uuid",
    "name": "Standard",
    "code": "STANDARD",
    "is_active": true
}
```

### 8.4 CancellationPolicyDetailResponse

```json
{
    "id": "uuid",
    "name": "Standard",
    "code": "STANDARD",
    "description": "Standard Cancellation",
    "refund_before_days": 7,
    "refund_percentage": 100,
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 8.5 CancellationPolicyListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Standard",
            "code": "STANDARD",
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

# 9. Payment Method DTOs

### 9.1 CreatePaymentMethodRequest

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

### 9.2 UpdatePaymentMethodRequest

All fields are optional.

### 9.3 PaymentMethodSummaryResponse

```json
{
    "id": "uuid",
    "name": "UPI",
    "code": "UPI",
    "is_active": true
}
```

### 9.4 PaymentMethodDetailResponse

```json
{
    "id": "uuid",
    "name": "UPI",
    "code": "UPI",
    "description": "UPI Transfer",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 9.5 PaymentMethodListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "UPI",
            "code": "UPI",
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

# 10. Currency DTOs

### 10.1 CreateCurrencyRequest

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

### 10.2 UpdateCurrencyRequest

All fields are optional.

### 10.3 CurrencySummaryResponse

```json
{
    "id": "uuid",
    "name": "Indian Rupee",
    "code": "INR",
    "symbol": "₹",
    "is_active": true
}
```

### 10.4 CurrencyDetailResponse

```json
{
    "id": "uuid",
    "name": "Indian Rupee",
    "code": "INR",
    "symbol": "₹",
    "description": "Indian Currency",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 10.5 CurrencyListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Indian Rupee",
            "code": "INR",
            "symbol": "₹",
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

# 11. Country DTOs

### 11.1 CreateCountryRequest

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

### 11.2 UpdateCountryRequest

All fields are optional.

### 11.3 CountrySummaryResponse

```json
{
    "id": "uuid",
    "name": "India",
    "code": "IN",
    "is_active": true
}
```

### 11.4 CountryDetailResponse

```json
{
    "id": "uuid",
    "name": "India",
    "code": "IN",
    "phone_code": "+91",
    "description": "India",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 11.5 CountryListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "India",
            "code": "IN",
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

# 12. State DTOs

### 12.1 CreateStateRequest

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
    "country_id": "uuid-country",
    "description": "Kerala State",
    "display_order": 1,
    "is_active": true
}
```

### 12.2 UpdateStateRequest

All fields are optional.

### 12.3 StateSummaryResponse

```json
{
    "id": "uuid",
    "name": "Kerala",
    "code": "KL",
    "country_id": "uuid-country",
    "is_active": true
}
```

### 12.4 StateDetailResponse

```json
{
    "id": "uuid",
    "name": "Kerala",
    "code": "KL",
    "country_id": "uuid-country",
    "description": "Kerala State",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 12.5 StateListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "Kerala",
            "code": "KL",
            "country_id": "uuid-country",
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

# 13. Tax Configuration DTOs

### 13.1 CreateTaxConfigurationRequest

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

### 13.2 UpdateTaxConfigurationRequest

All fields are optional.

### 13.3 TaxConfigurationSummaryResponse

```json
{
    "id": "uuid",
    "name": "GST",
    "code": "GST",
    "percentage": 5,
    "is_active": true
}
```

### 13.4 TaxConfigurationDetailResponse

```json
{
    "id": "uuid",
    "name": "GST",
    "code": "GST",
    "percentage": 5,
    "description": "Goods & Services",
    "display_order": 1,
    "is_active": true,
    "audit_info": {
        "created_by": "uuid",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid",
        "updated_at": "2026-07-20T12:30:00Z"
    }
}
```

### 13.5 TaxConfigurationListResponse

```json
{
    "items": [
        {
            "id": "uuid",
            "name": "GST",
            "code": "GST",
            "percentage": 5,
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
