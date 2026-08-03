# Master Module Implementation Plan

This implementation plan outlines the architecture and execution steps for migrating the Master Module, exactly per the frozen `03_master_dtos.md` contract.

## Proposed Execution Phases

To prevent technical debt, ensure referential integrity, and maximize code reuse, we will execute the migration in four distinct phases:

---

### Phase 0 – Shared Infrastructure ✅
Build the core architecture that all master entities will share:
- **`BaseModel`** (`app/core/base_model.py`): UUID PK, `created_at`, `updated_at`, `created_by`, `updated_by`, `version`, `is_active`.
- **`BaseRepository`** (`app/infrastructure/persistence/base_repository.py`): Natively supports `apply_search()`, `apply_sort()`, `apply_filters()`, `apply_pagination()`, `count()`.
- **`BaseService`** (`app/core/base_service.py`): Transaction helpers (`commit`, `rollback`), response formatters, and `check_optimistic_lock()`.

### Phase 0.5 – Shared Domain Objects ✅
- `app/common/pagination.py`, `filters.py`, `search.py`, `sorting.py`
- `app/domain/exceptions/` (package: `business.py`, `validation.py`, `not_found.py`, `auth.py`)
- `app/infrastructure/responses/api_response.py` (`{ success, message, data/errors }` envelope)
- `app/validators/common.py` (`validate_code`, `validate_slug`, `validate_fk`, `validate_display_order`)

---

### Phase 1 – Foundation Masters (8-Step Pipeline)

We implement entities in strict dependency order: `Country → State → District → Destination`.
Every entity follows the **same 8-step pipeline** documented below.

---

#### The Standard 8-Step Pipeline

**Step 1 – Model**
Define the SQLAlchemy model extending `BaseModel`. Finalize all columns, indexes, and FK references. Tweak freely before cutting a migration.

**Step 2 – Migration**
Once the model is stable, generate a clean single Alembic migration:
```
flask db migrate -m "add {entity} table"
flask db upgrade
```
Keeping migration as its own step prevents unnecessary Alembic revisions.

**Step 3 – Repository** *(persistence-only)*
The repository is responsible only for database queries. No business logic.

Standard methods for every entity:
- `get_by_id(id)` → entity or None
- `find_by_code(code)` → entity or None
- `list_active(**filters)` → list of entities (filtered, sorted, paginated via BaseRepository)
- `lookup(search_query)` → lightweight id/name/code list for dropdowns
- `save(entity)` / `delete(entity)`

> ❌ No duplicate validation, no FK existence checks, no hierarchy validation inside repositories. Those belong in the service layer.

**Step 4 – DTOs & Schemas**
Build all 6 Marshmallow schemas per the frozen `03_master_dtos.md` contract:
- `Create<Entity>Request` — with field-level validation
- `Update<Entity>Request` — with `version` field for optimistic locking
- `<Entity>SummaryResponse` — `id, code, name, is_active`
- `<Entity>DetailResponse` — full detail including audit fields
- `<Entity>ListResponse` — `items: SummaryResponse[], pagination`
- `<Entity>LookupResponse` — `id, name, code`

**Step 5 – Service Layer**
Business logic lives exclusively here. Follow this checklist for every operation:

*Create*
1. ✅ Validate DTO (Marshmallow)
2. ✅ Duplicate Check (code uniqueness)
3. ✅ FK Validation (verify referenced entities exist)
4. ✅ Business Rules (e.g., hierarchy validation)
5. ✅ Set Audit Fields (`created_by`, `updated_by`)
6. ✅ Persist via Repository
7. ✅ Commit

*Update*
1. ✅ Entity Exists
2. ✅ Optimistic Lock Check (`request.version == entity.version`)
3. ✅ Validate DTO
4. ✅ Duplicate Check (exclude self)
5. ✅ FK Validation
6. ✅ Apply changes, set `updated_by`, increment `version`
7. ✅ Commit

*Delete*
1. ✅ Entity Exists
2. ✅ Dependency Check (prevent delete if referenced by child records)
3. ✅ Soft Delete (`is_active = False`)
4. ✅ Commit

**Step 6 – Routes (Standard Contract)**
Every master entity exposes the same 6 endpoints:

```
GET    /{entities}           → list with search/filter/sort/pagination
GET    /{entities}/{id}      → detail by ID
GET    /{entities}/lookup    → lightweight dropdown list
POST   /{entities}           → create
PUT    /{entities}/{id}      → update
DELETE /{entities}/{id}      → soft delete
```

All endpoints require the corresponding permission (`master.{entity}.*`) and return the standard `{ success, message, data }` envelope.

**Step 7 – Tests**
Comprehensive test coverage for each entity:

| Test Case | Description |
|---|---|
| `test_create_success` | Valid create returns 201 + Location header |
| `test_duplicate_code` | Returns 409 on duplicate code |
| `test_create_validation_error` | Returns 400 on missing required fields |
| `test_get_by_id` | Returns full DetailResponse |
| `test_get_invalid_uuid` | Returns 400 on malformed UUID |
| `test_get_not_found` | Returns 404 on unknown ID |
| `test_list_pagination` | Returns correct page/page_size/total |
| `test_list_search` | Search by name/code |
| `test_list_filter` | Filter by `is_active` |
| `test_list_sort` | Sort by name/code/display_order |
| `test_list_empty` | Returns empty list, not error |
| `test_update_success` | Valid update returns 200 |
| `test_update_version_conflict` | Returns 409 on optimistic lock mismatch |
| `test_update_not_found` | Returns 404 |
| `test_delete_soft` | Entity marked inactive, not removed |
| `test_delete_not_found` | Returns 404 |
| `test_lookup_endpoint` | Returns id/name/code list |
| `test_unauthorized` | Returns 401 without JWT |
| `test_forbidden` | Returns 403 without required permission |

**Step 8 – Seed Data**
Seed scripts are organized under `seeds/` and executed in dependency order:

```
seeds/
    001_countries.py
    002_states.py
    003_districts.py
    004_destinations.py
    005_currencies.py
    ...
```

A single runner executes them all in order:
```bash
python manage.py seed
```

This scales cleanly as Phase 2 entities are added.

---

#### Phase 1A – Country Module ✅
8-step pipeline applied to `Country`.

**Model fields**: `id, code, name, description, display_order, phone_code, currency_code, is_active, version, created_at, updated_at, created_by, updated_by`

**Route prefix**: `GET/POST /api/v1/masters/countries`

**Seed file**: `seeds/001_countries.py` (India, USA, UK, Singapore, UAE, Sri Lanka, Nepal, Thailand)

---

#### Phase 1B – State Module ✅
8-step pipeline applied to `State`.

**Model fields**: `id, code, name, description, display_order, country_id (FK), is_active, version, ...`

**Route prefix**: `GET/POST /api/v1/masters/states`

**Additional repo methods**: `find_by_code_and_country(code, country_id)`, `list_by_country(country_id)`

**Seed file**: `seeds/002_states.py` (Kerala, Tamil Nadu, Maharashtra, Karnataka, Rajasthan, Goa, Delhi)

---

#### Phase 1C – District Module
8-step pipeline applied to `District`.

**Model fields**: `id, code, name, description, display_order, state_id (FK), country_id (FK), is_active, version, ...`

**Route prefix**: `GET/POST /api/v1/masters/districts`

**Additional repo methods**: `find_by_code_and_state(code, state_id)`, `list_by_state(state_id)`

**Service extra rule**: Validate that `state_id` belongs to `country_id`.

**Seed file**: `seeds/003_districts.py` (Idukki, Ernakulam, Thrissur, Wayanad, Munnar-district, Alappuzha for Kerala; etc.)

---

#### Phase 1D – Destination Module
8-step pipeline applied to `Destination`.

**Model fields**: `id, code, name, description, display_order, district_id (FK), state_id (FK), country_id (FK), is_active, version, ...`

**Route prefix**: `GET/POST /api/v1/masters/destinations`

**Query filters**: `?district_id=`, `?state_id=`, `?country_id=`

**Service extra rule**: Validate full `district → state → country` hierarchy.

**Seed file**: `seeds/004_destinations.py` (Munnar → Idukki, Kochi → Ernakulam, Thekkady → Idukki, Alleppey → Alappuzha, Mumbai → Mumbai City)

---

### Phase 2 – Independent Masters (8-Step Pipeline)

Once Phase 1 is solid, roll out the remaining 10 independent master entities using the exact same 8-step pipeline. Each gets its own numbered seed file:

| # | Entity | Seed File |
|---|---|---|
| 1 | Package Category | `seeds/005_package_categories.py` |
| 2 | Hotel Category | `seeds/006_hotel_categories.py` |
| 3 | Meal Plan | `seeds/007_meal_plans.py` |
| 4 | Activity Type | `seeds/008_activity_types.py` |
| 5 | Vehicle Type | `seeds/009_vehicle_types.py` |
| 6 | Season | `seeds/010_seasons.py` |
| 7 | Payment Method | `seeds/011_payment_methods.py` (UPI, Cash, Card, Bank Transfer) |
| 8 | Currency | `seeds/012_currencies.py` (INR, USD, EUR, AED, SGD) |
| 9 | Cancellation Policy | `seeds/013_cancellation_policies.py` |
| 10 | Tax Configuration | `seeds/014_tax_configurations.py` |

---

## Verification Plan

### Automated Tests
Every entity test file covers the 19-case checklist from Step 7 above, validating:
- CRUD & Lookup
- Search, Filter, Sort, Pagination
- Duplicate Code (409), Optimistic Lock (409), Dependency Delete (409)
- Invalid UUID (400), Validation Errors (400)
- Unauthorized (401), Forbidden (403)
- Empty result sets

### Manual Verification
Boot the server and verify all endpoints return the standard `{ success, message, data }` or `{ success, message, errors }` envelope with correct HTTP status codes.
