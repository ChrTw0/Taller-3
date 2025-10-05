"""User Service User Management Routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..core.database import get_session
from ..schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserPublic, UserInternal,
    UserCreateResponse, BaseResponse, ErrorResponse
)
from ..services.user_service import UserService
from ..dependencies import get_current_active_user, get_admin_user
from ..models.user import User

router = APIRouter(prefix="/users", tags=["User Management"])

@router.post(
    "/",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}}
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_session)
):
    """Create a new user account."""

    logger.info(f"Creating new user with email: {user_data.email}")

    try:
        user = await UserService.create_user(db, user_data)
        return UserCreateResponse(
            message="User created successfully",
            data=UserResponse.model_validate(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse}}
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile."""
    return UserResponse.model_validate(current_user)

@router.put(
    "/me",
    response_model=UserResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}}
)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile."""

    logger.info(f"User updating profile: {current_user.id}")

    try:
        updated_user = await UserService.update_user(db, current_user.id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse.model_validate(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/{user_id}",
    response_model=UserPublic,
    responses={404: {"model": ErrorResponse}}
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Get user by ID (public info only)."""

    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserPublic.model_validate(user)

@router.get(
    "/internal/{user_id}",
    response_model=UserInternal,
    responses={404: {"model": ErrorResponse}},
    tags=["Internal"]
)
async def get_user_internal(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Get user by ID with email (for inter-service communication only)."""

    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserInternal.model_validate(user)

@router.get(
    "/code/{user_code}",
    response_model=UserPublic,
    responses={404: {"model": ErrorResponse}}
)
async def get_user_by_code(
    user_code: str,
    db: AsyncSession = Depends(get_session)
):
    """Get user by code (public info only)."""

    user = await UserService.get_user_by_code(db, user_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserPublic.model_validate(user)

@router.get(
    "/teachers",
    response_model=List[UserPublic],
    summary="Get All Teachers",
    description="Public endpoint to get all teachers and admins"
)
async def get_teachers(
    db: AsyncSession = Depends(get_session)
):
    """Get all users with teacher or admin role (public endpoint)."""

    users = await UserService.get_users(db, skip=0, limit=1000)
    # Filter only teachers and admins
    teachers = [UserPublic.model_validate(user) for user in users if user.role in ['teacher', 'admin']]
    return teachers

@router.get(
    "/",
    response_model=List[UserPublic],
    dependencies=[Depends(get_admin_user)]
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    db: AsyncSession = Depends(get_session)
):
    """List all users (admin only)."""

    users = await UserService.get_users(db, skip=skip, limit=limit)
    return [UserPublic.model_validate(user) for user in users]

@router.delete(
    "/{user_id}",
    response_model=BaseResponse,
    dependencies=[Depends(get_admin_user)],
    responses={404: {"model": ErrorResponse}}
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Deactivate user (admin only)."""

    logger.info(f"Admin deactivating user: {user_id}")

    success = await UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return BaseResponse(message="User deactivated successfully")