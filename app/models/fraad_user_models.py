from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class FraudUser(Base):
    __tablename__ = "fraud_users"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
