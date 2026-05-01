from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order_models import OrderStatus
from app.schemas.order_schemas import OrderStatusUpdate
from app.services import cart_service
from app.services import order_service

# Create an order from cart items, then clear the cart.
async def checkout_order(db: AsyncSession, user_id: UUID):
    try:
        order = await cart_service.checkout_cart(db, user_id)
    except cart_service.CartError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"order": order}

# Return one order with its saved order items.
async def get_order_by_id(db: AsyncSession, order_id: UUID):
    order = await order_service.get_order_by_id(db, order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

# Return order history for one user.
async def get_orders_by_user_id(db: AsyncSession, user_id: UUID):
    return await order_service.get_orders_by_user_id(db, user_id)

# Return one order only when it belongs to the requested user.
async def get_order_by_user_id_and_order_id(db: AsyncSession, user_id: UUID, order_id: UUID):
    order = await order_service.get_order_by_user_id_and_order_id(db, user_id, order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found for this user")

    return order

# Move an order through allowed status transitions only.
async def update_order_status(db: AsyncSession, order_id: UUID, payload: OrderStatusUpdate):
    order = await order_service.get_order_by_id(db, order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    next_status = OrderStatus(payload.status.value)

    if not order_service.can_transition_order_status(order.status, next_status):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change order status from {order_service.normalize_order_status(order.status).value} to {next_status.value}",
        )

    return await order_service.update_order_status(db, order, next_status)

# Cancel an order only when the current status allows cancellation.
async def cancel_order(db: AsyncSession, order_id: UUID):
    order = await order_service.get_order_by_id(db, order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if not order_service.can_transition_order_status(order.status, OrderStatus.CANCELLED):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order with status {order_service.normalize_order_status(order.status).value}",
        )

    return await order_service.cancel_order(db, order)
