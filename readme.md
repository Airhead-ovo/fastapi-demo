### 操作
## 先激活虚拟环境  前面带了(.venv)就对了
source .venv/bin/activate
## 启动项目
uvicorn main:app --reload
## 接口文档链接 
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc

## alembic(アランビック)
alembic revision --autogenerate -m "add status to projects"
alembic upgrade head
alembic current

### fastapi分层
路由层 ルーター層
Schema层 スキーマ層
Service层 サービス層／ビジネスロジック層
Crud层 CRUD層 / データアクセス層（DAO層）
Model层　モデル層
Database层　データベース接続層



フロントエンド開発を担当しました。
Vue 3を使用して、ファイルアップロード機能を実装しました。
また、APIと連携して、必要な情報を取得する処理も実装しました。


ログイン時にパスワードを検証し、認証に成功した場合はJWTのアクセストークンを発行します。
