from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json

from crud.message import (
  create_message,
  get_messages
)
from models.user import User
from clients.llm_client import (
  chat_with_llm,
  stream_chat_with_llm,
  chat_with_tools
)
from schemas.task import (
  TaskCreate
)
from crud.conversation import get_conversation_by_id
from services.task import create_task_service
from tools.task_tools import TOOL_REGISTRY

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

  # # 3️⃣大模型を呼び出す　　　　だいもけい
  # reply = chat_with_llm(messages)

  # # 4️⃣aiの回答を保存する
  # create_message(
  #   db,
  #   conversation_id,
  #   "assistant",
  #   reply
  # )

  # return {
  #   "id": current_user.id,
  #   "role": "assistant",
  #   "conversation_id": conversation_id,
  #   "content": reply
  # }

  # 3️⃣　LLMを呼び出す
  ai_message = chat_with_tools(messages)

  # tool_call があるか確認する
  if ai_message.tool_calls:
    tool_call = ai_message.tool_calls[0]
    tool_name = tool_call.function.name

    arguments = json.loads(
      tool_call.function.arguments
    )

    tool_function = TOOL_REGISTRY.get(tool_name)

    if tool_function is None:
      raise HTTPException(
          status_code=400,
          detail="指定されたToolは存在しません"
      )

    result = tool_function(
      db,
      current_user,
      **arguments
    )
          
    messages.append(
      ai_message.model_dump()
    )
    messages.append({
      "role": "tool",
      "tool_call_id": tool_call.id,
      "content": json.dumps(
        result,
        ensure_ascii=False,
        default=str
      )
    })
    final_message = chat_with_tools(messages)
    assistant_message = create_message(
      db,
      conversation_id,
      "assistant",
      final_message.content
    )

    return assistant_message

  # 没有 tool_calls 的普通聊天
  assistant_message = create_message(
    db,
    conversation_id,
    "assistant",
    ai_message.content
  )

  return assistant_message


def stream_message_service(
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

  create_message(
    db,
    conversation_id,
    "user",
    content
  )

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
  ]

  full_reply = ""
  for chunk in stream_chat_with_llm(messages):
    full_reply += chunk
    yield f"data: {chunk}\n\n"

  create_message(
      db,
      conversation_id,
      "assistant",
      full_reply
  )

  