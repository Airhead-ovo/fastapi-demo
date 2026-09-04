from pydantic import BaseModel, ConfigDict

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