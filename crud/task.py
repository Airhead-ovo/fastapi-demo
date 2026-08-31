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
  project_id: int
):
  return db.scalars(
    select(Task)
    .where(Task.project_id == project_id)
  )