from schemas.task import TaskCreate
from services.task import (
  create_task_service,
  get_tasks_service
)

def create_task_tool(
  db,
  current_user,
  project_id: int,
  title: str,
  description: str | None = None
):
  task_data = TaskCreate(
    title=title,
    description=description
  )
  task = create_task_service(
    db,
    project_id,
    task_data,
    current_user
  )
  return {
    "id": task.id,
    "title": task.title,
    "status": task.status,
    "project_id": task.project_id
  }

def get_tasks_tool(
  db,
  current_user,
  project_id: int,
  status: str | None = None,
  keyword: str | None = None
):
  result = get_tasks_service(
    db,
    project_id,
    current_user,
    status,
    keyword,
    page=1,
    page_size=100
  )

  tasks = result["items"]

  return {
    "total": result["total"],
    "tasks": [
      {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "project_id": task.project_id
      }
      for task in tasks
    ]
  }


TOOL_REGISTRY = {
  "create_task": create_task_tool,
  "get_tasks": get_tasks_tool
}