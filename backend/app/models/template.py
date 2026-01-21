from sqlalchemy import Column, String, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.types import Integer
import uuid
import enum

from app.models import Base, TimestampMixin
from app.models.product import ProductCategory


class TemplateStyle(str, enum.Enum):
    UNBOXING = "unboxing"
    LIFESTYLE = "lifestyle"
    COMPARISON = "comparison"
    FEATURE = "feature"
    GAMING = "gaming"
    SMARTHOME = "smarthome"
    INTERIOR = "interior"
    HEALTH = "health"


class Template(Base, TimestampMixin):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    style = Column(Enum(TemplateStyle), nullable=False)
    durations = Column(ARRAY(Integer))  # [15, 30, 60]
    thumbnail_url = Column(String(500))
    preview_url = Column(String(500))
    config = Column(JSONB)  # Template configuration
    is_premium = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Template {self.name}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "style": self.style.value,
            "durations": self.durations,
            "thumbnail": self.thumbnail_url,
            "preview_url": self.preview_url,
            "is_premium": self.is_premium,
        }
