from fastapi import Request,HTTPException,status
from database import SessionDep
from apps.user.application.service import UserApplicationService
from apps.user.domain.models import User
from apps.user.utils import get_current_user_from_cookie

# Dependencies
def get_user_service(session: SessionDep) -> UserApplicationService:
    return UserApplicationService(session)

async def get_authenticated_user(
    request: Request, session: SessionDep
) -> User:
    user: User | None = await get_current_user_from_cookie(request, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user