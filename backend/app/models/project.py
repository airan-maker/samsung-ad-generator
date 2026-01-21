from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models import Base, TimestampMixin


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=True)
    custom_product_image = Column(String(500))
    custom_product_name = Column(String(200))
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, index=True)
    config = Column(JSONB)  # {"duration": 30, "tone": "premium", "language": "ko", ...}
    script = Column(JSONB)  # {"headline": "...", "subline": "...", ...}

    # Relationships
    user = relationship("User", back_populates="projects")
    product = relationship("Product")
    template = relationship("Template")
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "product": self.product.to_dict() if self.product else None,
            "template": self.template.to_dict() if self.template else None,
            "custom_product_image": self.custom_product_image,
            "custom_product_name": self.custom_product_name,
            "status": self.status.value,
            "config": self.config,
            "script": self.script,
            "videos": [v.to_dict() for v in self.videos] if self.videos else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
