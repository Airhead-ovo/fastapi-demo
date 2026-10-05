from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from models.conversation import Conversation
from models.user import User
from schemas.conversation import ConversationUpdate

def create_conversation(
  db: Session,
  title: str,
  user_id: int,
  project_id: int | None
):
  conversation = Conversation(
    title=title,
    user_id=user_id,
    project_id=project_id
  )

  db.add(conversation)
  db.commit()
  db.refresh(conversation)

  return conversation

def get_conversation_by_id(
  db: Session,
  conversation_id: int
):
  return db.get(Conversation, conversation_id)

def update_conversation_summary(
  db: Session,
  conversation: Conversation,
  summary: str,
  summary_message_id: int
):
  conversation.summary = summary
  conversation.summary_message_id = summary_message_id

  db.commit()
  db.refresh(conversation)

  return conversation

def get_conversations(
  db: Session,
  user_id: int
):
  query = (
    select(Conversation)
    .where(
      Conversation.user_id == user_id,
      Conversation.project_id.is_(None)
    )
    .order_by(
      # asc是升序 从小到大/时间从早到晚 ,  nulls_last是空值放最后
      Conversation.pinned_at.asc().nulls_last(),
      Conversation.updated_at.desc()
    )
  )
  return db.scalars(query).all()

def get_conversations_by_project_id(
  project_id: int,
  db,
  current_user
):
  query = (
    select(Conversation)
    .where(
      Conversation.project_id == project_id,
      Conversation.user_id == current_user.id
    )
    .order_by(
      Conversation.updated_at.desc()
    )
  )
  return db.scalars(query).all()

def update_conversation (
  db: Session,
  data: ConversationUpdate,
  conversation: Conversation
):
  update_data = data.model_dump(
    exclude_unset=True
  )
  for field, value in update_data.items():
    setattr(
      conversation,
      field,
      value
    )
  db.commit()
  db.refresh(conversation)

  return conversation

def delete_conversation (
  db: Session,
  conversation: Conversation
):
  db.delete(conversation)
  db.commit()

def update_conversation_pinned (
  pinned_at: datetime | None,
  conversation,
  db
):
  conversation.pinned_at = pinned_at
  db.commit()
  db.refresh(conversation)
  return conversation

def touch_conversation(
  conversation: Conversation
):
  conversation.updated_at = datetime.now()