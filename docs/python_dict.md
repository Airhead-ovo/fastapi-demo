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

---