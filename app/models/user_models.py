import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)
    mobile = Column(String, unique=True, index=True)
    role = Column(String, default="user", nullable=False)
    is_deleted = Column(Integer, default=0)  # 0 for active, 1 for deleted (soft delete)
    orders = relationship("Orders", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)
