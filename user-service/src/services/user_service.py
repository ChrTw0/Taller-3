"""User Service Business Logic."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from loguru import logger

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserLogin
from ..core.security import get_password_hash, verify_password, validate_password

class UserService:
    """User business logic service."""

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user."""
        logger.info(f"Creating user with email: {user_data.email}")

        # Validate password
        if not validate_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet requirements"
            )

        # Check if user already exists
        existing_user = await UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if code already exists
        existing_code = await UserService.get_user_by_code(db, user_data.code)
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User code already exists"
            )

        # Create user
        db_user = User(
            code=user_data.code,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
        )

        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            logger.info(f"User created successfully: {db_user.id}")
            return db_user
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating user"
            )

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        logger.info(f"Authenticating user: {email}")

        user = await UserService.get_user_by_email(db, email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None

        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {email}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {email}")
            return None

        logger.info(f"User authenticated successfully: {email}")
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_code(db: AsyncSession, code: str) -> Optional[User]:
        """Get user by code."""
        result = await db.execute(select(User).where(User.code == code))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination."""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user profile."""
        logger.info(f"Updating user: {user_id}")

        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            await db.commit()
            await db.refresh(user)
            logger.info(f"User updated successfully: {user_id}")
            return user
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating user"
            )

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Soft delete user (deactivate)."""
        logger.info(f"Deactivating user: {user_id}")

        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        await db.commit()
        logger.info(f"User deactivated successfully: {user_id}")
        return True