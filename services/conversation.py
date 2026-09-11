from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from crud.conversation import (
  create_conversation,
  get_conversations,
  get_conversation_by_id
)
from crud.message import get_messages

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

def get_messages_by_conversation_id_service(
  conversation_id: int,
  db: Session,
  current_user: User
):
  conversation = get_conversation_by_id(db, conversation_id)
  if conversation is None:
    raise HTTPException(
      status_code=404,
      detail="conversationが見つかりません"
    )
  if conversation.user_id != current_user.id:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="このconversationにアクセスする権限はありません"
    )
  return get_messages(
    db,
    conversation_id
  )