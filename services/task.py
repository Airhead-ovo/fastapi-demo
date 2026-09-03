from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.task import (
  create_task,
  get_tasks,
  get_task_by_id,
  update_task,
  delete_task
)
from schemas.task import (
  TaskCreate,
  TaskUpdate
)
from models.user import User
from models.task import TaskStatus

from services.project import (
  get_project_service
)

def create_task_service(
  db: Session,
  project_id: int,
  data: TaskCreate,
  current_user: User
):
  project = get_project_service(
    db, 
    current_user, 
    project_id
  )

  return create_task(
    db,
    data.title,
    data.description,
    project.id
  )

def get_tasks_service(
  db: Session,
  project_id: int,
  current_user: User,
  status: TaskStatus | None,
  keyword: str | None,
  page: int,
  page_size: int
):
  project = get_project_service(
    db, 
    current_user, 
    project_id
  )
  tasks, total = get_tasks(
    db,
    project.id,
    status,
    keyword,
    page,
    page_size
  )
  return {
    "items": tasks,
    "page": page,
    "page_size": page_size,
    "total": total
  }


def get_project_task(
  db: Session,
  current_user: User,
  project_id: int,
  task_id: int
):
  project = get_project_service(
    db, 
    current_user, 
    project_id
  )

  task = get_task_by_id(
    db,
    task_id
  )

  if task is None: 
    raise HTTPException(
      status_code=404,
      detail="taskは見つかりません"
    )

  if task.project_id != project.id:
    raise HTTPException(
      status_code=404,
      detail="taskは見つかりません"
    )

  return task
  
def get_task_service(
  db: Session,
  current_user: User,
  project_id: int,
  task_id: int
): 
  return get_project_task(
    db,
    current_user,
    project_id,
    task_id
  )

def update_task_service(
  db: Session,
  current_user:User,
  data: TaskUpdate,
  project_id: int,
  task_id: int
):
  task = get_project_task(
    db,
    current_user,
    project_id,
    task_id
  )

  return update_task(
    db,
    task,
    data
  )

def delete_task_service(
  db: Session,
  current_user:User,
  project_id: int,
  task_id: int
):
  task = get_project_task(
    db,
    current_user,
    project_id,
    task_id
  )

  return delete_task(
    db,
    task
  )