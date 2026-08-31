from sqlalchemy.orm import Session
from sqlalchemy import select

from models.task import Task

def create_task(
  db: Session,
  title: str,
  description: str | None,
  project_id: int
):
  task = Task(
    title=title,
    description=description,
    project_id=project_id
  )

  db.add(task)
  db.commit()
  db.refresh(task)

  return task

def get_tasks(
  db: Session,
  project_id: int,
  status: str | None,
  page: int,
  page_size: int
):
  query = select(Task).where(
    Task.project_id == project_id
  )

  if status is not None: 
    query = query.where(
      Task.status == status
    )

  offset = (page - 1) * page_size  

  query = (
    query
    .offset(offset)  # 前面跳过多少条
    .limit(page_size)  # 最多取多少条
  )

  return db.scalars(query).all()