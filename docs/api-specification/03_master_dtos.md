# 03 Master DTOs
## Reusable Configurations, Catalog Listings, and Core Master References

---

## 1. Request DTOs

### 1.1 `CreatePackageRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `title` | string | Yes | No | Max length: 100 | None | `Munnar Hills` |
| `slug` | string | Yes | No | Format: URL Slug | None | `munnar-hills` |
| `short_description` | string | Yes | No | Max length: 255 | None | `Tea valleys tour` |
| `description` | string | Yes | No | None | None | `Detailed Munnar tour description...` |
| `duration_days` | integer | Yes | No | `> 0` | None | 4 |
| `duration_nights`| integer | Yes | No | `>= 0` | None | 3 |
| `starting_price` | decimal | Yes | No | `> 0` | None | 8500.00 |
| `price_type` | string | Yes | No | Enum: PriceType | `PER_PERSON` | `PER_PERSON` |
| `gallery` | list | No | No | List of images | None | `[]` |
| `destinations` | list | Yes | No | List of Destination mappings | None | `[]` |
| `highlights` | list | No | No | List of package highlights | None | `[]` |
| `inclusions` | list | No | No | List of inclusions | None | `[]` |
| `exclusions` | list | No | No | List of exclusions | None | `[]` |
| `policies` | list | No | No | List of policies | None | `[]` |

```json
{
  "title": "Munnar Hills",
  "slug": "munnar-hills",
  "short_description": "Tea valleys tour",
  "description": "Detailed Munnar tour description...",
  "duration_days": 4,
  "duration_nights": 3,
  "starting_price": 8500.00,
  "price_type": "PER_PERSON",
  "gallery": [
    {
      "image_url": "https://cloudinary.com/munnar1.jpg",
      "display_order": 1
    }
  ],
  "destinations": [
    {
      "destination_id": "uuid-dest-1",
      "display_order": 1
    }
  ],
  "highlights": [
    { "title": "Tea Gardens" }
  ],
  "inclusions": [
    { "description": "Breakfast" }
  ],
  "exclusions": [
    { "description": "Personal Expenses" }
  ],
  "policies": [
    { "policy_type": "Cancellation", "description": "Refundable 7 days prior" }
  ],
  "is_featured": true,
  "is_active": true
}
```

### 1.2 `UpdatePackageRequest`
- All fields from `CreatePackageRequest` are supported but marked as optional.

### 1.3 `CreateDestinationRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `name` | string | Yes | No | Max length: 100 | None | `Munnar` |
| `state` | string | Yes | No | Max length: 100 | None | `Kerala` |

---

## 2. Response DTOs

### 2.1 `PackageSummaryResponse`
```json
{
  "id": "uuid-pkg-1",
  "title": "Munnar Hills",
  "slug": "munnar-hills",
  "starting_price": 8500.00,
  "is_active": true
}
```

### 2.2 `PackageDetailResponse`
```json
{
  "id": "uuid-pkg-1",
  "title": "Munnar Hills",
  "slug": "munnar-hills",
  "short_description": "Tea valleys tour",
  "description": "Detailed Munnar tour description...",
  "duration_days": 4,
  "duration_nights": 3,
  "starting_price": 8500.00,
  "price_type": "PER_PERSON",
  "gallery": [
    { "image_url": "https://cloudinary.com/munnar1.jpg", "display_order": 1 }
  ],
  "destinations": [
    { "id": "uuid-dest-1", "name": "Munnar", "state": "Kerala", "display_order": 1 }
  ],
  "highlights": [
    { "title": "Tea Gardens" }
  ],
  "inclusions": [
    { "description": "Breakfast" }
  ],
  "exclusions": [
    { "description": "Personal Expenses" }
  ],
  "policies": [
    { "policy_type": "Cancellation", "description": "Refundable 7 days prior" }
  ],
  "audit_info": {
    "created_by": "uuid-tm-1",
    "created_at": "2026-07-16T14:48:59Z"
  }
}
```
