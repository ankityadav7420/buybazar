from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.cart_schemas import CartItemCreate, CartItemQuantityUpdate
from app.services import cart_service


# Build the API response shape and calculate cart total from saved cart items.
def _cart_response(cart):
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": cart.items,
        "total_amount": cart_service.calculate_cart_total(cart),
    }


# Return the current user's cart; creates an empty cart if the user has none.
async def get_cart(db: AsyncSession, user_id: UUID):
    try:
        cart, total_amount = await cart_service.get_cart_response_data(db, user_id)
    except cart_service.CartError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": cart.items,
        "total_amount": total_amount,
    }


# Add a product to the user's cart using the product price saved in the database.
async def add_item_to_cart(db: AsyncSession, payload: CartItemCreate):
    try:
        cart = await cart_service.add_item_to_cart(
            db,
            payload.user_id,
            payload.product_id,
            payload.quantity,
        )
    except cart_service.CartError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _cart_response(cart)


# Change quantity for one item already present in the user's cart.
async def update_cart_item_quantity(
    db: AsyncSession,
    user_id: UUID,
    cart_item_id: UUID,
    payload: CartItemQuantityUpdate,
):
    try:
        cart = await cart_service.update_cart_item_quantity(
            db,
            user_id,
            cart_item_id,
            payload.quantity,
        )
    except cart_service.CartError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _cart_response(cart)


# Remove one item from the user's cart.
async def remove_cart_item(db: AsyncSession, user_id: UUID, cart_item_id: UUID):
    try:
        cart = await cart_service.remove_cart_item(db, user_id, cart_item_id)
    except cart_service.CartError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _cart_response(cart)
