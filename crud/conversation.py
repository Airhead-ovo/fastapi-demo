from sqlalchemy.orm import Session
from models.conversation import Conversation

def create_conversation(
  db: Session,
  title: str,
  user_id: int
):
  conversation = Conversation(
    title=title,
    user_id=user_id
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