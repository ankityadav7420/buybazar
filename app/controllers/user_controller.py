from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_schemas import UserCreate
from app.services import user_service


# Create a user who can own carts and orders.
async def create_user(db: AsyncSession, payload: UserCreate):
    try:
        return await user_service.create_user(db, payload)
    except user_service.UserCreateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Return all users.
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    return await user_service.get_users(db, skip, limit)


# Return one user or convert missing user into a 404 response.
async def get_user(db: AsyncSession, user_id: UUID):
    user = await user_service.get_user(db, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Permanently delete a user.
async def delete_user(db: AsyncSession, user_id: UUID):
    user = await user_service.delete_user(db, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
