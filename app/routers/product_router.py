from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import product_controller
from app.core.security import require_admin
from app.schemas.product_schemas import (
    ProductBulkCreate,
    ProductCreate,
    ProductsListResponse,
    ProductResponse,
    ProductSortBy,
    ProductStockUpdate,
    ProductUpdate,
)
from ..core.database import get_db


router = APIRouter(prefix="/products", tags=["Products"])

# create product
@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await product_controller.create_product(db, payload)


@router.post("/bulk", response_model=ProductsListResponse, status_code=status.HTTP_201_CREATED)
async def create_products_bulk(
    payload: ProductBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    products = await product_controller.create_products_bulk(db, payload.products)
    return {
        "message": "Products created successfully",
        "data": products,
    }


# get all product
@router.get("", response_model=list[ProductResponse])
async def get_all_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await product_controller.get_all_products(db, skip, limit)

# get only active product
@router.get("/active", response_model=list[ProductResponse])
async def get_active_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await product_controller.get_active_products(db, skip, limit)


@router.get("/search", response_model=list[ProductResponse])
async def search_products(
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    active_only: bool = True,
    sort_by: ProductSortBy = "name_asc",
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await product_controller.search_products(
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


# get single product
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await product_controller.get_product_by_id(db, product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await product_controller.update_product(db, product_id, payload)


@router.patch("/{product_id}/stock", response_model=ProductResponse)
async def update_product_stock(
    product_id: UUID,
    payload: ProductStockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await product_controller.update_product_stock(db, product_id, payload.stock_quantity)


# delete product by id
@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product_by_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await product_controller.delete_product_by_id(db, product_id)

# soft delete product by id
@router.patch("/{product_id}/soft-delete", response_model=ProductResponse)
async def soft_delete_product_by_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return await product_controller.soft_delete_product_by_id(db, product_id)
