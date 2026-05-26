from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import order_controller
from app.core.security import get_current_user, require_admin, require_self_or_admin, require_user
from app.schemas.cart_schemas import CartCheckoutResponse
from app.schemas.order_schemas import OrderResponse, OrderStatusUpdate
from ..core.database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])


def _can_access_order(current_user: dict, order: OrderResponse) -> bool:
    return current_user["role"] == "admin" or current_user["id"] == order.user_id

# Create an order from the user's cart.
@router.post("/checkout/{user_id}", response_model=CartCheckoutResponse, status_code=status.HTTP_201_CREATED)
async def checkout_order(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_user),
):
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Cannot checkout another user's cart")

    return await order_controller.checkout_order(db, user_id)

# Get Orders by User ID
@router.get("/user/{user_id}", response_model=list[OrderResponse])
async def get_orders_by_user_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_self_or_admin),
):
    return await order_controller.get_orders_by_user_id(db, user_id)

# Get one user's specific order.
@router.get("/user/{user_id}/{order_id}", response_model=OrderResponse)
async def get_order_by_user_id_and_order_id(
    user_id: UUID,
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_self_or_admin),
):
    return await order_controller.get_order_by_user_id_and_order_id(db, user_id, order_id)

# Get Order by ID
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    order = await order_controller.get_order_by_id(db, order_id)

    if not _can_access_order(current_user, order):
        raise HTTPException(status_code=403, detail="Cannot fetch another user's order")

    return order

# Update Order Status
@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await order_controller.update_order_status(db, order_id, payload)

# Cancel Order
@router.post("/{order_id}/cancel", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def cancel_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    order = await order_controller.get_order_by_id(db, order_id)

    if not _can_access_order(current_user, order):
        raise HTTPException(status_code=403, detail="Cannot cancel another user's order")

    return await order_controller.cancel_order(db, order_id)
