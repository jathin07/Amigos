# 10 Notification DTOs
## Notification Messages and Delivery Preferences Schemas

---

## 1. Request DTOs

### 1.1 `NotificationPreferenceRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `email_enabled` | boolean | Yes | No | None | true | true |
| `whatsapp_enabled`| boolean | Yes | No | None | false | false |
| `push_enabled` | boolean | Yes | No | None | true | true |

```json
{
  "email_enabled": true,
  "whatsapp_enabled": false,
  "push_enabled": true
}
```

---

## 2. Response DTOs

### 2.1 `NotificationResponse`
```json
{
  "id": "uuid-notif-1",
  "message": "Lead converted to Booking",
  "is_read": false,
  "created_at": "2026-07-16T14:48:59Z"
}
```
