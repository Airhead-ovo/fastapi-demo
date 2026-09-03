from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from enum import Enum
from datetime import datetime
from sqlalchemy.sql import func

from database import Base

class Task(Base):
  __tablename__ = "tasks"

  id: Mapped[int] = mapped_column(
    primary_key=True
  )
  title: Mapped[str]
  description: Mapped[str | None]
  status: Mapped[str] = mapped_column(
    default="todo"
  )
  project_id: Mapped[int] = mapped_column(
    ForeignKey("projects.id")
  )
  project: Mapped["Project"] = relationship(
    back_populates="tasks"
  )
  created_at: Mapped[datetime] = mapped_column(
    server_default=func.now()
  )
  updated_at: Mapped[datetime] = mapped_column(
    server_default=func.now(),
    onupdate=func.now()
  ) 

class TaskStatus(str, Enum):
  TODO = "todo"
  DOING = "doing"
  DONE = "done"