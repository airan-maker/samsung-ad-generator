from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models import Base, TimestampMixin


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # KRW
    currency = Column(String(3), default="KRW")
    plan = Column(String(20))
    payment_method = Column(String(50))
    transaction_id = Column(String(255))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Relationships
    user = relationship("User", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.id} {self.amount}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "amount": self.amount,
            "currency": self.currency,
            "plan": self.plan,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
