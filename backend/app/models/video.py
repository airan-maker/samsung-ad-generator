from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models import Base, TimestampMixin


class Video(Base, TimestampMixin):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1)
    duration = Column(Integer)  # seconds
    resolution = Column(String(20))  # "1080p", "720p", "4k"
    aspect_ratio = Column(String(10))  # "16:9", "9:16", "1:1"
    video_url = Column(String(500))
    thumbnail_url = Column(String(500))
    file_size = Column(BigInteger)  # bytes
    render_time = Column(Integer)  # seconds

    # Relationships
    project = relationship("Project", back_populates="videos")

    def __repr__(self):
        return f"<Video {self.id} v{self.version}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "version": self.version,
            "duration": self.duration,
            "resolution": self.resolution,
            "aspect_ratio": self.aspect_ratio,
            "video_url": self.video_url,
            "thumbnail_url": self.thumbnail_url,
            "file_size": self.file_size,
            "render_time": self.render_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
