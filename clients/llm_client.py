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