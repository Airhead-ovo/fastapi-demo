# llm_clientは外部のLLM APIとの通信を担当する

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://ws-l7s59gws13dh95vm.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)

def chat_with_llm(messages):
    response = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=messages
    )

    return response.choices[0].message.content

def stream_chat_with_llm(messages):
    stream = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=messages,
        stream=True
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content

        if content:
            yield content


tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "指定したProjectに新しいTaskを作成する",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "Taskを作成するProjectのID"
                    },
                    "title": {
                        "type": "string",
                        "description": "Taskのタイトル"
                    },
                    "description": {
                        "type": "string",
                        "description": "Taskの説明"
                    }
                },
                "required": [
                    "project_id",
                    "title"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "指定したProjectのTask一覧を取得する",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "Task一覧を取得するProjectのID"
                    },
                    "status": {
                        "type": "string",
                        "description": "Taskのステータス",
                        "enum": ["todo", "doing", "done"]
                    }
                },
                "required": ["project_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "指定したTaskの情報を更新する",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "ProjectのID"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "更新対象TaskのID"
                    },
                    "title": {
                        "type": "string",
                        "description": "Taskのタイトル"
                    },
                    "description": {
                        "type": "string",
                        "description": "Taskの説明"
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "todo",
                            "doing",
                            "done"
                        ]
                    }
                },
                "required": [
                    "project_id",
                    "task_id"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_projects",
            "description": "ログインユーザーが所有するproject一覧を取得する",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "新しいprojectを作成する",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "projectのタイトル"
                    },
                    "description": {
                        "type": "string",
                        "description": "projectの説明"
                    }
                },
                "required": [
                    "name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_project",
            "description": "指定されたprojectを変更する",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "projectのid"  
                    },
                    "name": {
                        "type": "string",
                        "description": "projectのタイトル"
                    },
                    "description": {
                        "type": "string",
                        "description": "projectの説明"
                    }
                },
                "required": [
                    "project_id"
                ]
            }
        }
    }
]

def chat_with_tools(messages):
    request_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *messages
    ]
    response = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=request_messages,
        tools=tools
    )
    return response.choices[0].message

def stream_chat_with_tools(messages):
    request_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *messages
    ]
    response = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=request_messages,
        tools=tools,
        stream=True
    )
    return response

SYSTEM_PROMPT = """
    あなたはTask管理システムを操作するAIアシスタントです。

    以下のルールを必ず守ってください。

    1. Taskを更新する際、task_idが不明な場合は、
        まずget_tasksを使用して対象Taskを特定してください。

    2. Project IDやTask IDが不明な場合は推測しないでください。

    3. Toolの実行結果だけを事実として扱ってください。

    4. Toolの実行に必要な情報が不足している場合は、
        ユーザーに確認してください。

    5. Taskの作成・取得・更新には、
        利用可能なToolを使用してください。

    ６. 現在のユーザーメッセージを最優先で処理してください。

    ７. 過去の会話で依頼された操作を、
        現在のユーザーが明示的に依頼していない限り、
        再実行しないでください。

    ８. 各ターンでは、現在のユーザーメッセージから必要な操作を判断してください。
"""

def summarize_conversation(
    old_summary: str | None,
    messages: list
):
    prompt = f"""
        以下の会話内容を簡潔に要約してください。

        以前の要約：
        {old_summary or "なし"}

        新しい会話：
        {messages}

        今後の会話で必要になる情報を残してください。
        特に、Project、Task、ユーザーの依頼内容、
        すでに完了した操作を優先してください。
    """

    response = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content