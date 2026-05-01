from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.models.order_models import OrderStatus
from app.schemas.order_items_schemas import OrderItemResponse


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    order_date: datetime
    total_amount: float
    status: OrderStatus
    delivered_at: datetime | None = None
    order_items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True
