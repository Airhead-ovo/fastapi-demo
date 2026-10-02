from pydantic import BaseModel, ConfigDict, field_validator

class ConversationCreate(BaseModel):
  title: str

class ConversationResponse(BaseModel):
  id: int
  title: str
  user_id: int
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