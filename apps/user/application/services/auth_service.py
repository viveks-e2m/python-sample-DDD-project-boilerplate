import uuid
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from apps.user.domain.services.auth_service import AuthDomainService
from apps.user.domain.models.auth_models import TwoFactorType, OAuthProvider, UserSession
from apps.user.application.schema.auth_schema import (
    TwoFactorSetupRequest, 
    TwoFactorVerifyRequest, 
    OAuthLoginRequest,
    UserSessionModel
)
from database import SessionDep


class AuthApplicationService:
    """
    Application service for authentication-related operations
    """

    def __init__(self, session: SessionDep):
        self.session = session
        self.domain_service = AuthDomainService(session)

    async def setup_two_factor_auth(self, user_id: uuid.UUID, setup_request: TwoFactorSetupRequest):
        """
        Application service for setting up two-factor authentication

        Args:
            user_id: The ID of the user
            setup_request: The 2FA setup request data

        Returns:
            Dictionary with setup information

        Raises:
            HTTPException: 400 - Invalid request
            HTTPException: 404 - User not found
            HTTPException: 500 - Internal server error
        """
        try:
            return await self.domain_service.setup_two_factor_auth(
                user_id, setup_request.type
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to setup 2FA: {str(e)}"
            )

    async def verify_two_factor_auth(self, user_id: uuid.UUID, verify_request: TwoFactorVerifyRequest) -> bool:
        """
        Application service for verifying two-factor authentication

        Args:
            user_id: The ID of the user
            verify_request: The 2FA verification request data

        Returns:
            Boolean indicating if verification was successful

        Raises:
            HTTPException: 400 - Invalid request
            HTTPException: 404 - 2FA not set up
            HTTPException: 500 - Internal server error
        """
        try:
            return await self.domain_service.verify_two_factor_auth(
                user_id, verify_request.code, verify_request.type
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify 2FA: {str(e)}"
            )

    async def get_user_sessions(self, user_id: uuid.UUID) -> List[UserSessionModel]:
        """
        Application service for getting user sessions

        Args:
            user_id: The ID of the user

        Returns:
            List of user sessions

        Raises:
            HTTPException: 500 - Internal server error
        """
        try:
            sessions = await self.domain_service.get_active_sessions(user_id)
            return [
                UserSessionModel(
                    id=session.id,
                    ip_address=session.ip_address,
                    user_agent=session.user_agent,
                    created_at=session.created_at,
                    expires_at=session.expires_at,
                    is_active=session.is_active
                )
                for session in sessions
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve sessions: {str(e)}"
            )

    async def revoke_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Application service for revoking a user session

        Args:
            session_id: The ID of the session to revoke
            user_id: The ID of the user

        Returns:
            Boolean indicating if session was revoked

        Raises:
            HTTPException: 404 - Session not found
            HTTPException: 500 - Internal server error
        """
        try:
            return await self.domain_service.revoke_session(session_id, user_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to revoke session: {str(e)}"
            )

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> int:
        """
        Application service for revoking all user sessions

        Args:
            user_id: The ID of the user

        Returns:
            Number of sessions revoked

        Raises:
            HTTPException: 500 - Internal server error
        """
        try:
            return await self.domain_service.revoke_all_sessions(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to revoke all sessions: {str(e)}"
            )

    async def impersonate_user(self, admin_user_id: uuid.UUID, target_user_id: uuid.UUID):
        """
        Application service for impersonating a user

        Args:
            admin_user_id: The ID of the admin user
            target_user_id: The ID of the user to impersonate

        Returns:
            Dictionary with impersonation information

        Raises:
            HTTPException: 403 - Not authorized
            HTTPException: 404 - User not found
            HTTPException: 500 - Internal server error
        """
        try:
            return await self.domain_service.impersonate_user(admin_user_id, target_user_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to impersonate user: {str(e)}"
            )

    async def handle_oauth_login(self, provider: str, oauth_request: OAuthLoginRequest):
        """
        Application service for handling OAuth login

        Args:
            provider: The OAuth provider
            oauth_request: The OAuth login request data

        Returns:
            Dictionary with login information

        Raises:
            HTTPException: 400 - Invalid provider
            HTTPException: 500 - Internal server error
        """
        try:
            # Convert string to OAuthProvider enum
            try:
                provider_enum = OAuthProvider(provider.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid OAuth provider: {provider}"
                )
            
            return await self.domain_service.handle_oauth_login(
                provider_enum, oauth_request.code, oauth_request.redirect_uri
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to handle OAuth login: {str(e)}"
            )