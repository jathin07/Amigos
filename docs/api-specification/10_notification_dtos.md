# 10 Notification DTOs
## In-App Notification Messages, Delivery Preferences, and Read Management Schemas

> **Module Type**: Infrastructure (Event-Driven, Reactive)
> **Design Note**: The Notification module is entirely reactive. It never initiates business logic. It only consumes Domain Events from other modules and delivers them to team members.
> **Fault Tolerance**: Notification delivery failures (SMTP down, push token expired) must never rollback parent business transactions.

---

## Notification Delivery Pipeline

```
Business Event Fired
     ↓
Workflow Engine (routes event)
     ↓
Notification Module (subscribes)
     ↓
Template Resolution (matches event → template)
     ↓
Channel Selection (In-App, Email, WhatsApp, SMS)
     ↓
Delivery Attempt
     ↓
Delivery History Log
```

---

## Notification Types

| Type Code | Trigger Event | Example Message |
| :--- | :--- | :--- |
| `LEAD_ASSIGNED` | `LeadAssigned` | New lead assigned to you: Raju Naik (Coorg Trip) |
| `PROPOSAL_APPROVED` | `ProposalFinalized` | Proposal #P2026-042 approved by customer |
| `ADVANCE_RECEIVED` | `AdvanceReceived` | ₹25,000 advance received for Booking AMT-2026-00001 |
| `BOOKING_CONFIRMED` | `BookingConfirmed` | Booking AMT-2026-00001 confirmed. Operations planning starts now. |
| `TASK_ASSIGNED` | Task created | You have been assigned: Confirm hotel reservation (Due: Aug 5) |
| `CHECKLIST_COMPLETE` | `ChecklistCompleted` | All checklist items completed for Booking AMT-2026-00001 |
| `TRIP_COMPLETED` | `TripCompleted` | Trip AMT-2026-00001 marked completed. Finance closure pending. |
| `PAYMENT_OVERDUE` | Scheduled cron | Payment installment overdue: ₹25,000 from Raj Enterprises |
| `VENDOR_PAYMENT_DUE` | Scheduled cron | Vendor payment pending: Hotel Coorg View – ₹4,750 |
| `FINANCE_CLOSED` | `FinanceClosed` | Finance closed for Booking AMT-2026-00001. |
| `SYSTEM_ALERT` | Internal system | System maintenance scheduled for tonight 11 PM. |

---

## Delivery Channels

| Channel | Enabled By Default | Notes |
| :--- | :--- | :--- |
| `IN_APP` | ✅ | Always delivered; stored in `notifications` table |
| `EMAIL` | ✅ | Sent via SMTP/SES; configurable per preference |
| `WHATSAPP` | ❌ | Optional; requires WhatsApp Business API integration |
| `SMS` | ❌ | Optional; requires SMS gateway integration |

---

## 1. Request DTOs

---

### 1.1 `UpdateNotificationPreferenceRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `email_enabled` | boolean | Yes | No | — | `true` | `true` |
| `whatsapp_enabled` | boolean | Yes | No | — | `false` | `false` |
| `sms_enabled` | boolean | Yes | No | — | `false` | `false` |
| `push_enabled` | boolean | Yes | No | — | `true` | `true` |
| `lead_notifications` | boolean | No | No | — | `true` | `true` |
| `task_notifications` | boolean | No | No | — | `true` | `true` |
| `payment_notifications` | boolean | No | No | — | `true` | `true` |
| `system_notifications` | boolean | No | No | — | `true` | `true` |

```json
{
  "email_enabled": true,
  "whatsapp_enabled": false,
  "sms_enabled": false,
  "push_enabled": true,
  "lead_notifications": true,
  "task_notifications": true,
  "payment_notifications": true,
  "system_notifications": true
}
```

---

### 1.2 `MarkReadRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `notification_id` | string | Yes | No | Format: UUID | — | `uuid-notif-1` |

```json
{
  "notification_id": "uuid-notif-1"
}
```

---

### 1.3 `BulkDismissRequest`

| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `notification_ids` | array[string] | Yes | No | Min: 1, Max: 100 UUIDs | — | `["uuid-notif-1", "uuid-notif-2"]` |

```json
{
  "notification_ids": ["uuid-notif-1", "uuid-notif-2", "uuid-notif-3"]
}
```

---

### 1.4 `MarkAllReadRequest`

No body required. Marks all unread notifications for the current user as read.

```json
{}
```

---

## 2. Response DTOs

---

### 2.1 `NotificationDetailResponse`

| Field | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | No | Notification UUID |
| `team_member_id` | string | No | Recipient team member UUID |
| `entity_type` | string | Yes | Related entity type (e.g., `Booking`, `Lead`, `Task`) |
| `entity_id` | string | Yes | Related entity UUID |
| `title` | string | No | Short notification headline |
| `message` | string | No | Full notification message body |
| `action_url` | string | Yes | Deeplink URL for front-end navigation |
| `notification_type` | string | No | Type code (e.g., `BOOKING_CONFIRMED`) |
| `priority` | object | No | `{ id, code, name }` (e.g., HIGH, MEDIUM, LOW) |
| `is_read` | boolean | No | Whether notification has been read |
| `sent_at` | string | Yes | ISO DateTime when delivered |
| `read_at` | string | Yes | ISO DateTime when opened by user |
| `created_at` | string | No | ISO DateTime when record created |

```json
{
  "id": "uuid-notif-1",
  "team_member_id": "uuid-tm-2",
  "entity_type": "Booking",
  "entity_id": "uuid-booking-1",
  "title": "Booking Confirmed",
  "message": "Booking AMT-2026-00001 for Raj Enterprises has been confirmed. Operations planning can now begin.",
  "action_url": "/bookings/uuid-booking-1",
  "notification_type": "BOOKING_CONFIRMED",
  "priority": { "id": "uuid-prio-high", "code": "HIGH", "name": "High" },
  "is_read": false,
  "sent_at": "2026-07-20T12:00:00Z",
  "read_at": null,
  "created_at": "2026-07-20T12:00:00Z"
}
```

---

### 2.2 `NotificationListResponse` (Paginated)

```json
{
  "items": [
    {
      "id": "uuid-notif-1",
      "title": "Booking Confirmed",
      "message": "Booking AMT-2026-00001 for Raj Enterprises has been confirmed.",
      "notification_type": "BOOKING_CONFIRMED",
      "entity_type": "Booking",
      "entity_id": "uuid-booking-1",
      "action_url": "/bookings/uuid-booking-1",
      "priority": { "code": "HIGH", "name": "High" },
      "is_read": false,
      "sent_at": "2026-07-20T12:00:00Z"
    },
    {
      "id": "uuid-notif-2",
      "title": "Task Assigned",
      "message": "You have been assigned: Confirm hotel reservation (Due: Aug 5).",
      "notification_type": "TASK_ASSIGNED",
      "entity_type": "Task",
      "entity_id": "uuid-task-1",
      "action_url": "/tasks/uuid-task-1",
      "priority": { "code": "MEDIUM", "name": "Medium" },
      "is_read": true,
      "sent_at": "2026-07-21T08:00:00Z"
    }
  ],
  "total": 2,
  "unread_count": 1,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

### 2.3 `UnreadCountResponse`

```json
{
  "unread_count": 7,
  "high_priority_unread": 2
}
```

---

### 2.4 `NotificationPreferenceResponse`

```json
{
  "team_member_id": "uuid-tm-2",
  "email_enabled": true,
  "whatsapp_enabled": false,
  "sms_enabled": false,
  "push_enabled": true,
  "lead_notifications": true,
  "task_notifications": true,
  "payment_notifications": true,
  "system_notifications": true,
  "updated_at": "2026-07-15T10:00:00Z"
}
```

---

### 2.5 `BulkDismissResultResponse`

```json
{
  "dismissed_count": 3,
  "failed_ids": [],
  "message": "3 notifications dismissed successfully"
}
```

---

## 3. Error Catalogue

| Error Code | HTTP Status | Trigger | Message |
| :--- | :--- | :--- | :--- |
| `NOTIFICATION_NOT_FOUND` | 404 | UUID does not exist for current user | Notification not found |
| `ALREADY_READ` | 409 | Marking already-read notification as read | Notification is already marked as read |
| `INVALID_BULK_DISMISS` | 422 | Bulk dismiss list is empty or exceeds limit | Notification IDs list must contain 1 to 100 items |

---

## 4. Subscribed Domain Events

| Event | Source | In-App Message Generated |
| :--- | :--- | :--- |
| `LeadAssigned` | CRM | New lead assigned: {customer_name} |
| `ProposalFinalized` | Proposal | Proposal approved by {customer_name} |
| `AdvanceReceived` | Finance | ₹{amount} advance received for Booking {booking_number} |
| `BookingConfirmed` | Booking | Booking {booking_number} confirmed. Operations can begin. |
| `TripCompleted` | Operations | Trip {booking_number} completed. Finance closure pending. |
| `FinanceClosed` | Finance | Finance closed for Booking {booking_number} |
| `TaskAssigned` | Operations | Task assigned: {task_title} (Due: {due_date}) |
| `ChecklistCompleted` | Operations | All checklist items completed for {booking_number} |
