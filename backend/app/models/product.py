from sqlalchemy import Column, String, Text, Date, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.models import Base, TimestampMixin


class ProductCategory(str, enum.Enum):
    SMARTPHONE = "smartphone"
    TV = "tv"
    APPLIANCE = "appliance"
    WEARABLE = "wearable"


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    model_number = Column(String(100))
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    subcategory = Column(String(50))
    description = Column(Text)
    specs = Column(JSONB)  # {"display": "6.9인치", "processor": "...", ...}
    images = Column(JSONB)  # ["url1", "url2", ...]
    features = Column(JSONB)  # ["feature1", "feature2", ...]
    released_at = Column(Date)

    def __repr__(self):
        return f"<Product {self.name}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "model_number": self.model_number,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "description": self.description,
            "specs": self.specs,
            "images": self.images,
            "features": self.features,
            "released_at": self.released_at.isoformat() if self.released_at else None,
        }

    @property
    def thumbnail(self):
        if self.images and len(self.images) > 0:
            return self.images[0]
        return None
