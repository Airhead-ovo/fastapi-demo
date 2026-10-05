from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text
from datetime import datetime
from sqlalchemy.sql import func

from database import Base

class Document(Base):
  __tablename__ = "documents"

  id: Mapped[int] = mapped_column(
    primary_key = True
  )

  filename: Mapped[str]

  file_path: Mapped[str]

  file_size: Mapped[int]

  document_chunks: Mapped[list["DocumentChunk"]] = relationship(
    back_populates="document",
    cascade="all, delete-orphan" 
  )

  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id")
  )

  user: Mapped["User"] = relationship(
    back_populates="documents"
  )

  project_id: Mapped[int] = mapped_column(
    ForeignKey("projects.id")
  )

  project: Mapped["Project"] = relationship(
    back_populates="documents"
  )

  created_at: Mapped[datetime] = mapped_column(
    server_default = func.now()
  )