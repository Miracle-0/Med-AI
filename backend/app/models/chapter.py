from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Chapter(Base):
    __tablename__ = "chapters"

    chapter_id = Column(String, primary_key=True, index=True)
    textbook_id = Column(String, ForeignKey("textbooks.textbook_id"), nullable=False)
    title = Column(String, nullable=False)
    page_start = Column(Integer, nullable=False)
    page_end = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    char_count = Column(Integer, default=0)

    textbook = relationship("Textbook", back_populates="chapters")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="chapter", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="chapter", cascade="all, delete-orphan")
