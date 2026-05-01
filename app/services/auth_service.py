import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.user_models import User

_otp_store: dict[str, str] = {}


class AuthError(Exception):
    pass


# Find a user by normalized email or mobile.
async def get_user_by_identifier(db: AsyncSession, identifier: str):
    result = await db.execute(
        select(User).where((User.email == identifier) | (User.mobile == identifier))
    )
    return result.scalars().first()


# Generate and store a short-lived development OTP.
async def request_otp(db: AsyncSession, identifier: str) -> str:
    user = await get_user_by_identifier(db, identifier)

    if user is None or user.is_deleted:
        raise AuthError("User not found")

    otp = f"{random.randint(100000, 999999)}"
    _otp_store[identifier] = otp
    return otp


# Verify OTP or master OTP, then issue a JWT.
async def login_with_otp(db: AsyncSession, identifier: str, otp: str) -> str:
    settings = get_settings()
    user = await get_user_by_identifier(db, identifier)

    if user is None or user.is_deleted:
        raise AuthError("User not found")

    expected_otp = _otp_store.get(identifier)

    if otp != settings.master_otp and otp != expected_otp:
        raise AuthError("Invalid OTP")

    _otp_store.pop(identifier, None)
    return create_access_token(user.id, user.role)
