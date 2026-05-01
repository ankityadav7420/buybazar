from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user_models import User
from app.schemas.user_schemas import UserCreate


class UserCreateError(Exception):
    pass


# Create a user after checking email/mobile uniqueness.
async def create_user(db: AsyncSession, user: UserCreate):
    result = await db.execute(
        select(User).where((User.email == user.email) | (User.mobile == user.mobile))
    )
    existing_user = result.scalars().first()

    if existing_user:
        if existing_user.email == user.email:
            raise UserCreateError("Email is already registered")

        raise UserCreateError("Mobile is already registered")

    db_user = User(
        name=user.name,
        email=user.email,
        age=user.age,
        mobile=user.mobile,
        role="user",
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# Return all users.
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    return result.scalars().all()

# Return users that are not soft-deleted.
async def get_active_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(User).where(User.is_deleted == 0).offset(skip).limit(limit)
    )
    return result.scalars().all()

# Fetch one user by UUID.
async def get_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


# Permanently remove a user row.
async def delete_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        await db.delete(user)
        await db.commit()

    return user


# Soft delete a user without removing the row.
async def soft_delete_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.is_deleted = 1  # Mark as deleted
        await db.commit()

    return user
