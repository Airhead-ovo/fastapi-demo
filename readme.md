# 操作
## 先激活虚拟环境  前面带了(.venv)就对了
source .venv/bin/activate
## 启动项目
uvicorn main:app --reload
## 接口文档链接 
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc

# AI Agent Demo
FastAPI + Vue + PostgreSQL + Redis + Qwen を使用した
AI Agent チャットアプリケーションです。

## Features

- AIチャット
- SSEによるストリーミングレスポンス
- 会話履歴の保存
- Project / Task管理
- Tool CallingによるProject / Task操作
- PostgreSQLによるデータ永続化
- Redisによるキャッシュ
- Docker Composeによる開発環境構築

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Qwen API

### Infrastructure

- Docker
- Docker Compose

## Setup

### 1. Clone

```bash
git clone <repository-url>
cd fastapi-demo
```

### 2.start
```
docker compose up -d --build
```
起動状態を確認
```
docker compose ps
```
ログを確認
```
docker compose logs -f api
```
