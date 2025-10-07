"""User Service Authentication Routes."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..core.database import get_session
from ..core.security import create_access_token
from ..core.config import get_settings
from ..schemas.user import UserLogin, UserPublic, UserLoginResponse, Token, ErrorResponse, UserCreate, UserCreateResponse, UserResponse
from ..services.user_service import UserService
from ..core.security import get_current_user

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/login",
    response_model=UserLoginResponse,
    responses={401: {"model": ErrorResponse}}
)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_session)
):
    """Authenticate user and return JWT token."""

    logger.info(f"Login attempt for email: {user_credentials.email}")

    # Authenticate user
    user = await UserService.authenticate_user(
        db, user_credentials.email, user_credentials.password
    )

    if not user:
        logger.warning(f"Failed login attempt for: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )

    logger.info(f"User logged in successfully: {user.email}")

    return UserLoginResponse(
        message="Login successful",
        data=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        ),
        user=UserPublic(
            id=user.id,
            code=user.code,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active
        )
    )

@router.post("/refresh")
async def refresh_token():
    """Refresh JWT token (placeholder for future implementation)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented yet"
    )

@router.post("/logout")
async def logout():
    """Logout user (placeholder for future implementation)."""
    # In a stateless JWT setup, logout is typically handled client-side
    # For server-side logout, you'd need a token blacklist
    return {"message": "Logout successful"}

@router.post(
    "/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}}
)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Register a new user (admin only)."""

    # Only admins can register new users
    if current_user.get("role") != "admin":
        logger.warning(f"Unauthorized registration attempt by user: {current_user.get('email')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can register new users"
        )

    logger.info(f"Admin {current_user.get('email')} attempting to register user: {user_data.email}")

    # Check if user already exists
    existing_user = await UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        logger.warning(f"Registration failed - email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Check if code already exists
    existing_code = await UserService.get_user_by_code(db, user_data.code)
    if existing_code:
        logger.warning(f"Registration failed - code already exists: {user_data.code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this code already exists"
        )

    # Create the user
    new_user = await UserService.create_user(db, user_data)
    logger.info(f"User registered successfully: {new_user.email} by admin: {current_user.get('email')}")

    return UserCreateResponse(
        message="User registered successfully",
        data=UserResponse(
            id=new_user.id,
            code=new_user.code,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            role=new_user.role,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at)
    )