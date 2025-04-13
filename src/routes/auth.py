import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    Request,
    BackgroundTasks,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.auth import AuthService, oauth2_scheme
from src.schemas.token import TokenResponse, RefreshTokenRequest
from src.schemas.user import UserResponse, UserCreate
from src.services.email import send_email
from src.schemas.email import RequestEmail
from src.schemas.user import ResetPassword


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("uvicorn.error")


def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register_user(user_data)
    background_tasks.add_task(
        send_email, user_data.email, user_data.username, str(request.base_url)
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate(form_data.username, form_data.password)
    access_token = auth_service.create_access_token(user.username)
    refresh_token = await auth_service.create_refresh_token(
        user.id,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    return TokenResponse(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_token: RefreshTokenRequest,
    request: Request = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.validate_refresh_token(refresh_token.refresh_token)

    new_access_token = auth_service.create_access_token(user.username)
    new_refresh_token = await auth_service.create_refresh_token(
        user.id,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    await auth_service.revoke_refresh_token(refresh_token.refresh_token)

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        refresh_token=new_refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: RefreshTokenRequest,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.revoke_access_token(token)
    await auth_service.revoke_refresh_token(refresh_token.refresh_token)
    return None

@router.post("/request-password-reset")
async def request_password_reset(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.user_repository.get_user_by_email(str(body.email))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    token = auth_service.create_reset_token(user.email)
    reset_link = f"{request.base_url}api/auth/reset-password?token={token}"
    background_tasks.add_task(send_email, user.email, user.username, reset_link)

    return {"message": "Password reset instructions sent to your email"}

@router.post("/reset-password")
async def reset_password(
    data: ResetPassword,
    auth_service: AuthService = Depends(get_auth_service),
):
    email = auth_service.decode_reset_token(data.token)
    user = await auth_service.user_repository.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_hashed = auth_service._hash_password(data.new_password)
    await auth_service.user_repository.update_password(user, new_hashed)

    return {"message": "Password has been successfully reset"}