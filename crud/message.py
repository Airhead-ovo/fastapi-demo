from sqlalchemy.orm import Session
from sqlalchemy import select, func

from models.message import Message
from models.conversation import Conversation

def create_message(
  db: Session,
  conversation_id: int,
  role: str,
  content: str
):
  message = Message(
    conversation_id=conversation_id,
    role=role,
    content=content
  )

  db.add(message)
  db.commit()
  db.refresh(message)

  return message

def get_messages(
  db: Session,
  conversation_id: int
):
  query = select(Message).where(
      Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())

  return db.scalars(query).all()