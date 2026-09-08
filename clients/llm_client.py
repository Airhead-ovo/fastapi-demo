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
    }
]

def chat_with_tools(messages):
    response = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message
