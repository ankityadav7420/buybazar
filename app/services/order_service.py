from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order_models import Orders, OrderStatus


ALLOWED_STATUS_TRANSITIONS = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


# Normalize DB/string enum values before checking transitions.
def normalize_order_status(status: OrderStatus | str) -> OrderStatus:
    if isinstance(status, OrderStatus):
        return status

    return OrderStatus(status.lower())


# Fetch one order with order_items loaded for API response serialization.
async def get_order_by_id(db: AsyncSession, order_id: UUID):
    result = await db.execute(
        select(Orders)
        .options(selectinload(Orders.order_items))
        .where(Orders.id == order_id)
    )
    return result.scalar_one_or_none()


# Fetch all orders for a user with order_items loaded.
async def get_orders_by_user_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Orders)
        .options(selectinload(Orders.order_items))
        .where(Orders.user_id == user_id)
    )
    return result.scalars().all()


# Fetch one order only if it belongs to the given user.
async def get_order_by_user_id_and_order_id(db: AsyncSession, user_id: UUID, order_id: UUID):
    result = await db.execute(
        select(Orders)
        .options(selectinload(Orders.order_items))
        .where(Orders.user_id == user_id, Orders.id == order_id)
    )
    return result.scalar_one_or_none()


# Return whether an order can move from the current status to the next status.
def can_transition_order_status(current_status: OrderStatus | str, next_status: OrderStatus) -> bool:
    current_status = normalize_order_status(current_status)
    return next_status in ALLOWED_STATUS_TRANSITIONS[current_status]


# Persist a valid order status change.
async def update_order_status(db: AsyncSession, order: Orders, next_status: OrderStatus):
    order.status = next_status

    if next_status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.utcnow()

    await db.commit()
    await db.refresh(order)
    return order


# Convenience wrapper for moving an order into cancelled status.
async def cancel_order(db: AsyncSession, order: Orders):
    return await update_order_status(db, order, OrderStatus.CANCELLED)
