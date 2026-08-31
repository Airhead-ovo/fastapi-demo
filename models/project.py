from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from database import Base

class Project(Base):
  __tablename__ = "projects"

  id: Mapped[int] = mapped_column(
    primary_key=True
  )
  name: Mapped[str]
  description: Mapped[str | None]
  owner_id: Mapped[int] = mapped_column(
    ForeignKey("users.id")
  )
  owner: Mapped["User"] = relationship(
    back_populates="projects"
  )
  status: Mapped[str] = mapped_column(
    default="active"
  )
  tasks: Mapped[list["Task"]] = relationship(
    back_populates="project"
  )