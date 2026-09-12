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


## docker
### build image 创建镜像
docker build -t fastapi-demo .

### 通过镜像启动容器
docker run -p 8000:8000 fastapi-demo

### 查看运行的docker
docker ps

### 停止docker运行
docker stop c64f8ce47206

### 启动 compose.yaml 里的服务 启动前重新 build Image
docker compose up --build
### 关闭服务
docker compose down

docker volume ls