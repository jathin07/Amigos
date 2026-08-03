# 18 Team DTOs
## Team Member Profile, Employee, and Team Management DTOs

This document defines the frozen API contract for the Team domain.

The Team module owns employee/team profile management through `TeamMember`.

Authentication credentials, passwords, JWT tokens, refresh tokens,
login state, and `UserAccount` remain owned by the Authentication module.

TeamMember and UserAccount are separate domain concepts.

---

# 1. Team Member DTOs

## 1.1 API Implementation Guidelines

### Endpoints

- `GET /api/v1/team-members`
- `GET /api/v1/team-members/{id}`
- `POST /api/v1/team-members`
- `PUT /api/v1/team-members/{id}`
- `DELETE /api/v1/team-members/{id}`

### Permissions

- `team.read`
- `team.create`
- `team.update`
- `team.delete`

### Searchable Fields

Search is case-insensitive across:

- `first_name`
- `last_name`
- `display_name`
- `employee_code`
- `official_email`

### Filtering Rules

Supported filters:

- `is_active`
- `department_id`
- `role_id`
- `reporting_manager_id`
- `employment_status`

### Sorting

Supported sortable fields:

- `employee_code`
- `first_name`
- `last_name`
- `display_name`
- `designation`
- `joined_date`
- `created_at`
- `updated_at`

Default:

    sort_by=created_at
    sort_order=desc

### Pagination

Default:

    page=1
    page_size=20

### Duplicate Validation

The following values must be unique:

- `employee_code`
- `official_email`

Duplicate values return:

    409 Conflict

### Soft Delete

DELETE does not physically remove the TeamMember.

Instead:

    is_active = false

Existing historical relationships must remain intact.

### Optimistic Locking

Updates must include the current `version`.

If the supplied version does not match the persisted version:

    409 Conflict
    ERR_CONCURRENT_MODIFICATION

Successful updates increment the version.

### Relationship Validation

When supplied:

- `department_id` must reference an existing active Department.
- `role_id` must reference an existing active Role.
- `reporting_manager_id` must reference an existing active TeamMember.
- A TeamMember cannot be their own reporting manager.

### Employment Validation

If both dates are supplied:

    left_date >= joined_date

An inactive/former employee may retain historical relationships.

---

# 2. CreateTeamMemberRequest

| Field | Type | Required | Nullable | Validation | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| first_name | string | Yes | No | Max 100 | John |
| last_name | string | No | Yes | Max 100 | Doe |
| display_name | string | Yes | No | Max 150 | John Doe |
| avatar_url | string | No | Yes | URL/Text | https://... |
| dob | date | No | Yes | YYYY-MM-DD | 1990-05-15 |
| gender | string | No | Yes | Max 20 | Male |
| employee_code | string | Yes | No | Max 50, Unique | TM001 |
| official_email | string | Yes | No | Email, Max 150, Unique | john.doe@amigos.com |
| personal_email | string | No | Yes | Email, Max 150 | john.doe@gmail.com |
| phone | string | Yes | No | Max 20 | +919876543210 |
| designation | string | No | Yes | Max 100 | Travel Consultant |
| department_id | uuid | No | Yes | Valid active FK | uuid |
| role_id | uuid | No | Yes | Valid active FK | uuid |
| reporting_manager_id | uuid | No | Yes | Valid active TeamMember FK | uuid |
| employment_status | string | No | Yes | Max 50 | FULL_TIME |
| joined_date | date | No | Yes | YYYY-MM-DD | 2026-01-10 |
| left_date | date | No | Yes | >= joined_date | null |
| is_active | boolean | No | No | Default true | true |
| emergency_contact_name | string | No | Yes | Max 150 | Jane Doe |
| emergency_contact_phone | string | No | Yes | Max 20 | +919876543211 |

### Example

```json
{
    "first_name": "John",
    "last_name": "Doe",
    "display_name": "John Doe",
    "employee_code": "TM001",
    "official_email": "john.doe@amigos.com",
    "phone": "+919876543210",
    "designation": "Travel Consultant",
    "department_id": null,
    "role_id": null,
    "reporting_manager_id": null,
    "employment_status": "FULL_TIME",
    "joined_date": "2026-01-10",
    "is_active": true
}
```

---

# 3. UpdateTeamMemberRequest

All mutable TeamMember fields are optional.

`version` is required for optimistic locking.

Example:

```json
{
    "designation": "Senior Travel Consultant",
    "reporting_manager_id": "UUID v4",
    "version": 1
}
```

The following fields MUST NOT be accepted through this DTO:

* `id`
* `created_at`
* `created_by`
* `updated_at`
* `updated_by`

Authentication fields MUST NOT be accepted:

* `username`
* `password`
* `password_hash`
* `access_token`
* `refresh_token`

---

# 4. TeamMemberSummaryResponse

```json
{
    "id": "UUID v4",
    "employee_code": "TM001",
    "display_name": "John Doe",
    "official_email": "john.doe@amigos.com",
    "phone": "+919876543210",
    "designation": "Travel Consultant",
    "employment_status": "FULL_TIME",
    "is_active": true
}
```

---

# 5. TeamMemberDetailResponse

```json
{
    "id": "UUID v4",
    "first_name": "John",
    "last_name": "Doe",
    "display_name": "John Doe",
    "avatar_url": "https://cloudinary.com/avatar.jpg",
    "dob": "1990-05-15",
    "gender": "Male",
    "employee_code": "TM001",
    "official_email": "john.doe@amigos.com",
    "personal_email": "john.doe@gmail.com",
    "phone": "+919876543210",
    "designation": "Travel Consultant",

    "department_id": "UUID v4",
    "role_id": "UUID v4",
    "reporting_manager_id": "UUID v4",

    "employment_status": "FULL_TIME",
    "availability_status": "AVAILABLE",

    "joined_date": "2026-01-10",
    "left_date": null,

    "emergency_contact_name": "Jane Doe",
    "emergency_contact_phone": "+919876543211",

    "is_active": true,
    "version": 1,

    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-01-10T09:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-01-10T09:00:00Z"
    }
}
```

---

# 6. TeamMemberListResponse

```json
{
    "items": [
        {
            "id": "UUID v4",
            "employee_code": "TM001",
            "display_name": "John Doe",
            "official_email": "john.doe@amigos.com",
            "phone": "+919876543210",
            "designation": "Travel Consultant",
            "employment_status": "FULL_TIME",
            "is_active": true
        }
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 50,
        "total_pages": 3
    }
}
```

---

# 7. Team Member / Authentication Boundary

The Team module manages:

* Employee profile
* Employee code
* Contact information
* Department
* Role assignment
* Reporting hierarchy
* Employment status
* Availability
* Join/leave information
* Emergency contacts

The Authentication module manages:

* UserAccount
* Username
* Password hashes
* Login
* Logout
* JWT
* Refresh tokens
* Password reset
* Failed login attempts
* Account locking

Creating a TeamMember MUST NOT automatically invent authentication
credentials unless an explicit business workflow defines account creation.

Team services MUST NOT directly access AuthRepository.

Cross-module authentication operations must use an Auth service contract
or domain event.

---

# 8. Delete Behaviour

DELETE:

```
/api/v1/team-members/{id}
```

performs a soft delete:

```
is_active = false
```

The TeamMember record must not be physically deleted because it may be
referenced by:

* Leads
* Bookings
* Assignments
* Audit records
* Organization records
* Historical transactions

If business rules prohibit deactivation for a particular state, the
service returns:

```
409 Conflict
```

---

# 9. Implementation Constraints

The existing TeamMember SQLAlchemy model is reused.

Do not:

* duplicate TeamMember into app/modules/team/models.py
* move the existing database model during this migration
* alter existing relationships merely to fit the new module
* access another module's repository
* move authentication responsibilities into TeamService

The Team module should provide the modular business/API boundary while
remaining compatible with the existing database schema.
