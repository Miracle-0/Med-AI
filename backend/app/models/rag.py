from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Chunk(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String, primary_key=True, index=True)
    textbook_id = Column(String, ForeignKey("textbooks.textbook_id"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.chapter_id"), nullable=False)
    page = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    textbook = relationship("Textbook", back_populates="chunks")
    chapter = relationship("Chapter", back_populates="chunks")
