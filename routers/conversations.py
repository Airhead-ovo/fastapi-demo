from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db

from schemas.message import (
  MessageResponse,
  MessageCreate
)
from schemas.conversation import (
  ConversationResponse
)
from models.user import User
from services.auth import get_current_user
from services.message import send_message_service
from services.conversation import create_conversation_service

router = APIRouter( 
  prefix="/conversations",
  tags=["Conversations"]
)

# aiにメッセじを送信する
@router.post(
  "/{conversation_id}/messages",
  response_model=MessageResponse
)
def send_message(
  conversation_id: int,
  data: MessageCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return send_message_service(
    db,
    conversation_id,
    data.content,
    current_user
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

# POST /conversations

# chatメッセージを取得する
# GET /conversations/{conversation_id}/messages