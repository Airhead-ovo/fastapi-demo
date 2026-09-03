from pydantic import BaseModel
from models.task import TaskStatus
from datetime import datetime
class TaskCreate(BaseModel):
  title: str
  description: str | None = None

class TaskResponse(BaseModel):
  id: int
  title: str
  description: str | None = None
  status: TaskStatus
  project_id: int
  create_at: datetime
  update_at: datetime

  class Config:
    from_attributes = True

class TaskListResponse(BaseModel):
  items: list[TaskResponse]
  page: int
  page_size: int
  total: int

class TaskUpdate(BaseModel):
  title: str | None = None
  description: str | None = None
  status: TaskStatus | None = None