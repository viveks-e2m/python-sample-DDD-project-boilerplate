import uuid
import secrets
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlmodel import select
from fastapi import HTTPException, status
from apps.user.domain.models.models import User
from apps.user.domain.models.auth_models import TwoFactorAuth, UserSession, OAuthAccount, TwoFactorType, OAuthProvider
from database import SessionDep


class AuthDomainService:
    """
    Domain service for authentication-related operations
    """

    def __init__(self, session: SessionDep):
        self.session = session

    async def setup_two_factor_auth(self, user_id: uuid.UUID, type: TwoFactorType) -> dict:
        """
        Setup two-factor authentication for a user

        Args:
            user_id: The ID of the user
            type: The type of 2FA to setup (TOTP, SMS, EMAIL)

        Returns:
            Dictionary with setup information
        """
        # Check if user exists
        user = self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if 2FA already exists for this user and type
        statement = select(TwoFactorAuth).where(
            TwoFactorAuth.user_id == user_id,
            TwoFactorAuth.type == type
        )
        result = self.session.exec(statement)
        existing_2fa = result.first()

        # If exists and enabled, return error
        if existing_2fa and existing_2fa.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{type.value} 2FA is already enabled for this user"
            )

        response_data: dict = {}

        # Note: For TOTP functionality, you would need to install the pyotp library
        # pip install pyotp
        # For now, we'll provide a simplified implementation without actual TOTP

        if type == TwoFactorType.TOTP:
            # Generate secret for TOTP (simplified)
            secret = secrets.token_urlsafe(32)
            
            # Create or update 2FA record
            if existing_2fa:
                existing_2fa.secret = secret
                existing_2fa.is_enabled = False  # Not enabled until verified
                self.session.add(existing_2fa)
            else:
                new_2fa = TwoFactorAuth(
                    user_id=user_id,
                    type=type,
                    secret=secret,
                    is_enabled=False
                )
                self.session.add(new_2fa)
            
            # In a real implementation with pyotp:
            # totp = pyotp.totp.TOTP(secret)
            # qr_code_url = totp.provisioning_uri(
            #     name=user.email,
            #     issuer_name="YourAppName"
            # )
            
            qr_code_url = f"https://example.com/qr?secret={secret}"  # Mock QR code URL
            response_data["qr_code_url"] = qr_code_url
            response_data["secret"] = secret
            
        elif type == TwoFactorType.SMS:
            # For SMS, we would need to collect phone number
            # This is a simplified implementation
            if existing_2fa:
                existing_2fa.phone_number = None  # Reset until verified
                existing_2fa.is_enabled = False
                self.session.add(existing_2fa)
            else:
                new_2fa = TwoFactorAuth(
                    user_id=user_id,
                    type=type,
                    phone_number=None,  # Will be set during verification
                    is_enabled=False
                )
                self.session.add(new_2fa)
                
        elif type == TwoFactorType.EMAIL:
            # For email 2FA, we'll use the user's email
            if existing_2fa:
                existing_2fa.is_enabled = False  # Not enabled until verified
                self.session.add(existing_2fa)
            else:
                new_2fa = TwoFactorAuth(
                    user_id=user_id,
                    type=type,
                    is_enabled=False
                )
                self.session.add(new_2fa)

        self.session.commit()
        
        # Generate recovery codes
        recovery_codes: List[str] = [secrets.token_urlsafe(16) for _ in range(10)]
        response_data["recovery_codes"] = recovery_codes
        
        return response_data

    async def verify_two_factor_auth(self, user_id: uuid.UUID, code: str, type: TwoFactorType) -> bool:
        """
        Verify 2FA code during setup or login

        Args:
            user_id: The ID of the user
            code: The 2FA code to verify
            type: The type of 2FA to verify

        Returns:
            Boolean indicating if verification was successful
        """
        # Get 2FA record
        statement = select(TwoFactorAuth).where(
            TwoFactorAuth.user_id == user_id,
            TwoFactorAuth.type == type
        )
        result = self.session.exec(statement)
        two_factor_auth = result.first()

        if not two_factor_auth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{type.value} 2FA not set up for this user"
            )

        is_valid = False

        # Simplified verification logic
        # In a real implementation, you would verify against actual TOTP/SMS/email codes
        if len(code) == 6 and code.isdigit():
            is_valid = True

        if is_valid:
            # Enable 2FA if it was verification during setup
            two_factor_auth.is_enabled = True
            self.session.add(two_factor_auth)
            self.session.commit()

        return is_valid

    async def create_user_session(self, user_id: uuid.UUID, session_token: str, 
                                  ip_address: Optional[str] = None, 
                                  user_agent: Optional[str] = None,
                                  expires_in_hours: int = 24) -> UserSession:
        """
        Create a new user session

        Args:
            user_id: The ID of the user
            session_token: The session token
            ip_address: The IP address of the client
            user_agent: The user agent string
            expires_in_hours: Hours until session expires

        Returns:
            The created UserSession object
        """
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        
        return session

    async def get_active_sessions(self, user_id: uuid.UUID) -> List[UserSession]:
        """
        Get all active sessions for a user

        Args:
            user_id: The ID of the user

        Returns:
            List of active UserSession objects
        """
        statement = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.now(timezone.utc)
        )
        result = self.session.exec(statement)
        return list(result.all())

    async def revoke_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Revoke a specific session

        Args:
            session_id: The ID of the session to revoke
            user_id: The ID of the user (for verification)

        Returns:
            Boolean indicating if session was revoked
        """
        statement = select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == user_id
        )
        result = self.session.exec(statement)
        session = result.first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        session.is_active = False
        self.session.add(session)
        self.session.commit()
        
        return True

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> int:
        """
        Revoke all sessions for a user

        Args:
            user_id: The ID of the user

        Returns:
            Number of sessions revoked
        """
        statement = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        )
        result = self.session.exec(statement)
        sessions = result.all()

        count = 0
        for session in sessions:
            session.is_active = False
            self.session.add(session)
            count += 1

        if count > 0:
            self.session.commit()
            
        return count

    async def impersonate_user(self, admin_user_id: uuid.UUID, target_user_id: uuid.UUID) -> dict:
        """
        Allow admin to impersonate another user

        Args:
            admin_user_id: The ID of the admin user
            target_user_id: The ID of the user to impersonate

        Returns:
            Dictionary with impersonation information
        """
        # Check if admin user exists and is superuser
        admin_user = self.session.get(User, admin_user_id)
        if not admin_user or not admin_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can impersonate other users"
            )

        # Check if target user exists
        target_user = self.session.get(User, target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )

        # Create impersonation token/session
        # In a real implementation, you would create a special token
        # that allows switching back to the admin user
        impersonation_token = secrets.token_urlsafe(32)
        
        return {
            "impersonation_token": impersonation_token,
            "target_user_id": target_user_id,
            "message": "Impersonation started successfully"
        }

    async def handle_oauth_login(self, provider: OAuthProvider, code: str, redirect_uri: str) -> dict:
        """
        Handle OAuth login with external providers

        Args:
            provider: The OAuth provider
            code: The OAuth authorization code
            redirect_uri: The redirect URI

        Returns:
            Dictionary with login information
        """
        # This is a simplified implementation
        # In a real application, you would:
        # 1. Exchange the code for an access token with the provider
        # 2. Get user information from the provider
        # 3. Create or update user account
        # 4. Create session for the user
        
        # For demonstration, we'll return a mock response
        return {
            "provider": provider.value,
            "access_token": secrets.token_urlsafe(32),
            "user_id": str(uuid.uuid4()),
            "message": f"OAuth login with {provider.value} successful"
        }