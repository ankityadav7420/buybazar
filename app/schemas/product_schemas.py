from uuid import UUID

from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=2, max_length=1000)
    price: float = Field(gt=0)
    stock_quantity: int = Field(ge=0)

class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    stock_quantity: int
    is_deleted: int

    class Config:
        from_attributes = True
