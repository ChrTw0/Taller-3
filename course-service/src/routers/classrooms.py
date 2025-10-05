"""Course Service Classroom Management Routes - Independent Classrooms."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from ..core.database import get_session
from ..models.course import Classroom, CourseClassroom
from ..schemas.course import (
    ClassroomCreate, ClassroomUpdate, ClassroomResponse,
    CourseClassroomCreate, CourseClassroomUpdate, CourseClassroomResponse,
    BaseResponse, ErrorResponse
)

router = APIRouter(prefix="/classrooms", tags=["Classroom Management"])

# ==================== CLASSROOM CRUD (Independent) ====================

@router.post(
    "/",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}}
)
async def create_classroom(
    classroom_data: ClassroomCreate,
    db: AsyncSession = Depends(get_session)
):
    """Create a new independent classroom."""

    logger.info(f"Creating classroom: {classroom_data.code}")

    # Check if code already exists
    result = await db.execute(
        select(Classroom).where(Classroom.code == classroom_data.code)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Classroom with code '{classroom_data.code}' already exists"
        )

    try:
        classroom = Classroom(**classroom_data.model_dump())
        db.add(classroom)
        await db.commit()
        await db.refresh(classroom)

        logger.info(f"Classroom created: {classroom.id}")
        return ClassroomResponse.model_validate(classroom)

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating classroom: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/",
    response_model=List[ClassroomResponse],
    responses={500: {"model": ErrorResponse}}
)
async def get_all_classrooms(
    is_active: Optional[bool] = Query(None),
    building: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_session)
):
    """Get all classrooms with optional filters."""

    try:
        query = select(Classroom)

        if is_active is not None:
            query = query.where(Classroom.is_active == is_active)

        if building:
            query = query.where(Classroom.building.ilike(f"%{building}%"))

        query = query.offset(skip).limit(limit).order_by(Classroom.code)

        result = await db.execute(query)
        classrooms = result.scalars().all()

        return [ClassroomResponse.model_validate(c) for c in classrooms]

    except Exception as e:
        logger.error(f"Error fetching classrooms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get(
    "/{classroom_id}",
    response_model=ClassroomResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Get classroom by ID."""

    result = await db.execute(
        select(Classroom).where(Classroom.id == classroom_id)
    )
    classroom = result.scalar_one_or_none()

    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {classroom_id} not found"
        )

    return ClassroomResponse.model_validate(classroom)

@router.put(
    "/{classroom_id}",
    response_model=ClassroomResponse,
    responses={404: {"model": ErrorResponse}}
)
async def update_classroom(
    classroom_id: int,
    classroom_data: ClassroomUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update classroom."""

    result = await db.execute(
        select(Classroom).where(Classroom.id == classroom_id)
    )
    classroom = result.scalar_one_or_none()

    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {classroom_id} not found"
        )

    try:
        update_data = classroom_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(classroom, key, value)

        await db.commit()
        await db.refresh(classroom)

        logger.info(f"Classroom updated: {classroom.id}")
        return ClassroomResponse.model_validate(classroom)

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating classroom: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete(
    "/{classroom_id}",
    response_model=BaseResponse,
    responses={404: {"model": ErrorResponse}}
)
async def delete_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Delete classroom (soft delete)."""

    result = await db.execute(
        select(Classroom).where(Classroom.id == classroom_id)
    )
    classroom = result.scalar_one_or_none()

    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {classroom_id} not found"
        )

    try:
        classroom.is_active = False
        await db.commit()

        logger.info(f"Classroom deleted: {classroom.id}")
        return BaseResponse(
            success=True,
            message=f"Classroom {classroom.code} deleted successfully"
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting classroom: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
