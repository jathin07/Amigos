from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class PermissionDTO(BaseModel):
    code: str
    name: str
    description: str

class UserSummary(BaseModel):
    id: str
    employee_code: str
    name: str
    email: str
    phone: str
    designation: str
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    last_login_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class SessionDTO(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"

class LoginResponse(BaseModel):
    session: SessionDTO
    user: UserSummary

class CurrentUserResponse(BaseModel):
    user: UserSummary
    permissions: List[PermissionDTO]

class VerifyTokenResponse(BaseModel):
    valid: bool
    expires_at: str
    user_id: str
    role: str
