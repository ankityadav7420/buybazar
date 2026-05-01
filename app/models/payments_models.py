import enum
import uuid

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class PaymentStatus(enum.Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED="refunded"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    payment_date = Column(DateTime, default=func.now())
    currency = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.CREATED, nullable=False)

    order = relationship("Orders", back_populates="payments")
