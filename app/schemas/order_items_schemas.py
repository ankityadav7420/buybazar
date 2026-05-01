from uuid import UUID

from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True
