from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json
import logging

from crud.message import (
  create_message,
  get_recent_messages,
  get_message_by_id,
  delete_messages_from,
)
from crud.conversation import touch_conversation
from models.user import User
from models.conversation import Conversation
from clients.llm_client import (
  stream_chat_with_llm,
  chat_with_tools,
  summarize_conversation,
  stream_chat_with_tools
)
from crud.conversation import (
  get_conversation_by_id,
  update_conversation_summary
)
from tools.task_tools import (
  TOOL_REGISTRY
)
from crud.message import (
  get_unsummarized_messages
)
from services.conversation import get_conversation_by_id_service
from utils.sse import sse_event

logger = logging.getLogger(__name__)

# 业务在使用的 
def send_message_stream_service(
  db: Session,
  conversation_id: int,
  content: str,
  current_user: User
):
  logger.info(
    "Agent request received conversation_id=%s user_id=%s",
    conversation_id,
    current_user.id
  ) 

  # conversationと権限を確認
  conversation = get_conversation_by_id(db, conversation_id)
  if conversation is None:
    raise HTTPException(
      status_code=404,
      detail="指定されたconversationが見つかりません"
    )
  if conversation.user_id != current_user.id:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      # 　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　けんげん
      detail="このconversationにアクセスする権限はありません"
    )
  
  # まずユーザーメッセージをdbに保存する
  create_message(
    db,
    conversation_id,
    "user",
    content
  )

  touch_conversation(
    conversation
  )

  db.commit()

  # 直近（ちょっきん）２０件の会話歴史を取得して　　LLMに渡す
  db_messages = get_recent_messages(
    db,
    conversation_id,
    limit=20
  )
  # SQLAlchemy Messageはdictに変換する
  messages = [
    {
      "role": message.role,
      "content": message.content
    }
    for message in db_messages
  ] # リスト内包表記 　　ないほうひょうき

  MAX_TOOL_STEPS = 5  # 無限ループを防ぐために、tool実行回数に上限を設ける
  for step in range(MAX_TOOL_STEPS):
    tool_calls_buffer = {}
    full_content = ""

    #　LLMをストリーミングで呼び出す
    stream = stream_chat_with_tools(messages)

    # LLMのレスポンスをchunk単位で受け取る
    for chunk in stream:

      # choicesが空のchunkはスキップする
      if not chunk.choices:
        continue

      delta = chunk.choices[0].delta
      # 1️⃣　普通の回答を受け取る　：　deltaに追加して　すぐフロントへ送信
      if delta.content:
        full_content += delta.content # db保存用に

        yield sse_event(
          "content",
          {
            "content": delta.content # フロントエンドへ逐次送信　ちくじ　そうしん
          }
        )
      #　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　ぶんかつ 　　　　　　　　　　　　　　　　　　　　　　　けつごう
      #　2️⃣ tool　callを受け取る　：分割されたtool callを結合
      if delta.tool_calls:

        for tool_call in delta.tool_calls:

          index = tool_call.index

          if index not in tool_calls_buffer:
            tool_calls_buffer[index] = {
              "id": tool_call.id,
              "name": "",
              "arguments": ""
            }

          if tool_call.id:
            tool_calls_buffer[index]["id"] = (
              tool_call.id
            )

          if tool_call.function.name:
            tool_calls_buffer[index]["name"] += (
              tool_call.function.name
            )
          
          if tool_call.function.arguments:
            tool_calls_buffer[index]["arguments"] += (
              tool_call.function.arguments
            )

    #  Tool Callがなくなる → 最終回答
    if not tool_calls_buffer:

      create_message(
        db,
        conversation_id,
        "assistant",
        full_content
      )
      touch_conversation(
        conversation
      )
      db.commit()


      # summaryを更新
      update_conversation_summary_service(
        db,
        conversation
      )

      # ストリーム終了を通知
      yield sse_event(
        "done",
        {}
      )
      return # Generatorが終了
    
    # tool callがある
    # tool callをassistant　messageとして歴史に追加
    assistant_tool_calls = []

    for tool_data in tool_calls_buffer.values():
      assistant_tool_calls.append(
        {
          "type": "function",
          "id": tool_data["id"],
          "function": {
            "name": tool_data["name"],
            "arguments": tool_data["arguments"]
          }
        }
      )

    messages.append(
      {
        "role": "assistant",
        "content": None,
        "tool_calls": assistant_tool_calls
      }
    )

    # toolを実行
    for tool_data in tool_calls_buffer.values():

      tool_name = tool_data["name"]

      arguments = json.loads(
        tool_data["arguments"]
      )
      
      logger.info(
        "Tool execution started tool=%s conversation_id=%s",
        tool_name,
        conversation_id
      )
    
      yield sse_event(
        "tool_start",
        {
          "tool_name": tool_name
        }
      )
    
      tool_function = TOOL_REGISTRY.get(
        tool_name
      )
    
      if tool_function is None:
        raise HTTPException(
          status_code=400,
          detail="指定されたToolは存在しません"
        )
      
      try:
        if tool_name == "knowledge_search":
          result = tool_function(
            db,
            current_user,
            conversation_id=conversation_id,
            **arguments
          )
        else:
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
    
      yield sse_event(
        "tool_end",
        {
          "tool_name": tool_name
        }
      )

      # Toolの実行結果を履歴に追加
      messages.append(
        {
          "role": "tool",
          "tool_call_id": tool_data["id"],
          "content": json.dumps( # 变成字符串
            result,
            ensure_ascii=False,
            default=str
          )
        }
      )

  raise HTTPException(
    status_code=500,
    detail="Toolの実行回数が上限を超えました"
  )

def update_conversation_summary_service(
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
  
def update_message_service (
  conversation_id,
  message_id,
  data,
  db,
  current_user
):
  try:
    conversation = get_conversation_by_id_service(
      conversation_id, 
      db, 
      current_user
    )
      
    message = get_message_by_id(message_id, db)
    if message is None:
      raise HTTPException(
        status_code=404,
        detail="messageが見つかりません"
      )
    if message.conversation_id != conversation.id:
      raise HTTPException(
        status_code=404,
        detail="messageが見つかりません"
      )
    if message.role != "user":
      raise HTTPException(
        status_code=403,
        detail="'assistant'のメッセージを変更する権限がない"
      )

    delete_messages_from(
      message,
      db
    )

    # 清空摘要
    conversation.summary = None
    conversation.summary_message_id = None

    touch_conversation(conversation)

    db.commit()

  except Exception:
    db.rollback()
    raise