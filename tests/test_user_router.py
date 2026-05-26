import asyncio
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.routers import user_router


@dataclass
class UserStub:
    id: UUID
    name: str = "Test User"
    email: str = "test@example.com"
    age: int = 30
    mobile: str = "9999999999"
    role: str = "user"
    is_deleted: int = 0


def test_create_user_returns_standard_message(monkeypatch):
    user = UserStub(id=uuid4())

    async def fake_create_user(db, payload):
        return user

    monkeypatch.setattr(user_router.user_controller, "create_user", fake_create_user)

    response = asyncio.run(user_router.create_user(payload=object(), db=object()))

    assert response == {
        "message": "User created successfully",
        "data": user,
    }


def test_get_users_returns_standard_message(monkeypatch):
    users = [UserStub(id=uuid4()), UserStub(id=uuid4(), email="other@example.com")]

    async def fake_get_users(db, skip, limit):
        return users

    monkeypatch.setattr(user_router.user_controller, "get_users", fake_get_users)

    response = asyncio.run(user_router.get_users(db=object(), current_user={}))

    assert response == {
        "message": "Users fetched successfully",
        "data": users,
    }


def test_get_user_returns_standard_message(monkeypatch):
    user = UserStub(id=uuid4())

    async def fake_get_user(db, user_id):
        return user

    monkeypatch.setattr(user_router.user_controller, "get_user", fake_get_user)

    response = asyncio.run(user_router.get_user(user_id=user.id, db=object(), current_user={}))

    assert response == {
        "message": "User fetched successfully",
        "data": user,
    }


def test_delete_user_returns_standard_message(monkeypatch):
    user = UserStub(id=uuid4(), is_deleted=1)

    async def fake_delete_user(db, user_id):
        return user

    monkeypatch.setattr(user_router.user_controller, "delete_user", fake_delete_user)

    response = asyncio.run(user_router.delete_user(user_id=user.id, db=object(), current_user={}))

    assert response == {
        "message": "User deleted successfully",
        "data": user,
    }
