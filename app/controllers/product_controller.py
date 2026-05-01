from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product_schemas import ProductCreate
from app.services import product_service


# Create a product that can later be added to carts and orders.
async def create_product(db: AsyncSession, payload: ProductCreate):
    return await product_service.create_product(db, payload)


# Return all products, including soft-deleted ones.
async def get_all_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    return await product_service.get_all_products(db, skip, limit)

# Return only products available for users to buy.
async def get_active_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    return await product_service.get_active_products(db, skip, limit)


# Return one product or convert missing product into a 404 response.
async def get_product_by_id(db: AsyncSession, product_id: UUID):
    product = await product_service.get_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# Permanently delete a product.
async def delete_product_by_id(db: AsyncSession, product_id: UUID):
    product = await product_service.delete_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# Mark a product deleted without removing the row.
async def soft_delete_product_by_id(db: AsyncSession, product_id: UUID):
    product = await product_service.soft_delete_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
