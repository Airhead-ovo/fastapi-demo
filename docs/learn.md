## alembic(アランビック)
alembic revision --autogenerate -m "add status to projects"
alembic upgrade head
alembic current

---

## fastapi分层
路由层 ルーター層
Schema层 スキーマ層
Service层 サービス層／ビジネスロジック層
Crud层 CRUD層 / データアクセス層（DAO層）
Model层　モデル層
Database层　データベース接続層

---

フロントエンド開発を担当しました。
Vue 3を使用して、ファイルアップロード機能を実装しました。
また、APIと連携して、必要な情報を取得する処理も実装しました。


ログイン時にパスワードを検証し、認証に成功した場合はJWTのアクセストークンを発行します。

---

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
### 关闭并删除容器
docker compose down

### 更新到requirements
pip install redis
pip freeze > requirements.txt

### volume负责持久化数据
docker volume ls

### 进入Redis Container
docker compose exec redis redis-cli

---

## SQLAlchemy 对象、Python dict、JSON 字符串
SQLAlchemy对象
    ↓ 手动取字段
Python dict/list
    ↓ json.dumps()
JSON 字符串
    ↓ json.loads()
Python dict / list

### SQLAlchemy对象:
return get_my_projects(
  db=db,
  owner_id=current_user.id
)
 ↓ ↓ ↓ ↓ ↓
Project(
  id=1,
  name="AI Agent",
  description="Agent项目"
)
调用方式: project.id, project.name, project.description

### Python dict
project_dict = {
  "id": project.id,
  "name": project.name,
  "description": project.description,
}
 ↓ ↓ ↓ ↓ ↓
{
  "id": 1,
  "name": "AI Agent",
  "description": "Agent项目"
} 

如果有多个project:
project_list = [
  {
    "id": project.id,
    "name": project.name,
    "description": project.description,
  }
  for project in projects
]
 ↓ ↓ ↓ ↓ ↓
project_list = [
  {"id": 1, "name": "AI Agent"},
  {"id": 2, "name": "Python"}
]
这还不是json字符串 是python list

### json字符串
通过 **json.dumps(project_list)** 把Python对象转换成JSON字符串
**dumps = Python → JSON 字符串**

json字符串: str = '[{"id": 1, "name": "AI Agent"}, {"id": 2, "name": "Python"}]'
**json.loads(str)**
 ↓ ↓ ↓ ↓ ↓
Python list / dict:
  project_list = [
    {"id": 1, "name": "AI Agent"},
    {"id": 2, "name": "Python"}
  ]
**loads =  JSON 字符串 → Python**

---

## AWS
**一个提供云服务器、数据库、文件存储、网络等服务的平台。**

- EC2
→ 跑后端的云服务器

- RDS
→ 托管PostgreSQL / MySQL等数据库

- S3
→ 对象存储: 图片、上传文件、报告等

- ECS
→ 专门跑 Docker Container 的服务
