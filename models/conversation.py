from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text
from sqlalchemy.sql import func
from datetime import datetime

from database import Base

class Conversation(Base):
  __tablename__ = "conversations"

  id: Mapped[int] = mapped_column(
    primary_key = True
  )

  title: Mapped[str]

  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id")
  )

  user: Mapped["User"] = relationship(
    back_populates="conversations"
  )

  messages: Mapped[list["Message"]] = relationship(
    back_populates="conversations"
  )

  summary: Mapped[str | None] = mapped_column(
    Text,
    nullable=True
  )

  summary_message_id: Mapped[int | None] = mapped_column(
    nullable=True
  )

  created_at: Mapped[datetime] = mapped_column(
    server_default = func.now()
  )

  updated_at: Mapped[datetime] = mapped_column(
    server_default = func.now(),
    onupdate = func.now()
  )