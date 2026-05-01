from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import auth_controller
from app.core.database import get_db
from app.schemas.auth_schemas import OtpLogin, OtpRequest, OtpRequestResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/otp/request", response_model=OtpRequestResponse)
async def request_otp(payload: OtpRequest, db: AsyncSession = Depends(get_db)):
    return await auth_controller.request_otp(db, payload)


@router.post("/otp/login", response_model=TokenResponse)
async def login(payload: OtpLogin, db: AsyncSession = Depends(get_db)):
    return await auth_controller.login(db, payload)
