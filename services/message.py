from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json
import logging

from crud.message import (
  create_message,
  get_recent_messages
)
from models.user import User
from models.conversation import Conversation
from clients.llm_client import (
  stream_chat_with_llm,
  chat_with_tools,
  summarize_conversation
)
from crud.conversation import (
  get_conversation_by_id,
  update_conversation_summary
)
from tools.task_tools import (
  TOOL_REGISTRY,
  TOOL_SCHEMA_REGISTRY
)
from crud.message import (
  get_unsummarized_messages
)

logger = logging.getLogger(__name__)

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
      detail="このconversationにアクセスする権限はありません"
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

  MAX_TOOL_STEPS = 5  # 無限ループを防ぐために、tool実行回数に上限を設ける
  for step in range(MAX_TOOL_STEPS):
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

      update_conversation_summary(
        db,
        conversation
      )

      print(
        "Tool loop finished: final_answer=%r",
        ai_message.content
      )
      return assistant_message

    # tool_call がある
    messages.append(
      ai_message.model_dump()# 把Pydantic basemodel变成普通对象dict
    )

    # tool Callを処理する
    for tool_call in ai_message.tool_calls:
      tool_name = tool_call.function.name

      arguments = json.loads(
        tool_call.function.arguments
      )
      
      # tool_schema = TOOL_SCHEMA_REGISTRY.get(tool_name)
      # validated = tool_schema(
      #   **arguments
      # )

      print(
        "Tool requested: name=%s, call_id=%s, arguments=%s",
        tool_name,
        tool_call.id,
        arguments
      )

      tool_function = TOOL_REGISTRY.get(tool_name)

      if tool_function is None:
        raise HTTPException(
          status_code=400,
          detail="指定されたToolは存在しません"
        )

      try:
        result = tool_function(
          db,
          current_user,
          **arguments
        )
      except HTTPException as e:
        result = {
          "success": False,
          "status_code": e.status_code,
          "error": e.detail
        }
          
      messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(
          result,
          ensure_ascii=False,
          default=str
        )
      })

  raise HTTPException(
    status_code=500,
    detail="Toolの実行回数が上限を超えました"
  )


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

def update_conversation_summary(
  db: Session,
  conversation: Conversation
):
  old_messages = get_unsummarized_messages(
    db,
    conversation.id,
    conversation.summary_message_id
  )

  if len(old_messages) < 40:
    return

  summary_messages = [
    {
      "role": message.role,
      "content": message.content
    }
    for message in old_messages
  ]

  new_summary = summarize_conversation(
    conversation.summary,
    summary_messages
  )

  return update_conversation_summary(
    db,
    conversation,
    new_summary,
    old_messages[-1].id # old_messages[-1]はlistで最後のメッセージ
  )
  
