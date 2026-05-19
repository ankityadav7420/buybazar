from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.core.security import create_access_token, decode_access_token, require_admin, require_user


def test_create_access_token_can_be_decoded():
    user_id = uuid4()

    token = create_access_token(user_id=user_id, role="admin")
    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_decode_access_token_rejects_tampered_token():
    token = create_access_token(user_id=uuid4(), role="user")
    tampered_token = f"{token[:-1]}x"

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(tampered_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"


def test_require_admin_allows_admin_user():
    current_user = {"id": uuid4(), "role": "admin"}

    assert require_admin(current_user) == current_user


def test_require_user_rejects_admin_user():
    with pytest.raises(HTTPException) as exc_info:
        require_user({"id": uuid4(), "role": "admin"})

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "User access required"
