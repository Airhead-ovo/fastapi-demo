from pydantic import BaseModel, ConfigDict, field_validator

class MessageCreate(BaseModel):
  content: str

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    conversation_id: int

    model_config = ConfigDict(
        from_attributes=True
    )

class MessageUpdate(BaseModel):
  content: str

  @field_validator("content")
  @classmethod
  def validate_content(cls, value):
    if not value.strip():
      raise ValueError("変更したcontentを入力する必要がある")
    return value.strip()
