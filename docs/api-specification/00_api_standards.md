# 00 API Standards & Conventions

This document serves as the **Global API Contract** for the Amigos Tourism Platform. Every other specification (API, DTO, Service, Testing, Mobile) must strictly adhere to the standards outlined below.

## API Design Principles
- Resource-oriented REST design
- Predictable URI structure
- Explicit workflow commands
- Backward compatibility
- Stable response contracts
- Consistent error handling
- Stateless communication

## 1. Naming Standards
- **URI Paths**: `kebab-case` (e.g., `/api/v1/trip-plans`)
- **JSON Keys**: `snake_case` (e.g., `trip_start_date`)
- **Query Parameters**: `snake_case` (e.g., `created_from`)
- **Resource Names**: Plural nouns (e.g., `/api/v1/bookings`)
- **Identifiers**: `UUIDv4` exclusively

## 2. URI Standards
URIs must strictly represent resources and their hierarchy without exposing business verbs (except for distinct Workflow/Command endpoints).
- Collection: `GET /api/v1/resources`
- Singleton: `GET /api/v1/resources/{id}`
- Nested Collection: `GET /api/v1/resources/{id}/sub-resources`
- Workflow Command: `POST /api/v1/resources/{id}/confirm`

## 3. HTTP Methods
- **GET**: Idempotent and safe. Retrieves resources or collections. Never alters state.
- **POST**: Non-idempotent creation of new resources, or triggering of specific workflow operations (e.g. `/confirm`).
- **PUT**: Idempotent total replacement of a resource (requires all fields). Used sparingly.
- **PATCH**: Performs partial updates. Implementations **should be designed to be idempotent where practical**, but this is not guaranteed by the HTTP specification.
- **DELETE**: Soft deletes a resource. Requires elevated permissions.

## 4. HTTP Status Codes
- `200 OK`: GET successful, or successful synchronous PUT/PATCH operations.
- `201 Created`: POST successfully created a resource.
- `202 Accepted`: Background jobs queued (e.g., bulk exports, notifications).
- `204 No Content`: Successful DELETE operation. This response **must not** include a response body.
- `400 Bad Request`: Structural validation failure (e.g., malformed JSON, missing required field, invalid query parameter).
- `401 Unauthorized`: Missing, malformed, or expired JWT token.
- `403 Forbidden`: Authenticated, but lacking sufficient RBAC permissions.
- `404 Not Found`: Resource does not exist or was deleted.
- `409 Conflict`: Optimistic concurrency failure or invalid state transition.
- `422 Unprocessable Entity`: Semantic/Business validation failure (e.g., booking dates invalid, traveller count exceeds package capacity).
- `429 Too Many Requests`: Rate limiting thresholds exceeded.
- `500 Internal Server Error`: Uncaught exceptions.
- `503 Service Unavailable`: Dependent service (e.g., database) unreachable.

## 5. Required Headers
- `Authorization`: `Bearer {JWT}` (Required for all secure endpoints)
- `Content-Type`: `application/json` (unless uploading files)
- `Accept`: `application/json`
- `Idempotency-Key`: Required on mutative financial operations (e.g. payments, refunds)
- `If-Match`: Required for optimistic concurrency (e.g. `PUT/PATCH` on `Booking`, `Proposal`, `TripPlan`)
- `X-Correlation-ID`: Optional tracing identifier injected by the client.

## 6. Request Formats
All standard request payloads must be strictly valid JSON. Requests violating structural schema limits (e.g. missing mandatory fields) will fail fast at the request validation layer before reaching business logic (yielding 400 Bad Request).

## 7. Response Envelopes
Responses enforce a universal envelope for both single objects and collections to guarantee frontend structural consistency.

**Success**:
```json
{
  "success": true,
  "data": {},
  "error": null,
  "validation_errors": []
}
```

**Errors**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERR_XYZ",
    "message": "Human readable description",
    "details": {}
  },
  "validation_errors": []
}
```

## 8. Query Parameters
Query parameters manipulate the result set for GET requests.
- **Search**: `?q={term}` (Shorthand for global text searching)
- **Select Fields**: `?fields=id,name,status`
- **Unknown query parameters** are ignored or rejected consistently.
- **Duplicate query parameters** are invalid unless explicitly documented.

## 9. Filtering
Universal filtering grammar supporting exact, ranges, and multi-value queries:
- Equality: `?status[eq]=CONFIRMED`
- Greater Than (Equal): `?price[gte]=10000`
- Less Than (Equal): `?price[lte]=25000`
- Between: `?created_at[between]=2026-01-01,2026-01-31`
- In Array: `?status[in]=CONFIRMED,COMPLETED`

*Note: Multiple filters are ANDed together by default. OR conditions require explicit syntax.*

## 10. Sorting
Sorting is managed via the single `sort` parameter, using a minus sign `-` for descending order.
- Ascending: `?sort=created_at`
- Descending: `?sort=-created_at`
- Multiple: `?sort=name,-price`

*Note: If two records share the same sort field value, the backend applies the primary key as a secondary sort to ensure deterministic, stable pagination.*

## 11. Pagination
Offset pagination is standardized across all list endpoints (except endless streams like audit logs, which use `cursor`).
- **Default Limit**: `20`
- **Maximum Limit**: `100`
- **Page Minimum**: `1` (Page starts at 1)
- **Limit Minimum**: `1`
Example: `?page=2&limit=50`

**Pagination Metadata Envelope**:
For paginated responses, the `meta` object sits alongside the `data` array at the top level of the envelope:
```json
{
  "success": true,
  "data": [...],
  "meta": {
    "page": 2,
    "limit": 50,
    "total": 155,
    "pages": 4
  },
  "error": null,
  "validation_errors": []
}
```

## 12. Error Standards
All error codes begin with an explicit prefix mapping to domain failures:
- `ERR_...`: General business and concurrency rules
- `AUTH_...`: Authentication and Session
- `FIN_...`: Finance constraints
- `BOOK_...`: Booking lifecycle constraints
Example: `ERR_RESOURCE_MODIFIED`

## 13. Versioning
Explicit URI versioning is employed (e.g., `/api/v1/`).
- **Non-Breaking Changes (Allowed without version bump)**: Adding new response fields, adding optional query parameters, adding endpoints.
- **Breaking Changes (Requires `v2`)**: Removing fields, changing existing field data types, making optional parameters mandatory, or renaming endpoints.
- **Deprecation Lifecycle**: Deprecated versions remain supported for 12 months before removal.

## 14. Content Types
The API explicitly supports and validates:
- `application/json`: Default for all data payloads.
- `multipart/form-data`: Required for file uploads.
- `application/pdf`: For report/document generation downloads.
- `text/csv`: For bulk export responses.

## 15. Security Headers
API responses must inject standard security headers:
- `Strict-Transport-Security`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy`
- `Referrer-Policy`
- `Permissions-Policy`

## 16. Concurrency Standards
All mutable root aggregates (`Booking`, `TripPlan`, `Proposal`) expose a `row_version` field. Clients mutating these aggregates must provide the matching `If-Match` header. Failures yield a `409 Conflict`.

## 17. Idempotency
An `Idempotency-Key` header guarantees safe retries for unstable network conditions. It is **strictly enforced** for all financial mutations and other irreversible workflow operations. If a duplicated key is detected within 24 hours, the API returns the previously cached response without re-executing the operation.

## 18. OpenAPI Standards
- All endpoints must be documented via an OpenAPI v3 specification.
- Tags must cluster around Aggregate Roots.
- Every endpoint requires complete 2xx, 4xx, and 5xx JSON response examples.
- Security schemas (`BearerAuth`) must be uniformly applied.
