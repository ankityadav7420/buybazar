from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.order_schemas import OrderResponse


class CartItemCreate(BaseModel):
    user_id: UUID
    product_id: UUID
    quantity: int = Field(gt=0, le=100)


class CartItemQuantityUpdate(BaseModel):
    quantity: int = Field(gt=0, le=100)


class CartItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: UUID
    user_id: UUID
    items: list[CartItemResponse] = []
    total_amount: float

    class Config:
        from_attributes = True


class CartCheckoutResponse(BaseModel):
    order: OrderResponse
