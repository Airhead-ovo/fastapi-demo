from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from models.user import User
from crud.conversation import (
  create_conversation,
  get_conversations,
  get_conversation_by_id,
  get_conversations_by_project_id,
  update_conversation,
  delete_conversation,
  update_conversation_pinned,
  change_conversation_to_project,
  change_document_to_project
)
from schemas.conversation import (
  ConversationUpdate,
  ConversationPinUpdate
)
from crud.message import (
  get_messages,
)
from services.project import (
  get_project_service
)

def create_conversation_service(
  db: Session,
  title: str,
  current_user: User,
  project_id: int | None = None
):
  if project_id is not None:
    get_project_service(db, current_user, project_id)

  return create_conversation(
    db,
    title,
    current_user.id,
    project_id
  )

def get_conversations_service(
  db: Session,
  current_user: User
):
  return get_conversations(
    db,
    current_user.id
  )
def get_conversations_by_project_id_service(
  project_id: int,
  db: Session,
  current_user: User
):
  get_project_service(db, current_user, project_id)

  return get_conversations_by_project_id(
    project_id,
    db,
    current_user
  )
# 校验 conversation
def get_conversation_by_id_service(
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
  return conversation
  
def get_messages_by_conversation_id_service(
  conversation_id: int,
  db: Session,
  current_user: User
):
  conversation = get_conversation_by_id_service(conversation_id, db, current_user)
  return get_messages(
    db,
    conversation.id
  )

def update_conversation_service (
  conversation_id: int,
  data: ConversationUpdate,
  db: Session,
  current_user: User
):
  conversation = get_conversation_by_id_service(conversation_id, db, current_user)
  return update_conversation(
    db,
    data,
    conversation
  )

def delete_conversation_service(
  conversation_id: int,
  db: Session,
  current_user: User
):
  conversation = get_conversation_by_id_service(conversation_id, db, current_user)
  delete_conversation(
    db,
    conversation
  )

def update_conversation_pinned_service (
  conversation_id: int,
  data: ConversationPinUpdate,
  db: Session,
  current_user: User
): 
  conversation = get_conversation_by_id_service(conversation_id, db, current_user)
  pinned_at = datetime.now() if data.is_pinned else None
  return update_conversation_pinned(
    pinned_at,
    conversation, 
    db
  )

def change_conversation_to_project_servie(
  conversation_id,
  project_id,
  db,
  current_user
):
  try:

    conversation = get_conversation_by_id_service(conversation_id, db, current_user)

    if conversation.project_id is not None:
      raise HTTPException(
        status_code=400,
        detail="无法移动已有项目的对话"
      )

    project = get_project_service(db, current_user, project_id)

    for document in conversation.documents:
      change_document_to_project(
        document,
        project
      )

    change_conversation_to_project(
      conversation,
      project,
    )

    db.commit()

  except Exception:
    db.rollback()
    raise
