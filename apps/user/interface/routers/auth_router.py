import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from apps.user.application.services.auth_service import AuthApplicationService
from apps.user.application.schema.auth_schema import (
    TwoFactorSetupRequest,
    TwoFactorVerifyRequest,
    OAuthLoginRequest,
    SessionListResponse,
    AuthResponse
)
from apps.user.domain.models.models import User
from apps.user.interface.dependency import get_authenticated_user
from database import SessionDep
from typing import List

# Dependencies
def get_auth_service(session: SessionDep) -> AuthApplicationService:
    return AuthApplicationService(session)

router = APIRouter()

@router.post("/2fa/setup", response_model=AuthResponse, tags=["Authentication"])
async def setup_two_factor_auth(
    setup_request: TwoFactorSetupRequest,
    current_user: User = Depends(get_authenticated_user),
    service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Setup two-factor authentication (TOTP, SMS, email OTP).

    Args:
        setup_request: The 2FA setup request data
        current_user: The authenticated user
        service: Auth application service

    Returns:
        AuthResponse with setup information
    """
    try:
        result = await service.setup_two_factor_auth(current_user.id, setup_request)
        return AuthResponse(
            success=True,
            message=f"{setup_request.type.value} 2FA setup initiated successfully",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup 2FA: {str(e)}"
        )

@router.post("/2fa/verify", response_model=AuthResponse, tags=["Authentication"])
async def verify_two_factor_auth(
    verify_request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_authenticated_user),
    service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Verify 2FA code during login.

    Args:
        verify_request: The 2FA verification request data
        current_user: The authenticated user
        service: Auth application service

    Returns:
        AuthResponse indicating verification success
    """
    try:
        is_valid = await service.verify_two_factor_auth(
            current_user.id, verify_request
        )
        
        if is_valid:
            return AuthResponse(
                success=True,
                message="2FA verification successful",
                data={"verified": True}
            )
        else:
            return AuthResponse(
                success=False,
                message="Invalid 2FA code",
                data={"verified": False}
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify 2FA: {str(e)}"
        )

@router.post("/social-login/{provider}", response_model=AuthResponse, tags=["Authentication"])
async def social_login(
    provider: str,
    oauth_request: OAuthLoginRequest,
    service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Login using OAuth2 (Google, GitHub, Facebook).

    Args:
        provider: The OAuth provider (google, github, facebook)
        oauth_request: The OAuth login request data
        service: Auth application service

    Returns:
        AuthResponse with login information
    """
    try:
        result = await service.handle_oauth_login(provider, oauth_request)
        return AuthResponse(
            success=True,
            message=f"Successfully logged in with {provider}",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login with {provider}: {str(e)}"
        )

@router.get("/sessions", response_model=AuthResponse, tags=["Authentication"])
async def list_active_sessions(
    current_user: User = Depends(get_authenticated_user),
    service: AuthApplicationService = Depends(get_auth_service)
):
    """
    List active sessions/devices.

    Args:
        current_user: The authenticated user
        service: Auth application service

    Returns:
        AuthResponse with list of active sessions
    """
    try:
        sessions = await service.get_user_sessions(current_user.id)
        return AuthResponse(
            success=True,
            message="Active sessions retrieved successfully",
            data={"sessions": [session.model_dump() for session in sessions]}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )

@router.delete("/sessions/{session_id}", response_model=AuthResponse, tags=["Authentication"])
async def revoke_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_authenticated_user),
    service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Revoke a session/device.

    Args:
        session_id: The ID of the session to revoke
        current_user: The authenticated user
        service: Auth application service

    Returns:
        AuthResponse indicating revocation success
    """
    try:
        result = await service.revoke_session(session_id, current_user.id)
        if result:
            return AuthResponse(
                success=True,
                message="Session revoked successfully",
                data={"revoked": True}
            )
        else:
            return AuthResponse(
                success=False,
                message="Failed to revoke session",
                data={"revoked": False}
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke session: {str(e)}"
        )

@router.post("/impersonate/{user_id}", response_model=AuthResponse, tags=["Authentication"])
async def impersonate_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_authenticated_user),
    service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Impersonate a user (useful for support/admin tools).

    Args:
        user_id: The ID of the user to impersonate
        current_user: The authenticated user (must be admin)
        service: Auth application service

    Returns:
        AuthResponse with impersonation information
    """
    try:
        result = await service.impersonate_user(current_user.id, user_id)
        return AuthResponse(
            success=True,
            message="User impersonation started successfully",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to impersonate user: {str(e)}"
        )

@router.post("/logout-all", response_model=AuthResponse, tags=["Authentication"])
async def logout_all_sessions(
    current_user: User = Depends(get_authenticated_user),
    service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Invalidate all user sessions.

    Args:
        current_user: The authenticated user
        service: Auth application service

    Returns:
        AuthResponse indicating logout success
    """
    try:
        count = await service.revoke_all_sessions(current_user.id)
        return AuthResponse(
            success=True,
            message=f"Logged out from {count} sessions successfully",
            data={"sessions_revoked": count}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout from all sessions: {str(e)}"
        )