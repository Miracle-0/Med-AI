from sqlalchemy import Column, String, Integer, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RelationType(str, enum.Enum):
    PREREQUISITE = "prerequisite"
    PARALLEL = "parallel"
    CONTAINS = "contains"
    APPLIES_TO = "applies_to"

class MergeAction(str, enum.Enum):
    MERGE = "merge"
    KEEP = "keep"
    REMOVE = "remove"

class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    node_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    definition = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    textbook_id = Column(String, ForeignKey("textbooks.textbook_id"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.chapter_id"), nullable=False)
    page = Column(Integer, nullable=False)

    textbook = relationship("Textbook", back_populates="knowledge_nodes")
    chapter = relationship("Chapter", back_populates="knowledge_nodes")
    source_edges = relationship("KnowledgeEdge", foreign_keys="KnowledgeEdge.source_node_id", back_populates="source_node")
    target_edges = relationship("KnowledgeEdge", foreign_keys="KnowledgeEdge.target_node_id", back_populates="target_node")

class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    edge_id = Column(String, primary_key=True, index=True)
    source_node_id = Column(String, ForeignKey("knowledge_nodes.node_id"), nullable=False)
    target_node_id = Column(String, ForeignKey("knowledge_nodes.node_id"), nullable=False)
    relation_type = Column(String, nullable=False)
    description = Column(Text)

    source_node = relationship("KnowledgeNode", foreign_keys=[source_node_id], back_populates="source_edges")
    target_node = relationship("KnowledgeNode", foreign_keys=[target_node_id], back_populates="target_edges")

class MergeDecision(Base):
    __tablename__ = "merge_decisions"

    decision_id = Column(String, primary_key=True, index=True)
    action = Column(String, nullable=False)
    affected_nodes = Column(Text, nullable=False)
    result_node_id = Column(String)
    reason = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
