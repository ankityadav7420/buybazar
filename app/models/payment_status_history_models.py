import enum
import uuid

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class PaymentStatusHistory(enum.Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED="refunded"

class PaymentStatusHistory(Base):
    __tablename__ = "payment_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)
    payment_date = Column(DateTime, default=func.now())
    status = Column(Enum(PaymentStatusHistory), default=PaymentStatusHistory.CREATED, nullable=False)
    status_at = Column(DateTime, default=func.now(), nullable=False)

    payment = relationship("Payment")
