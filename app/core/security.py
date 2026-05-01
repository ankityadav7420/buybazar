import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

bearer_scheme = HTTPBearer()


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user_id: UUID, role: str) -> str:
    settings = get_settings()
    header = {"alg": "HS256", "typ": "JWT"}
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": int(expires_at.timestamp()),
    }

    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(settings.jwt_secret_key.encode(), signing_input, hashlib.sha256).digest()

    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"


def decode_access_token(token: str) -> dict:
    settings = get_settings()

    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    expected_signature = hmac.new(settings.jwt_secret_key.encode(), signing_input, hashlib.sha256).digest()
    actual_signature = _base64url_decode(encoded_signature)

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise HTTPException(status_code=401, detail="Invalid token")

    payload = json.loads(_base64url_decode(encoded_payload))

    if payload["exp"] < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="Token expired")

    return payload


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    payload = decode_access_token(credentials.credentials)

    return {
        "id": UUID(payload["sub"]),
        "role": payload["role"],
    }


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return current_user


def require_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User access required")

    return current_user


def require_self_or_admin(user_id: UUID, current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] == "admin" or current_user["id"] == user_id:
        return current_user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
