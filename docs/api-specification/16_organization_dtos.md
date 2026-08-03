# 16 Organization DTOs
## Organization Configuration, Branches, and Profile DTOs

This document defines the schema definitions, validation rules, field requirements, and JSON types for the Organization module.

---

# 1. Organization DTOs

### 1.1 API Implementation Guidelines
- **Endpoints**:
  - `GET /api/v1/organization`
  - `PUT /api/v1/organization`
- **Permissions**:
  - `organization.read`
  - `organization.update`
- **Searchable Fields**: None (single record configuration)
- **Filtering Rules**: None

### 1.2 CreateOrganizationRequest

| Field | Type | Required | Validation | Example |
| :--- | :--- | :--- | :--- | :--- |
| organization_name | string | Yes | Max 200 | ABC College |
| organization_type_id | uuid | Yes | Valid FK | uuid |
| address | string | No | Text | MG Road, Bangalore |
| city | string | No | Max 100 | Bangalore |
| state | string | No | Max 100 | Karnataka |
| phone | string | No | Max 20 | 0801234567 |
| email | string | No | Email, Max 150 | contact@abccollege.edu |
| website | string | No | Max 200 | www.abccollege.edu |
| notes | string | No | Text | Educational client |
| is_active | boolean | No | Default true | true |
| divisions | array | No | Organization divisions list | See below |
| contact_persons | array | No | Organization contact persons | See below |

#### Divisions Object
- `department`: string (Max 150)
- `course`: string (Max 150)
- `section`: string (Max 50)
- `year`: string (Max 50)
- `semester`: string (Max 50)
- `batch`: string (Max 50)

#### Contact Persons Object
- `name`: string (Required, Max 150)
- `designation`: string (Max 100)
- `phone`: string (Required, Max 20)
- `alternate_phone`: string (Max 20)
- `email`: string (Max 150)
- `is_primary`: boolean (Default false)
- `preferred_contact_method`: string (Max 30)
- `notes`: string (Text)
- `is_active`: boolean (Default true)

```json
{
    "organization_name": "ABC College",
    "organization_type_id": "UUID v4",
    "address": "MG Road, Bangalore",
    "city": "Bangalore",
    "state": "Karnataka",
    "phone": "0801234567",
    "email": "contact@abccollege.edu",
    "is_active": true,
    "divisions": [
        {
            "department": "Computer Science",
            "course": "B.Tech",
            "batch": "2026"
        }
    ],
    "contact_persons": [
        {
            "name": "Dr. Smith",
            "designation": "HOD",
            "phone": "+919876543230",
            "email": "smith@abccollege.edu",
            "is_primary": true
        }
    ]
}
```

### 1.3 UpdateOrganizationRequest

All fields are optional.

### 1.4 OrganizationSummaryResponse

```json
{
    "id": "UUID v4",
    "organization_name": "ABC College",
    "organization_type_id": "UUID v4",
    "phone": "0801234567",
    "email": "contact@abccollege.edu",
    "is_active": true
}
```

### 1.5 OrganizationDetailResponse

```json
{
    "id": "UUID v4",
    "organization_name": "ABC College",
    "organization_type_id": "UUID v4",
    "address": "MG Road, Bangalore",
    "city": "Bangalore",
    "state": "Karnataka",
    "phone": "0801234567",
    "email": "contact@abccollege.edu",
    "website": "www.abccollege.edu",
    "notes": "Educational client",
    "is_active": true,
    "divisions": [
        {
            "id": "UUID v4",
            "department": "Computer Science",
            "course": "B.Tech",
            "section": null,
            "year": null,
            "semester": null,
            "batch": "2026"
        }
    ],
    "contact_persons": [
        {
            "id": "UUID v4",
            "name": "Dr. Smith",
            "designation": "HOD",
            "phone": "+919876543230",
            "alternate_phone": null,
            "email": "smith@abccollege.edu",
            "is_primary": true,
            "preferred_contact_method": "EMAIL",
            "notes": null,
            "is_active": true
        }
    ],
    "version": 1,
    "audit_info": {
        "created_by": "UUID v4",
        "created_at": "2026-07-20T12:00:00Z",
        "updated_by": "UUID v4",
        "updated_at": "2026-07-20T12:00:00Z"
    }
}
```

### 1.6 OrganizationListResponse

```json
{
    "items": [
        // OrganizationSummaryResponse objects
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_records": 150,
        "total_pages": 8
    }
}
```
