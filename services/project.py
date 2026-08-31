from sqlalchemy.orm import Session
from fastapi import HTTPException, status

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

def create_project_service(
  db: Session,
  data: ProjectCreate,
  current_user: User
):
  return create_project(
    db=db,
    name=data.name,
    description=data.description,
    owner_id=current_user.id
  )

def get_my_projects_service(
  db: Session,
  current_user: User
):
  return get_my_projects(
    db=db,
    owner_id=current_user.id
  )

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
  return update_project(
    db, 
    project, 
    data
  )

  
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
  return delete_project(
    db, 
    project
  )
  