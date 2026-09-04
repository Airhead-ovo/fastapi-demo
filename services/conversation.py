from sqlalchemy.orm import Session

from models.user import User
from crud.conversation import create_conversation

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