from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product_models import Product
from app.schemas.product_schemas import ProductCreate


# Create a product available for carts and checkout.
async def create_product(db: AsyncSession, product: ProductCreate):
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity
    )

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


# Return all product rows, including soft-deleted products.
async def get_all_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Product).offset(skip).limit(limit)
    )
    return result.scalars().all()


# Return only products that users can buy.
async def get_active_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Product).where(Product.is_deleted == 0).offset(skip).limit(limit)
    )
    return result.scalars().all()


# Fetch one product by UUID.
async def get_product_by_id(db: AsyncSession, product_id: UUID):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    return result.scalar_one_or_none()

# Permanently remove a product row.
async def delete_product_by_id(db: AsyncSession, product_id: UUID):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if product:
        await db.delete(product)
        await db.commit()

    return product

# Soft delete a product so it no longer appears as active.
async def soft_delete_product_by_id(db: AsyncSession, product_id: UUID):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if product:
        product.is_deleted = 1
        await db.commit()

    return product
