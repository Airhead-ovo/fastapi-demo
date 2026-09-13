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
from utils.sse import sse_event

logger = logging.getLogger(__name__)

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


# 簡単なstream
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
      detail="指定されたConversationが見つかりません"
    )
  
  if conversation.user_id != current_user.id:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      # 　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　けんげん
      detail="このConversationにアクセスする権限はありません"
    )

  # まずユーザーメッセージをdbに保存する
  create_message(
    db,
    conversation_id,
    "user",
    content
  )

  # 直近（ちょっきん）２０件の会話歴史を取得して　　LLMに渡す
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

  # SQLAlchemy Messageはdictに変換する
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

# 普通版本的 不带流式的
def send_message_service(
    db: Session,
    conversation_id: int,
    content: str,
    current_user: User
):
    conversation = get_conversation_by_id(
        db,
        conversation_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="指定されたConversationが見つかりません"
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="このConversationにアクセスする権限がありません"
        )

    # 1️⃣ ユーザーのメッセージを保存
    create_message(
        db,
        conversation_id,
        "user",
        content
    )

    # 2️⃣ LLMに渡す会話履歴を取得
    db_messages = get_recent_messages(
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

    MAX_TOOL_STEPS = 5

    # 3️⃣ Agent Loop
    for step in range(MAX_TOOL_STEPS):

        ai_message = chat_with_tools(
            messages
        )

        # Tool Callがない → 最終回答
        if not ai_message.tool_calls:

            assistant_message = create_message(
                db,
                conversation_id,
                "assistant",
                ai_message.content
            )

            update_conversation_summary_service(
                db,
                conversation
            )

            return assistant_message

        # assistantのTool Call情報を履歴に追加
        messages.append(
            ai_message.model_dump()
        )

        # 4️⃣ Tool Callを処理
        for tool_call in ai_message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
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

            # Tool実行結果をLLMの履歴に追加
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
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
  
