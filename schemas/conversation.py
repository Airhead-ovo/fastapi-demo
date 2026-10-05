from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime

class ConversationCreate(BaseModel):
  title: str

class ConversationResponse(BaseModel):
  id: int
  title: str
  user_id: int
  pinned_at: datetime | None
  project_id: int | None = None
  model_config = ConfigDict(
    from_attributes=True
  )

class ConversationUpdate(BaseModel):
  title: str

  @field_validator("title")
  @classmethod
  def validate_title(cls, value):
    if not value.strip():
      raise ValueError("title 入力必要がある")
    return value.strip()

class ConversationPinUpdate(BaseModel):
  is_pinned: bool