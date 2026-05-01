from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import user_controller
from app.core.security import require_admin, require_self_or_admin
from app.schemas.user_schemas import UserCreate, UserResponse
from ..core.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


# Create user
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await user_controller.create_user(db, payload)


# Get users
@router.get("", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await user_controller.get_users(db, skip, limit)


# Get single user
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_self_or_admin),
):
    return await user_controller.get_user(db, user_id)


# Delete user
@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await user_controller.delete_user(db, user_id)
