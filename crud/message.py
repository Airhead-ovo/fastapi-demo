from sqlalchemy.orm import Session
from sqlalchemy import select, func, delete

from models.message import Message

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
  db.flush()
  db.refresh(message)

  return message

def get_messages(
  db: Session,
  conversation_id: int
):
  query = (
    select(Message)
    .where(Message.conversation_id == conversation_id)
  )

  return db.scalars(query).all()

def get_recent_messages(
  db: Session,
  conversation_id: int,
  limit: int = 20
):
  query = (
    select(Message)
    .where(
      Message.conversation_id == conversation_id
    )
    .order_by(
      Message.created_at.asc()
    )
    .limit(limit)
  )

  return db.scalars(query).all()

def get_unsummarized_messages(
  db: Session,
  conversation_id: int,
  summary_message_id: int | None,
  limit: int = 20
):
  query = (
    select(Message)
    .where(
      Message.conversation_id == conversation_id
    )
    .order_by(
      Message.id.asc()
    )
  )

  if summary_message_id is not None:
    query = query.where(
      Message.id > summary_message_id
    )

  query = query.limit(limit)
  
  return db.scalars(query).all()


def get_message_by_id(
  message_id: int,
  db: Session,
):
  query = (
    select(Message)
    .where(
      Message.id == message_id
    )
  )
  return db.scalar(query)


# 删除需要修改的message之后的所有问答
def delete_messages_from(
  message: Message,
  db: Session
):
  stmt = (
    delete(Message)
    .where(
      Message.conversation_id == message.conversation_id,
      Message.id >= message.id
    )
  )
  db.execute(stmt)