from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(
    primary_key=True
  )
  email: Mapped[str]
  password_hash: Mapped[str]
  role: Mapped[str] = mapped_column(
    default="user"
  )
  projects: Mapped[list["Project"]] = relationship(
    back_populates="owner"
  )
  conversations: Mapped[list["Conversation"]] = relationship(
    back_populates="user" 
  )
