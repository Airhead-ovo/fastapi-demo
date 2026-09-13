from sqlalchemy.orm import Session
from sqlalchemy import select

from models.project import Project
from models.user import User
from schemas.project import (
  ProjectUpdate
)

def create_project(
    db: Session,
    name: str,
    description: str | None,
    owner_id: int
):
  project = Project(
    name=name,
    description=description,
    owner_id=owner_id
  )
  db.add(project)
  db.commit()
  db.refresh(project)

  return project

def get_my_projects(
    db: Session,
    owner_id: int
):
  return db.scalars(
    select(Project)
    .where(Project.owner_id == owner_id)
  )

def get_project(
  db: Session,
  project_id: int
):
  return db.scalar(
    select(Project)
    .where(Project.id == project_id)
  )
  # return db.get(Project, project_id) 主キーが project_id と一致するProjectを1件取得する

def update_project(
  db: Session,
  project: Project,
  data: ProjectUpdate,
):
  update_data = data.model_dump(
    exclude_unset=True
  )
  for field, value in update_data.items(): # 1個ずつ取り出して
    setattr(
        project,
        field,
        value
      )

  db.commit()
  db.refresh(project)

  return project

def delete_project(
  db: Session, 
  project: Project
): 
  db.delete(project)
  db.commit()