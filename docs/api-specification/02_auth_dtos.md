# 02 Auth DTOs
## Authentication Request & Response Data Transfer Objects

This document defines the schema definitions, validation rules, field requirements, and JSON types for every authentication and authorization DTO across the Amigos Tourism application.

---

## 1. Responsibilities & Boundary Scope
The Authentication module is responsible for:
- User authentication & Session management.
- JWT generation, validation, and token refresh.
- Password resets workflows, password changes, and refresh token blacklisting.
- Role and permission retrieval and authorization middleware integration.

*Note: This module does not manage Team Member profile edits or role re-assignments. Those belong to the Master module.*

---

## 2. Authentication Flow & State Machine

### 2.1 State Transitions
```text
Unauthenticated ──(Login)──> Authenticated ──(Refresh)──> Authenticated
       │                                                      │
       └─────────────────────────(Logout)─────────────────────┘
```

### 2.2 Execution Path
```text
Login Request ──> Validate Credentials (DB Check) ──> Generate JWT ──> Return Session + UserSummary
```

---

## 3. Authentication Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/auth/login` | Login user, establish session |
| **POST** | `/auth/logout` | Terminate session, blacklist refresh token |
| **POST** | `/auth/refresh`| Generate new short-lived access token |
| **POST** | `/auth/forgot-password` | Generate reset link (securely masked) |
| **POST** | `/auth/reset-password` | Complete password reset |
| **POST** | `/auth/change-password` | Update password for active user |
| **GET** | `/auth/me` | Fetch active user profile and permissions |
| **GET** | `/auth/verify` | Validate access token integrity |

---

## 4. Request DTOs

### 4.1 `LoginRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `email` | string | Yes | No | Format: Email | None | `user@example.com` |
| `password` | string | Yes | No | Min length: 8 | None | `Password123` |
| `remember_me` | boolean | No | No | None | false | true |

```json
{
  "email": "user@example.com",
  "password": "Password123",
  "remember_me": true
}
```

### 4.2 `ForgotPasswordRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `email` | string | Yes | No | Format: Email | None | `user@example.com` |

```json
{
  "email": "user@example.com"
}
```

### 4.3 `ResetPasswordRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `token` | string | Yes | No | Format: UUID | None | `uuid-reset-token-1` |
| `new_password` | string | Yes | No | Min length: 8 | None | `NewSecurePassword123` |
| `confirm_password`| string | Yes | No | Must match `new_password`| None | `NewSecurePassword123` |

```json
{
  "token": "uuid-reset-token-1",
  "new_password": "NewSecurePassword123",
  "confirm_password": "NewSecurePassword123"
}
```

### 4.4 `ChangePasswordRequest`
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `current_password`| string | Yes | No | Min length: 8 | None | `OldPassword123` |
| `new_password` | string | Yes | No | Min length: 8 | None | `NewSecurePassword123` |
| `confirm_password`| string | Yes | No | Must match `new_password`| None | `NewSecurePassword123` |

```json
{
  "current_password": "OldPassword123",
  "new_password": "NewSecurePassword123",
  "confirm_password": "NewSecurePassword123"
}
```

### 4.5 `RefreshTokenRequest`
*Note: If HttpOnly cookie transport is activated, the request body is empty `{}` and the token is read from cookies.*
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `refresh_token` | string | No | Yes | None | None | `refresh_token_jwt` |

```json
{
  "refresh_token": "refresh_token_jwt"
}
```

### 4.6 `LogoutRequest`
*Note: If HttpOnly cookie transport is activated, the request body is empty `{}`.*
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `refresh_token` | string | No | Yes | None | None | `refresh_token_jwt` |

```json
{
  "refresh_token": "refresh_token_jwt"
}
```

---

## 5. Response DTOs

### 5.1 `LoginResponse`
```json
{
  "session": {
    "access_token": "access_token_jwt",
    "refresh_token": "refresh_token_jwt",
    "expires_in": 3600,
    "token_type": "Bearer"
  },
  "user": {
    "id": "uuid-tm-1",
    "employee_code": "TM001",
    "name": "Arjun",
    "email": "tm@example.com",
    "phone": "9876543210",
    "designation": "Operations Executive",
    "role": "Team Member",
    "avatar_url": "https://cloudinary.com/avatar.jpg",
    "is_active": true,
    "last_login_at": "2026-07-16T14:48:59Z"
  }
}
```

### 5.2 `LogoutResponse`
```json
{
  "success": true,
  "message": "Logged out successfully."
}
```

### 5.3 `ForgotPasswordResponse`
```json
{
  "success": true,
  "message": "Password reset link has been sent if the account exists."
}
```

### 5.4 `ResetPasswordResponse`
```json
{
  "success": true,
  "message": "Password reset successfully."
}
```

### 5.5 `ChangePasswordResponse`
```json
{
  "success": true,
  "message": "Password updated successfully."
}
```

### 5.6 `RefreshTokenResponse`
```json
{
  "access_token": "new_access_token_jwt",
  "expires_in": 3600
}
```

### 5.7 `CurrentUserResponse`
```json
{
  "user": {
    "id": "uuid-tm-1",
    "employee_code": "TM001",
    "name": "Arjun",
    "email": "tm@example.com",
    "phone": "9876543210",
    "designation": "Operations Executive",
    "role": "Team Member",
    "avatar_url": "https://cloudinary.com/avatar.jpg",
    "is_active": true,
    "last_login_at": "2026-07-16T14:48:59Z"
  },
  "permissions": [
    {
      "code": "booking.write",
      "name": "Booking Write",
      "description": "Create and modify bookings"
    }
  ]
}
```

### 5.8 `VerifyTokenResponse`
```json
{
  "valid": true,
  "expires_at": "2026-07-16T15:48:59Z",
  "user_id": "uuid-tm-1",
  "role": "Team Member"
}
```

---

## 6. Shared UserSummary DTO
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | string | Yes | No | Format: UUID | None | `uuid-tm-1` |
| `employee_code` | string | Yes | No | Max length: 50 | None | `TM001` |
| `name` | string | Yes | No | Max length: 150 | None | `Arjun` |
| `email` | string | Yes | No | Format: Email | None | `tm@example.com` |
| `phone` | string | Yes | No | Format: Phone | None | `9876543210` |
| `designation` | string | Yes | No | Max length: 100 | None | `Operations Executive` |
| `role` | string | Yes | No | Enum: RoleType | None | `Team Member` |
| `avatar_url` | string | No | Yes | Format: URL | None | `https://cloudinary.com/avatar.jpg` |
| `is_active` | boolean | Yes | No | None | true | true |
| `last_login_at` | string | No | Yes | Format: ISO8601 | None | `2026-07-16T14:48:59Z` |

---

## 7. Permission DTO
| Field | Type | Required | Nullable | Validation | Default | Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `code` | string | Yes | No | Max length: 100 | None | `booking.write` |
| `name` | string | Yes | No | Max length: 100 | None | `Booking Write` |
| `description` | string | Yes | No | Max length: 255 | None | `Create and modify bookings` |

---

## 8. JWT Token Claims Specification
Access tokens contain the following claims:
```json
{
  "sub": "team_member_uuid",
  "role": "Team Member",
  "permissions": ["booking.write"],
  "iat": 1784210400,
  "exp": 1784214000
}
```

---

## 9. Security & Hardening Rules
- **Password Storage**: Passwords must be hashed using `bcrypt` (rounds: 12).
- **Hashed Sessions**: Refresh tokens are SHA-256 hashed before database checks.
- **Expiry Guidelines**: Password reset tokens expire after exactly `15 minutes`.
- **Brute Force Lock**: Lock account for `30 minutes` after `5` consecutive failed login attempts.
- **Transport**: Enable refresh token rotation and HttpOnly secure cookies.

---

## 10. Auth Error Codes Catalog

| Code | HTTP Status | Meaning |
| :--- | :--- | :--- |
| `ERR_INVALID_CREDENTIALS` | 401 Unauthorized | Incorrect email or password credentials. |
| `ERR_ACCOUNT_DISABLED` | 403 Forbidden | Team member account is marked inactive. |
| `ERR_ACCOUNT_LOCKED` | 423 Locked | Too many failed attempts, try again later. |
| `ERR_INVALID_TOKEN` | 401 Unauthorized | JWT signature verify check failed. |
| `ERR_TOKEN_EXPIRED` | 401 Unauthorized | Access token expired. |
| `ERR_REFRESH_TOKEN_EXPIRED`| 401 Unauthorized | Refresh token has expired, re-login required. |
| `ERR_PASSWORD_MISMATCH` | 400 Bad Request | Password input fields do not match. |
| `ERR_INVALID_RESET_TOKEN` | 400 Bad Request | Password reset token is malformed or invalid. |
| `ERR_RESET_TOKEN_EXPIRED` | 400 Bad Request | Reset link lifetime exceeded. |
