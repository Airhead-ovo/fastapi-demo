from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db

from services.auth import get_current_user
from models.user import User
from services.project import (
  create_project_service,
  get_my_projects_service,
  get_project_service,
  update_project_service,
  delete_project_service
)
from services.task import (
  create_task_service,
  get_tasks_service,
  get_task_service,
  update_task_service,
  delete_task_service
)
from schemas.project import (
  ProjectCreate,
  ProjectResponse,
  ProjectUpdate
)
from schemas.task import (
  TaskListResponse,
  TaskCreate,
  TaskResponse,
  TaskUpdate
)

router = APIRouter( 
  prefix="/projects",
  tags=["Projects"]
)

@router.post(
  "",
  response_model=ProjectResponse
)
def create_project(
  data: ProjectCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return create_project_service(
    db, data, current_user
  )

@router.get(
  "/me/projects",
  response_model=list[ProjectResponse]
)
def get_my_projects(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return get_my_projects_service(
    db,
    current_user
  )

@router.get(
  "/{project_id}",
  response_model=ProjectResponse
)
def get_project(
  project_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return get_project_service(
    db,
    current_user,
    project_id
  )

@router.patch(
  "/{project_id}"
)
def update_project(
  project_id: int,
  data: ProjectUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
): 
  return update_project_service(
    project_id,
    db,
    data,
    current_user
  )
  

@router.delete(
  "/{project_id}",
  status_code=204
)
def delete_project(
  project_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
): 
  delete_project_service(
    db,
    project_id,
    current_user
  )

@router.post(
  "/{project_id}/tasks",
  response_model=TaskResponse
)
def create_task(
  project_id: int,
  data: TaskCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return create_task_service(
    db,
    project_id,
    data,
    current_user
  )

@router.get(
  "/{project_id}/tasks",
  response_model=TaskListResponse
)
def get_tasks(
  project_id: int,
  status: str | None = None,  # Query
  keyword: str | None = None, 
  page: int = Query(default=1, ge=1),             
  page_size: int = Query(default=10, ge=1, le=100), # 最小値　１　さいしょうち   　最大値　１００
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return get_tasks_service(
    db,
    project_id,
    current_user,
    status,
    keyword,
    page,
    page_size
  )

@router.get(
  "/{project_id}/tasks/{task_id}",
  response_model=TaskResponse
)
def get_task(
  project_id: int,
  task_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return get_task_service(
    db,
    current_user,
    project_id,
    task_id
  )

@router.patch(
  "/{project_id}/tasks/{task_id}",
  response_model=TaskResponse
)
def update_task(
  data: TaskUpdate,
  project_id: int,
  task_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
): 
  return update_task_service(
    db,
    current_user,
    data,
    project_id,
    task_id
  )

@router.delete(
  "/{project_id}/tasks/{task_id}",
  status_code=204 # DELETE成功しだけど、返すデータはない
)
def delete_task(
  project_id: int,
  task_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
): 
  return delete_task_service(
    db,
    current_user,
    project_id,
    task_id
  )