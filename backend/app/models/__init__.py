from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func
from uuid import uuid4


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


from app.models.user import User
from app.models.product import Product
from app.models.template import Template
from app.models.project import Project
from app.models.video import Video
from app.models.payment import Payment

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Product",
    "Template",
    "Project",
    "Video",
    "Payment",
]
