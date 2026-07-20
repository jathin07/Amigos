# 09 Assignment DTOs
## Workload Assignments Ownership Change Requests & Auditing Logs

---

## 1. Request DTOs

### 1.1 `AssignLeadRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `new_team_member_id` | string | Yes | No | Format: UUID | None | `uuid-tm-2` |
| `reason` | string | No | Yes | Max length: 255 | None | `Workload allocation` |

```json
{
  "new_team_member_id": "uuid-tm-2",
  "reason": "Workload allocation"
}
```

### 1.2 `AssignOperationsOwnerRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `new_operations_owner_id` | string | Yes | No | Format: UUID | None | `uuid-tm-3` |
| `reason` | string | No | Yes | Max length: 255 | None | `Operational shift assign` |

```json
{
  "new_operations_owner_id": "uuid-tm-3",
  "reason": "Operational shift assign"
}
```

---

## 2. Response DTOs

### 2.1 `AssignmentHistoryResponse`
```json
{
  "id": "uuid-assign-1",
  "entity_type": "Lead",
  "entity_id": "uuid-lead-1",
  "previous_owner_id": null,
  "new_owner_id": "uuid-tm-2",
  "assigned_by": "uuid-tm-1",
  "reason": "Workload allocation",
  "assigned_at": "2026-07-16T14:48:59Z"
}
```
