from pydantic import BaseModel, Field, field_validator

from app.schemas.user_schemas import EMAIL_PATTERN, MOBILE_PATTERN


class OtpRequest(BaseModel):
    identifier: str = Field(description="Email or mobile number")

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        identifier = value.strip().lower().replace(" ", "").replace("-", "")

        if not EMAIL_PATTERN.match(identifier) and not MOBILE_PATTERN.match(identifier):
            raise ValueError("Enter a valid email or mobile number")

        return identifier


class OtpRequestResponse(BaseModel):
    message: str
    dev_otp: str


class OtpLogin(BaseModel):
    identifier: str
    otp: str = Field(min_length=4, max_length=10)

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "").replace("-", "")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
