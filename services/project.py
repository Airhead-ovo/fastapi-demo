from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json

from crud.project import (
  create_project,
  get_my_projects,
  get_project,
  update_project,
  delete_project
)
from models.user import User
from schemas.project import (
  ProjectCreate,
  ProjectUpdate
)
from utils.redis_client import redis_client

def create_project_service(
  db: Session,
  data: ProjectCreate,
  current_user: User
):
  project = create_project(
    db=db,
    name=data.name,
    description=data.description,
    owner_id=current_user.id
  )

  cache_key = f"user:{current_user.id}:projects"
  redis_client.delete(cache_key)
  
  return project

def get_my_projects_service(
  db: Session,
  current_user: User
):
  cache_key = f"user:{current_user.id}:projects"
  cached_projects = redis_client.get(cache_key)
  
  if cached_projects:
    return json.loads(cached_projects)

  projects = get_my_projects(
    db=db,
    owner_id=current_user.id
  )
  project_list = [
    {
      "id": project.id,
      "name": project.name,
      "description": project.description
    }
    for project in projects
  ]

  redis_client.set(
    cache_key,
    json.dumps(project_list, ensure_ascii=False), # 存的是json字符串
    ex=60
  )
  
  return project_list

def get_project_service(
  db: Session,
  current_user: User,
  project_id: int
): 
  project = get_project(
    db,
    project_id
  )

  # まず　projectが存在するかどうかを確認して
  if project is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="projectは見つかりません"
    )

  #次に　アクセス権限を確認する
  if project.owner_id != current_user.id:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="このprojectを閲覧する権限がありません"
    )
  return project

def update_project_service(
  project_id: int,
  db: Session,
  data: ProjectUpdate,
  current_user: User
):
  project = get_project_service(
    db, 
    current_user, 
    project_id
  )

  updated_project = update_project(
    db, 
    project, 
    data
  )

  cache_key = f"user:{current_user.id}:projects"
  redis_client.delete(cache_key)

  return updated_project

  
def delete_project_service(
  db: Session,
  project_id: int,
  current_user: User
): 
  project = get_project_service(
    db, 
    current_user, 
    project_id
  )

  deleted_project = delete_project(
    db, 
    project
  )

  cache_key = f"user:{current_user.id}:projects"
  redis_client.delete(cache_key)

  return deleted_project
  