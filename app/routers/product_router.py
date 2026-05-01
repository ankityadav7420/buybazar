from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import product_controller
from app.core.security import require_admin
from app.schemas.product_schemas import ProductCreate, ProductResponse
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
# get single product
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    return await product_controller.get_product_by_id(db, product_id)

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
