from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product_schemas import ProductCreate, ProductSortBy, ProductUpdate
from app.services import product_service


# Create a product that can later be added to carts and orders.
async def create_product(db: AsyncSession, payload: ProductCreate):
    return await product_service.create_product(db, payload)


async def create_products_bulk(db: AsyncSession, payloads: list[ProductCreate]):
    return await product_service.create_products_bulk(db, payloads)


# Return all products, including soft-deleted ones.
async def get_all_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    return await product_service.get_all_products(db, skip, limit)

# Return only products available for users to buy.
async def get_active_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    return await product_service.get_active_products(db, skip, limit)


async def search_products(
    db: AsyncSession,
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    active_only: bool = True,
    sort_by: ProductSortBy = "name_asc",
    skip: int = 0,
    limit: int = 100,
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")

    return await product_service.search_products(
        db,
        q=q,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        active_only=active_only,
        sort_by=sort_by,
        skip=skip,
        limit=limit,
    )


# Return one product or convert missing product into a 404 response.
async def get_product_by_id(db: AsyncSession, product_id: UUID):
    product = await product_service.get_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


async def update_product(db: AsyncSession, product_id: UUID, payload: ProductUpdate):
    product = await product_service.update_product(db, product_id, payload)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


async def update_product_stock(db: AsyncSession, product_id: UUID, stock_quantity: int):
    product = await product_service.update_product_stock(db, product_id, stock_quantity)

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
