from sqlalchemy.orm import Session

from models.user import User
from crud.conversation import (
  create_conversation,
  get_conversations
)

def create_conversation_service(
  db: Session,
  title: str,
  current_user: User
):
  return create_conversation(
    db,
    title,
    current_user.id
  )

def get_conversations_service(
  db: Session,
  current_user: User
):
  return get_conversations(
    db,
    current_user.id
  )