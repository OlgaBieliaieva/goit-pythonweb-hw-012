from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    status,
    BackgroundTasks,
    UploadFile,
    File,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.conf.config import settings
from src.utils.depend_service import (
    get_auth_service,
    get_user_service,
    get_current_admin_user
)
from src.utils.email_token import get_email_from_token
from src.database.db import get_db
from src.models.user_model import User
from src.schemas.email import RequestEmail
from src.schemas.user import UserResponse
from src.services.auth import AuthService, oauth2_scheme
from src.services.email import send_email
from src.services.upload_file import UploadFileService
from src.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=UserResponse)
@limiter.limit("10/minute")
async def me(
    request: Request,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get the current authenticated user's details.

    Args:
        request: The request object.
        token: The OAuth2 token used for authentication.
        auth_service: The AuthService to handle authentication logic.

    Returns:
        A UserResponse model containing the user's details.
    """
    return await auth_service.get_current_user(token)


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str, user_service: UserService = Depends(get_user_service)
):
    """
    Confirm the user's email address using the verification token.

    Args:
        token: The email confirmation token.
        user_service: The UserService to handle user-related operations.

    Returns:
        A message indicating whether the email is confirmed or already confirmed.
    """
    email = get_email_from_token(token)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Your email successfully confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    """
    Request an email verification for a user.

    Args:
        body: The request email schema containing the email to verify.
        background_tasks: The background tasks to send the email.
        request: The request object to generate the email URL.
        user_service: The UserService to handle user-related operations.

    Returns:
        A message instructing the user to check their email.
    """
    user = await user_service.get_user_by_email(str(body.email))

    if user.confirmed:
        return {"message": "Your email already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Check your email"}



@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update the avatar for the current authenticated user.

    Args:
        file: The new avatar file uploaded by the user.
        user: The current authenticated user.
        user_service: The UserService to handle user-related operations.

    Returns:
        A UserResponse model containing the updated user details.
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET
    ).upload_file(file, user.username)

    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    """
    Admin route to check the authentication and authorization of an admin user.

    Args:
        current_user: The current authenticated user, expected to be an admin.

    Returns:
        A message welcoming the admin user.
    """
    return {"message": f"Вітаємо, {current_user.username}! Це адміністративний маршрут"}