from sqlalchemy.orm import Session
from sqlalchemy import select, func

from models.task import (
  Task,
  TaskStatus
)
from schemas.task import TaskUpdate


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
  status: TaskStatus | None,
  keyword: str | None,
  page: int,
  page_size: int
):
  query = select(Task).where(
    Task.project_id == project_id
  )

  count_query = select(func.count(Task.id)).where(
    Task.project_id == project_id
  )

  if status is not None: 
    query = query.where(
      Task.status == status
    )
    count_query = count_query.where(
      Task.status == status
    )

  if keyword:
    query = query.where(
      Task.title.contains(keyword)
    )
    count_query = count_query.where(
      Task.title.contains(keyword)
    )

  total = db.scalar(count_query) # 执行 SQL，然后只取结果的第一个值 就是数字

  offset = (page - 1) * page_size  

  tasks = db.scalars(
    query
    .offset(offset)  # 前面跳过多少条
    .limit(page_size)  # 最多取多少条
  ).all()

  return tasks, total

def get_task_by_id(
  db: Session,
  task_id: int  
):
  query = select(Task).where(
    Task.id == task_id
  )
  return db.scalar(query)
  # return db.get(Task, task_id)

def update_task(
  db: Session,
  task: Task,
  data: TaskUpdate
):
  update_data = data.model_dump(
    exclude_unset=True
  )
  for field, value in update_data.items():
    setattr(task, field, value)

  db.commit()
  db.refresh(task)

  return task

def delete_task(
  db: Session,
  task: Task
):
  db.delete(task)
  db.commit()