from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

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
