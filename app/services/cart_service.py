from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart_models import Cart, CartItem
from app.models.order_items_models import OrderItem
from app.models.order_models import OrderStatus, Orders
from app.models.product_models import Product
from app.models.user_models import User
from app.services.order_service import get_order_by_id


class CartError(Exception):
    pass


# Load a user's cart with items eagerly loaded for async response serialization.
async def get_cart_by_user_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items))
        .where(Cart.user_id == user_id)
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


# Return the existing user cart or create an empty one for first-time users.
async def get_or_create_cart(db: AsyncSession, user_id: UUID):
    user = await db.get(User, user_id)

    if user is None:
        raise CartError("User not found")

    cart = await get_cart_by_user_id(db, user_id)

    if cart is not None:
        return cart

    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.flush()
    return await get_cart_by_user_id(db, user_id)


# Return cart plus total amount for API response payloads.
async def get_cart_response_data(db: AsyncSession, user_id: UUID):
    cart = await get_or_create_cart(db, user_id)
    return cart, calculate_cart_total(cart)


# Calculate total from trusted unit prices stored on cart items.
def calculate_cart_total(cart: Cart) -> float:
    return sum(item.unit_price * item.quantity for item in cart.items)


# Add a product to cart after checking product existence, deletion state, and stock.
async def add_item_to_cart(db: AsyncSession, user_id: UUID, product_id: UUID, quantity: int):
    if quantity <= 0:
        raise CartError("Quantity must be greater than 0")

    cart = await get_or_create_cart(db, user_id)
    product = await db.get(Product, product_id)

    if product is None or product.is_deleted:
        raise CartError("Product not found")

    existing_item = next((item for item in cart.items if item.product_id == product_id), None)
    current_quantity = existing_item.quantity if existing_item else 0
    next_quantity = current_quantity + quantity

    if product.stock_quantity is not None and product.stock_quantity < next_quantity:
        raise CartError("Product does not have enough stock")

    if existing_item:
        existing_item.quantity = next_quantity
        existing_item.unit_price = product.price
    else:
        cart.items.append(
            CartItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price,
            )
        )

    await db.commit()
    return await get_cart_by_user_id(db, user_id)


# Replace the quantity for one cart item and refresh its unit price from product.
async def update_cart_item_quantity(db: AsyncSession, user_id: UUID, cart_item_id: UUID, quantity: int):
    if quantity <= 0:
        raise CartError("Quantity must be greater than 0")

    cart = await get_or_create_cart(db, user_id)
    cart_item = next((item for item in cart.items if item.id == cart_item_id), None)

    if cart_item is None:
        raise CartError("Cart item not found")

    product = await db.get(Product, cart_item.product_id)

    if product is None or product.is_deleted:
        raise CartError("Product not found")

    if product.stock_quantity is not None and product.stock_quantity < quantity:
        raise CartError("Product does not have enough stock")

    cart_item.quantity = quantity
    cart_item.unit_price = product.price
    await db.commit()
    return await get_cart_by_user_id(db, user_id)


# Remove one item from a user's cart.
async def remove_cart_item(db: AsyncSession, user_id: UUID, cart_item_id: UUID):
    cart = await get_or_create_cart(db, user_id)
    cart_item = next((item for item in cart.items if item.id == cart_item_id), None)

    if cart_item is None:
        raise CartError("Cart item not found")

    await db.delete(cart_item)
    await db.commit()
    return await get_cart_by_user_id(db, user_id)


# Checkout implementation used by POST /orders/checkout/{user_id}.
# It converts cart_items into order_items, reduces stock, and clears the cart.
async def checkout_cart(db: AsyncSession, user_id: UUID):
    cart = await get_or_create_cart(db, user_id)

    if not cart.items:
        raise CartError("Cart is empty")

    total_amount = 0.0
    order_items = []

    for cart_item in cart.items:
        product = await db.get(Product, cart_item.product_id)

        if product is None or product.is_deleted:
            raise CartError(f"Product {cart_item.product_id} not found")

        if product.stock_quantity is not None and product.stock_quantity < cart_item.quantity:
            raise CartError(f"Product {cart_item.product_id} does not have enough stock")

        unit_price = product.price
        total_amount += unit_price * cart_item.quantity

        if product.stock_quantity is not None:
            product.stock_quantity -= cart_item.quantity

        order_items.append(
            OrderItem(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
            )
        )

    order = Orders(
        user_id=user_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        order_items=order_items,
    )

    db.add(order)

    for cart_item in list(cart.items):
        await db.delete(cart_item)

    await db.commit()
    return await get_order_by_id(db, order.id)
