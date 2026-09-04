from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from datetime import datetime

from database import Base

class Message(Base):
  __tablename__ = "messages"

  id: Mapped[int] = mapped_column(
    primary_key = True
  )

  role: Mapped[str]

  content: Mapped[str]

  conversation_id: Mapped[int] = mapped_column(
    ForeignKey("conversations.id")
  )

  conversations: Mapped["Conversation"] = relationship(
    back_populates="messages"
  )

  created_at: Mapped[datetime] = mapped_column(
    server_default = func.now()
  )