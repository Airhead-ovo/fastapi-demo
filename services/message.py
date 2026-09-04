from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.message import (
  create_message,
  get_messages
)
from models.user import User
from clients.llm_client import chat_with_llm
from crud.conversation import get_conversation_by_id

def send_message_service(
  db: Session,
  conversation_id: int,
  content: str,
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
      # 　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　けんげん
      detail="このconversationをアクセスする権限はありません"
    )
  
  # 1️⃣ユーザーのメッセージを保存する
  create_message(
    db,
    conversation_id,
    "user",
    content
  )

  # 2️⃣歴史メッセージを取得して 　　LLMが必要とする形式に変換する
  db_messages = get_messages(
    db,
    conversation_id
  )
  messages = [
    {
      "role": message.role,
      "content": message.content
    }
    for message in db_messages
  ] # リスト内包表記 　　ないほうひょうき

  # 3️⃣大模型を呼び出す　　　　だいもけい
  reply = chat_with_llm(messages)

  # 4️⃣aiの回答を保存する
  create_message(
    db,
    conversation_id,
    "assistant",
    reply
  )

  return {
    "id": current_user.id,
    "role": "assistant",
    "conversation_id": conversation_id,
    "content": reply
  }



  