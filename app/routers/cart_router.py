from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import cart_controller
from app.core.database import get_db
from app.core.security import require_self_or_admin, require_user
from app.schemas.cart_schemas import (
    CartItemCreate,
    CartItemQuantityUpdate,
    CartResponse,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/{user_id}", response_model=CartResponse)
async def get_cart(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_self_or_admin),
):
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Cannot get another user's cart")

    return await cart_controller.get_cart(db, user_id)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    payload: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_user),
):
    if current_user["id"] != payload.user_id:
        raise HTTPException(status_code=403, detail="Cannot add items to another user's cart")

    return await cart_controller.add_item_to_cart(db, payload)


@router.patch("/{user_id}/items/{cart_item_id}", response_model=CartResponse)
async def update_cart_item_quantity(
    user_id: UUID,
    cart_item_id: UUID,
    payload: CartItemQuantityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_self_or_admin),
):
    return await cart_controller.update_cart_item_quantity(db, user_id, cart_item_id, payload)


@router.delete("/{user_id}/items/{cart_item_id}", response_model=CartResponse)
async def remove_cart_item(
    user_id: UUID,
    cart_item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_self_or_admin),
):
    return await cart_controller.remove_cart_item(db, user_id, cart_item_id)
