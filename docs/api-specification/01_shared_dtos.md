# 01 Shared Value Object DTOs
## Reusable Component Schemas

These schemas define the structural templates shared across multiple modules.

---

## 1. Request vs Response Shared DTO Usage Matrix

| DTO | Request Payload | Response Payload |
| :--- | :---: | :---: |
| **`PaginationMeta`** | ❌ | ✅ |
| **`Money`** | ✅ | ✅ |
| **`FileAttachment`** | ✅ | ✅ |
| **`Address`** | ✅ | ✅ |
| **`AuditInfo`** | ❌ | ✅ |
| **`UUIDReference`** | ✅ | ✅ |
| **`ValidationError`** | ❌ | ✅ |
| **`SortOption`** | ✅ | ✅ |
| **`FilterOption`** | ✅ | ❌ |
| **`LookupValue`** | ❌ | ✅ |

> **DateTime Rule**: All datetime fields must use ISO 8601 UTC format (`YYYY-MM-DDTHH:mm:ssZ`). No separate wrapper DTO is needed for simple date strings.

---

## 2. DTO Definitions

### 2.1 `PaginationMeta`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `page` | integer | Yes | No | `> 0` | 1 | 1 |
| `limit` | integer | Yes | No | `> 0` | 15 | 15 |
| `total_records`| integer | Yes | No | `>= 0` | None | 120 |
| `total_pages` | integer | Yes | No | `>= 0` | None | 8 |
| `has_next` | boolean | Yes | No | None | false | true |
| `has_previous`| boolean | Yes | No | None | false | false |

### 2.2 `Money`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `amount` | decimal | Yes | No | `>= 0.00` | None | `12500.00` |
| `currency` | string | Yes | No | Length: 3 | `INR` | `INR` |
| `formatted_amount`| string | No | Yes | Currency formatting | None | `₹12,500.00` |

### 2.3 `FileAttachment`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `file_id` | string | Yes | No | Format: UUID | None | `uuid-file-1` |
| `file_url` | string | Yes | No | Format: URL | None | `https://cloudinary.com/doc.pdf` |
| `file_name` | string | Yes | No | Max length: 255 | None | `receipt.pdf` |
| `extension` | string | Yes | No | Max length: 10 | None | `pdf` |
| `mime_type` | string | Yes | No | Max length: 100 | None | `application/pdf` |
| `size` | integer | Yes | No | `> 0` | None | 204800 |
| `uploaded_at` | string | Yes | No | Format: ISO8601 | None | `2026-07-16T14:48:59Z` |

### 2.4 `Address`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `address_line_1`| string | Yes | No | Max length: 255 | None | `123 Main St` |
| `address_line_2`| string | No | Yes | Max length: 255 | None | `Door No: 4B` |
| `city` | string | Yes | No | Max length: 100 | None | `Coimbatore` |
| `district` | string | No | Yes | Max length: 100 | None | `Coimbatore` |
| `state` | string | Yes | No | Max length: 100 | None | `Tamil Nadu` |
| `postal_code` | string | Yes | No | Max length: 20 | None | `641001` |
| `country` | string | Yes | No | Max length: 100 | `India` | `India` |

### 2.5 `AuditInfo`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `created_by` | string | Yes | No | Format: UUID | None | `uuid-tm-1` |
| `created_at` | string | Yes | No | Format: ISO8601 | None | `2026-07-16T14:48:59Z` |
| `updated_by` | string | No | Yes | Format: UUID | None | `uuid-tm-2` |
| `updated_at` | string | No | Yes | Format: ISO8601 | None | `2026-07-16T14:50:00Z` |
| `deleted_at` | string | No | Yes | Format: ISO8601 | None | `2026-07-16T14:55:00Z` |
| `is_deleted` | boolean | Yes | No | None | false | false |

### 2.6 `UUIDReference`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | string | Yes | No | Format: UUID | None | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |

### 2.7 `ValidationError`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `field` | string | Yes | No | Max length: 100 | None | `phone` |
| `message` | string | Yes | No | Max length: 255 | None | `Phone number is required` |

### 2.8 `SortOption`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `field` | string | Yes | No | Max length: 100 | None | `created_at` |
| `direction` | string | Yes | No | Enum: `asc`, `desc` | `asc` | `desc` |

### 2.9 `FilterOption`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `search` | string | No | Yes | Max length: 255 | None | `coorg` |
| `status` | string | No | Yes | Max length: 100 | None | `ACTIVE` |
| `from_date` | string | No | Yes | Format: ISO8601 | None | `2026-07-16T00:00:00Z` |
| `to_date` | string | No | Yes | Format: ISO8601 | None | `2026-07-20T23:59:59Z` |

### 2.10 `LookupValue`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | string | Yes | No | Format: UUID | None | `uuid-lookup-1` |
| `code` | string | Yes | No | Max length: 100 | None | `BOOKING_CONFIRMED` |
| `name` | string | Yes | No | Max length: 100 | None | `Booking Confirmed` |
| `is_active` | boolean | Yes | No | None | true | true |

---

## 3. Reusable Shared DTO Invariant Rules
1. **Shared DTOs are immutable templates**.
2. **Module DTOs may compose one or more Shared DTOs**.
3. **Shared DTOs must never contain business-specific fields**.
4. **Shared DTOs should remain backward compatible**.
5. **All IDs use UUID strings**.
6. **All timestamps use ISO 8601 UTC**.
7. **Nullability must be explicitly documented**.
