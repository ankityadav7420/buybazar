import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.routers import order_route


def test_admin_can_fetch_orders_for_any_user(monkeypatch):
    user_id = uuid4()
    orders = [SimpleNamespace(id=uuid4(), user_id=user_id)]

    async def fake_get_orders_by_user_id(db, requested_user_id):
        assert requested_user_id == user_id
        return orders

    monkeypatch.setattr(
        order_route.order_controller,
        "get_orders_by_user_id",
        fake_get_orders_by_user_id,
    )

    response = asyncio.run(
        order_route.get_orders_by_user_id(
            user_id=user_id,
            db=object(),
            current_user={"id": uuid4(), "role": "admin"},
        )
    )

    assert response == orders


def test_order_owner_can_fetch_order_by_id(monkeypatch):
    user_id = uuid4()
    order = SimpleNamespace(id=uuid4(), user_id=user_id)

    async def fake_get_order_by_id(db, order_id):
        assert order_id == order.id
        return order

    monkeypatch.setattr(order_route.order_controller, "get_order_by_id", fake_get_order_by_id)

    response = asyncio.run(
        order_route.get_order_by_id(
            order_id=order.id,
            db=object(),
            current_user={"id": user_id, "role": "user"},
        )
    )

    assert response == order


def test_user_cannot_fetch_another_users_order(monkeypatch):
    order = SimpleNamespace(id=uuid4(), user_id=uuid4())

    async def fake_get_order_by_id(db, order_id):
        return order

    monkeypatch.setattr(order_route.order_controller, "get_order_by_id", fake_get_order_by_id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            order_route.get_order_by_id(
                order_id=order.id,
                db=object(),
                current_user={"id": uuid4(), "role": "user"},
            )
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Cannot fetch another user's order"


def test_order_owner_can_cancel_order(monkeypatch):
    user_id = uuid4()
    order = SimpleNamespace(id=uuid4(), user_id=user_id)
    cancelled_order = SimpleNamespace(id=order.id, user_id=user_id, status="cancelled")

    async def fake_get_order_by_id(db, order_id):
        return order

    async def fake_cancel_order(db, order_id):
        assert order_id == order.id
        return cancelled_order

    monkeypatch.setattr(order_route.order_controller, "get_order_by_id", fake_get_order_by_id)
    monkeypatch.setattr(order_route.order_controller, "cancel_order", fake_cancel_order)

    response = asyncio.run(
        order_route.cancel_order(
            order_id=order.id,
            db=object(),
            current_user={"id": user_id, "role": "user"},
        )
    )

    assert response == cancelled_order


def test_user_cannot_cancel_another_users_order(monkeypatch):
    order = SimpleNamespace(id=uuid4(), user_id=uuid4())

    async def fake_get_order_by_id(db, order_id):
        return order

    monkeypatch.setattr(order_route.order_controller, "get_order_by_id", fake_get_order_by_id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            order_route.cancel_order(
                order_id=order.id,
                db=object(),
                current_user={"id": uuid4(), "role": "user"},
            )
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Cannot cancel another user's order"
