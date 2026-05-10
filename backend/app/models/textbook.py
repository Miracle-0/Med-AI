from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ParseStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"

class Textbook(Base):
    __tablename__ = "textbooks"

    textbook_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    title = Column(String, nullable=False)
    format = Column(String, nullable=False)
    total_pages = Column(Integer, default=0)
    total_chars = Column(Integer, default=0)
    upload_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    parse_status = Column(String, default=ParseStatus.UPLOADED)

    chapters = relationship("Chapter", back_populates="textbook", cascade="all, delete-orphan")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="textbook", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="textbook", cascade="all, delete-orphan")
