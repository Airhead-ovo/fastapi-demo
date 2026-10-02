from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from database import get_db
from schemas.message import (
  MessageResponse,
  MessageCreate,
  MessageUpdate
)
from schemas.conversation import (
  ConversationResponse,
  ConversationUpdate,
  ConversationPinUpdate
)
from models.user import User
from services.auth import get_current_user
from services.message import (
  send_message_stream_service,
  update_message_service
)
from services.conversation import (
  create_conversation_service,
  get_conversations_service,
  get_messages_by_conversation_id_service,
  update_conversation_service,
  delete_conversation_service,
  update_conversation_pinned_service
)

router = APIRouter( 
  prefix="/conversations",
  tags=["Conversations"]
)

# 会話を作成する
@router.post(
  "",
  response_model=ConversationResponse
)
def create_conversation (
  title: str,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  return create_conversation_service(
    db,
    title,
    current_user
  )


@router.post(
  "/{conversation_id}/messages/stream",
)
def stream_message(
  conversation_id: int,
  data: MessageCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  generator =  send_message_stream_service(
    db,
    conversation_id,
    data.content,
    current_user
  )

  return StreamingResponse(
    generator,
    media_type="text/event-stream"
  )

@router.get(
  "",
  response_model=list[ConversationResponse]
)
def get_conversations(
  db: Session = Depends(get_db),
  current_user:User = Depends(get_current_user)
):
  return get_conversations_service(
    db,
    current_user
  )

@router.get(
  "/{conversation_id}/messages",
  response_model=list[MessageResponse]
)
def get_messages_by_conversation_id(
  conversation_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  return get_messages_by_conversation_id_service (
    conversation_id,
    db,
    current_user,
  )

@router.patch(
  "/{conversation_id}",
  response_model=ConversationResponse
)
def update_conversation(
  conversation_id: int,
  data: ConversationUpdate, 
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  return update_conversation_service (
    conversation_id,
    data,
    db,
    current_user
  )

@router.delete(
  "/{conversation_id}",
  status_code = 204
)
def delete_conversation(
  conversation_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  delete_conversation_service(
    conversation_id,
    db,
    current_user
  )

@router.patch(
  "/{conversation_id}/pinned",
  response_model=ConversationResponse 
)
def update_conversation_pinned(
  conversation_id: int,
  data: ConversationPinUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return update_conversation_pinned_service(
    conversation_id,
    data,
    db,
    current_user
  )

@router.patch(
  "/{conversation_id}/messages/{message_id}",
  status_code=204
)
def update_message(
  conversation_id: int,
  message_id: int,
  data: MessageUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return update_message_service(
    conversation_id,
    message_id,
    data,
    db,
    current_user
  ) 