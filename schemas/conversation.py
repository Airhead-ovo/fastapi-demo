from pydantic import BaseModel, ConfigDict

class ConversationCreate(BaseModel):
  title: str

class ConversationResponse(BaseModel):
  id: int
  title: str
  user_id: int
  model_config = ConfigDict(
    from_attributes=True
  )
