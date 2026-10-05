from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from services.auth import get_current_user
from models.user import User
from schemas.document import (
  DocumentResponse,
  DocumentChunkResponse
)
from services.document import (
  create_document_service,
  rag_answer_service,
  create_conversation_document_service
)

router = APIRouter()

# 上传给指定的project
@router.post(
  "/projects/{project_id}/documents",
  response_model=DocumentResponse
)
async def create_document(
  project_id: int,
  file: UploadFile = File(...),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return await create_document_service(
    project_id,
    file,
    db,
    current_user
  )

# 在项目里检索增强并生成回答
@router.get(
  "/projects/conversations/{conversation_id}/documents/search",
)
def search_chunks(
  conversation_id: int,
  question: str,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return rag_answer_service(
    conversation_id,
    question,
    db,
    current_user
  )

# 普通conversation上传对话内临时文件
@router.post(
  "/conversations/{conversation_id}/documents",
  response_model=DocumentResponse
)
async def create_conversation_document(
  conversation_id: int,
  file: UploadFile = File(...),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return await create_conversation_document_service(
    conversation_id,
    file,
    db,
    current_user
  )