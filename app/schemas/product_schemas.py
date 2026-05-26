from uuid import UUID

from pydantic import BaseModel, Field
from typing import Literal

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=2, max_length=1000)
    price: float = Field(gt=0)
    stock_quantity: int = Field(ge=0)


class ProductBulkCreate(BaseModel):
    products: list[ProductCreate] = Field(min_length=1, max_length=100)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, min_length=2, max_length=1000)
    price: float | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_deleted: int | None = Field(default=None, ge=0, le=1)


class ProductStockUpdate(BaseModel):
    stock_quantity: int = Field(ge=0)


ProductSortBy = Literal["name_asc", "name_desc", "price_asc", "price_desc"]


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    stock_quantity: int
    is_deleted: int

    class Config:
        from_attributes = True


class ProductsListResponse(BaseModel):
    message: str
    data: list[ProductResponse]
