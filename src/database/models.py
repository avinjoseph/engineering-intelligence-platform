from datetime import datetime
from time import timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    title = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship to DocumentChunk
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # Assuming 768 dimensions for the embedding
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tsv = Column(
        TSVECTOR,
        Computed("to_tsvector('english', chunk_text)", persisted=True),
    )
    # Relationship to Document
    document = relationship("Document", back_populates="chunks")
    
    __table_args__ = (
        Index("chunks_tsv_idx", "tsv", postgresql_using="gin"),
        Index("chunks_embedding_idx",
              "embedding",
              postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )