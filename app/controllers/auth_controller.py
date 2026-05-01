from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth_schemas import OtpLogin, OtpRequest
from app.services import auth_service


# Request an OTP for a registered email/mobile.
async def request_otp(db: AsyncSession, payload: OtpRequest):
    try:
        otp = await auth_service.request_otp(db, payload.identifier)
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": "OTP generated. Use SMS/email provider in production.", "dev_otp": otp}


# Verify OTP and return a JWT bearer token.
async def login(db: AsyncSession, payload: OtpLogin):
    try:
        token = await auth_service.login_with_otp(db, payload.identifier, payload.otp)
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return {"access_token": token, "token_type": "bearer"}
