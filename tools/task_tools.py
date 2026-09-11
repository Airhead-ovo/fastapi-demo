from services.task import (
  create_task_service,
  get_tasks_service,
  update_task_service
)
from services.project import (
  get_my_projects_service,
  create_project_service,
  update_project_service
)
from schemas.task import (
  TaskUpdate,
  TaskCreate
)
from schemas.project import (
  ProjectCreate,
  ProjectUpdate
)
from schemas.tool import (
  CreateProjectToolArgs,
  GetProjectsToolArgs
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

def update_task_tool(
  db,
  current_user,
  project_id,
  task_id,
  title: str | None = None,
  description: str | None = None,
  status: str | None = None
):
  update_data = {}
  if title is not None:
    update_data['title'] = title

  if description is not None:
    update_data['description'] = description

  if status is not None:
    update_data['status'] = status

  task_data = TaskUpdate(
    **update_data
  )

  task = update_task_service(
    db,
    current_user,
    task_data,
    project_id,
    task_id
  )
  
  return {
    "id": task.id,
    "title": task.title,
    "description": task.description,
    "status": task.status,
    "project_id": task.project_id
  }

def get_projects_tool(
  db,
  current_user
):
  result = get_my_projects_service(
    db,
    current_user
  )

  return [
    {
      "id": project.id,
      "description": project.description,
      "name": project.name,
    }
    for project in result
  ]

def create_project_tool(
  db,
  current_user,
  name: str,
  description: str | None = None
):
  project_data = ProjectCreate(
    name=name,
    description=description
  )

  project = create_project_service(
    db,
    project_data,
    current_user
  )

  return {
    "id": project.id,
    "name": project.name,
    "description": project.description
  }

def update_project_tool(
  db,
  current_user,
  project_id: int,
  name: str | None = None,
  description: str | None = None
):
  update_data = {}
  if name is not None:
    update_data["name"] = name
  if description is not None:
    update_data["description"] = description

  project_data = ProjectUpdate(
    **update_data
  )
  
  project = update_project_service(
    project_id,
    db,
    project_data,
    current_user
  )
  return {
    "id": project.id,
    "name": project.name,
    "description": project.description
  }



TOOL_REGISTRY = {
  "create_task": create_task_tool,
  "get_tasks": get_tasks_tool,
  "update_task": update_task_tool,
  "get_projects": get_projects_tool,
  "create_project": create_project_tool,
  "update_project": update_project_tool
}

TOOL_SCHEMA_REGISTRY = {
  "create_project": CreateProjectToolArgs,
  "get_projects" :GetProjectsToolArgs
}