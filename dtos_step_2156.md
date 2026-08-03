# 03 Master DTOs
## Reusable Configurations, Catalogs, and Reference Data

The Master module stores reusable reference data shared across multiple business modules.

These entities are maintained by administrators and referenced by CRM, Package, Proposal, Booking, Operations, Finance, and Reports.

---

# Master Modules

- Destination
- Package Category
- Hotel Category
- Vehicle Type
- Meal Plan
- Activity Type
- Season
- Cancellation Policy
- Payment Method
- Country
- State
- Currency
- Tax Configuration

---

# 1. Destination DTOs

## 1.1 CreateDestinationRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| name | string | Yes | Max 100 | Munnar |
| slug | string | Yes | URL Slug | munnar |
| state | string | Yes | Max 100 | Kerala |
| country | string | Yes | Max 100 | India |
| description | string | No | Max 1000 | Hill station |
| cover_image | string | No | URL | https://... |
| is_active | boolean | No | Default true | true |

### Example

```json
{
    "name": "Munnar",
    "slug": "munnar",
    "state": "Kerala",
    "country": "India",
    "description": "Beautiful hill station",
    "cover_image": "https://cloudinary.com/munnar.jpg",
    "is_active": true
}
```

---

## 1.2 UpdateDestinationRequest

Supports all fields from CreateDestinationRequest as optional.

---

## 1.3 DestinationSummaryResponse

```json
{
    "id": "uuid-destination",
    "name": "Munnar",
    "state": "Kerala",
    "country": "India",
    "is_active": true
}
```

---

## 1.4 DestinationDetailResponse

```json
{
    "id": "uuid-destination",
    "name": "Munnar",
    "slug": "munnar",
    "state": "Kerala",
    "country": "India",
    "description": "Beautiful hill station",
    "cover_image": "https://cloudinary.com/munnar.jpg",
    "is_active": true,
    "audit_info": {
        "created_by": "uuid-user",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "uuid-user",
        "updated_at": "2026-07-20T15:30:00Z"
    }
}
```

---

# 2. Package Category DTOs

## CreatePackageCategoryRequest

```json
{
    "name": "Adventure",
    "code": "ADVENTURE",
    "description": "Adventure Tours",
    "icon": "mountain",
    "is_active": true
}
```

## PackageCategoryResponse

```json
{
    "id": "uuid",
    "name": "Adventure",
    "code": "ADVENTURE",
    "description": "Adventure Tours",
    "icon": "mountain",
    "is_active": true
}
```

---

# 3. Hotel Category DTOs

Examples

- Homestay
- Resort
- 3 Star
- 4 Star
- 5 Star

## CreateHotelCategoryRequest

```json
{
    "name": "Resort",
    "code": "RESORT",
    "is_active": true
}
```

---

# 4. Vehicle Type DTOs

Examples

- Hatchback
- Sedan
- SUV
- Tempo Traveller
- Mini Bus
- Bus

## CreateVehicleTypeRequest

```json
{
    "name": "SUV",
    "capacity": 6,
    "luggage_capacity": 4,
    "is_active": true
}
```

---

# 5. Meal Plan DTOs

Examples

- EP
- CP
- MAP
- AP
- Breakfast Only

## CreateMealPlanRequest

```json
{
    "name": "MAP",
    "description": "Breakfast and Dinner",
    "is_active": true
}
```

---

# 6. Activity Type DTOs

Examples

- Trekking
- Safari
- Boating
- Camping
- Sightseeing
- Water Sports

```json
{
    "name": "Trekking",
    "icon": "mountain",
    "is_active": true
}
```

---

# 7. Season DTOs

Examples

- Summer
- Winter
- Monsoon
- Peak Season
- Off Season

```json
{
    "name": "Peak Season",
    "start_month": 10,
    "end_month": 2,
    "is_active": true
}
```

---

# 8. Cancellation Policy DTOs

```json
{
    "name": "Standard",
    "refund_before_days": 7,
    "refund_percentage": 100,
    "is_active": true
}
```

---

# 9. Payment Method DTOs

Examples

- Cash
- UPI
- Credit Card
- Debit Card
- Net Banking
- Razorpay

```json
{
    "name": "UPI",
    "code": "UPI",
    "is_active": true
}
```

---

# 10. Country DTOs

```json
{
    "name": "India",
    "iso_code": "IN",
    "phone_code": "+91",
    "is_active": true
}
```

---

# 11. State DTOs

```json
{
    "name": "Kerala",
    "country_id": "uuid-country",
    "is_active": true
}
```

---

# 12. Currency DTOs

```json
{
    "code": "INR",
    "symbol": "₹",
    "name": "Indian Rupee",
    "is_active": true
}
```

---

# 13. Tax Configuration DTOs

```json
{
    "name": "GST",
    "percentage": 5,
    "is_active": true
}
```

---

# Common Audit Information

All master entities include:

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

# Used By

| Module | Master Data Used |
|---------|------------------|
| CRM | Destination |
| Package | Destination, Package Category, Hotel Category, Meal Plan, Activity Type |
| Proposal | Destination, Hotel Category, Vehicle Type, Meal Plan, Activity Type |
| Booking | Vehicle Type, Meal Plan |
| Operations | Vehicle Type |
| Finance | Currency, Tax Configuration |
| Reports | All Master References |