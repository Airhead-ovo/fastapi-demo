from pydantic import BaseModel

class TaskCreate(BaseModel):
  title: str
  description: str | None = None

class TaskResponse(BaseModel):
  id: int
  title: str
  description: str | None = None
  status: str
  project_id: int

  class Config:
    from_attributes = True

class TaskListResponse(BaseModel):
  items: list[TaskResponse]
  page: int
  page_size: int
  total: int