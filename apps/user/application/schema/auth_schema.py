import uuid
from typing import Optional, List
from sqlmodel import SQLModel
from pydantic import BaseModel
from datetime import datetime
from apps.user.domain.models.auth_models import TwoFactorType, OAuthProvider


# 2FA Setup Request/Response Models
class TwoFactorSetupRequest(BaseModel):
    type: TwoFactorType


class TwoFactorSetupResponse(BaseModel):
    qr_code_url: Optional[str] = None
    secret: Optional[str] = None
    recovery_codes: Optional[List[str]] = None


# 2FA Verify Request Model
class TwoFactorVerifyRequest(BaseModel):
    code: str
    type: TwoFactorType


# OAuth Request Model
class OAuthLoginRequest(BaseModel):
    code: str  # OAuth authorization code
    redirect_uri: str


# Session Models
class UserSessionModel(SQLModel):
    id: uuid.UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_active: bool


class SessionListResponse(BaseModel):
    sessions: List[UserSessionModel]


# Impersonation Request Model
class ImpersonateRequest(BaseModel):
    user_id: uuid.UUID


# Generic Response for Auth Operations
class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
