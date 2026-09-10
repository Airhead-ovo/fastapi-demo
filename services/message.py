from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json

from crud.message import (
  create_message,
  get_recent_messages
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
  db_messages = get_recent_messages(
    db,
    conversation_id,
    limit=20
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

  while True:
    # 3️⃣　LLMを呼び出す
    ai_message = chat_with_tools(messages)

    #  Tool Callがない → 最終回答
    if not ai_message.tool_calls:
      assistant_message = create_message(
        db,
        conversation_id,
        "assistant",
        ai_message.content
      )

      return assistant_message

    # tool_call がある
    messages.append(
      ai_message.model_dump()
    )

    # tool Callを処理する
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
          
    messages.append({
      "role": "tool",
      "tool_call_id": tool_call.id,
      "content": json.dumps(
        result,
        ensure_ascii=False,
        default=str
      )
    })


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

  db_messages = get_recent_messages(
    db,
    conversation_id,
    limit=20
  )

  messages = []

  if conversation.summary:
    messages.append({
      "role": "system",
      "content":(
        "これまでの会話の要約：\n"
        + conversation.summary
      )
    })

    print("summary", conversation.summary)

    messages.extend([
      {
        "role": message.role,
        "content": message.content
      }
      for message in db_messages
    ])

  messages = [
    {
        "role": message.role,
        "content": message.content
    }
    for message in db_messages
  ]
  print("messages", messages)

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

  