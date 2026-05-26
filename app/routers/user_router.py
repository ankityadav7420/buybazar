from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import user_controller
from app.core.security import require_admin, require_self_or_admin
from app.schemas.user_schemas import UserCreate, UserDataResponse, UsersListResponse
from ..core.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


# Create user
@router.post("", response_model=UserDataResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await user_controller.create_user(db, payload)
    return {
        "message": "User created successfully",
        "data": user,
    }


# Get users
@router.get("", response_model=UsersListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    users = await user_controller.get_users(db, skip, limit)
    return {
        "message": "Users fetched successfully",
        "data": users,
    }


# Get single user
@router.get("/{user_id}", response_model=UserDataResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_self_or_admin),
):
    user = await user_controller.get_user(db, user_id)
    return {
        "message": "User fetched successfully",
        "data": user,
    }


# Delete user
@router.delete("/{user_id}", response_model=UserDataResponse)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    user = await user_controller.delete_user(db, user_id)
    return {
        "message": "User deleted successfully",
        "data": user,
    }
