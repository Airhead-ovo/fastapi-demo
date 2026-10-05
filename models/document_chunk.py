from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text
from pgvector.sqlalchemy import Vector

from database import Base

class DocumentChunk(Base):
  __tablename__ = "document_chunks"

  id: Mapped[int] = mapped_column(
    primary_key = True
  )

  chunk_index: Mapped[int]

  # str 是 Python 类型，Text 是数据库 column type
  content: Mapped[str] = mapped_column(Text)

  embedding: Mapped[list[float]] = mapped_column(
    Vector(1024)
  )

  document_id: Mapped[int] = mapped_column(
    ForeignKey(
      "documents.id",
      ondelete="CASCADE"
    )
  )

  document: Mapped["Document"] = relationship(
    back_populates="document_chunks"
  )

