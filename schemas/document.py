from pydantic import BaseModel, ConfigDict

class DocumentResponse(BaseModel):
  id: int
  filename: str
  file_path: str
  file_size: int
  project_id: int
  model_config = ConfigDict(
    from_attributes=True
  )

class DocumentChunkResponse(BaseModel):
  id: int
  chunk_index: int
  content: str
  document_id: int
  distance: float
