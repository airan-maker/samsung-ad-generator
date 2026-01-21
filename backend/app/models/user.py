from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models import Base, TimestampMixin


class PlanType(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100))
    profile_image = Column(String(500))
    provider = Column(String(20))  # google, kakao
    provider_id = Column(String(255))
    credits = Column(Integer, default=3)
    plan = Column(Enum(PlanType), default=PlanType.FREE)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "profile_image": self.profile_image,
            "plan": self.plan.value,
            "credits": self.credits,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
