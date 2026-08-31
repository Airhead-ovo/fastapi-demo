from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.task import (
  create_task,
  get_tasks
)
from schemas.task import TaskCreate
from models.user import User

from services.project import get_project_service

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
  status: str | None,
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