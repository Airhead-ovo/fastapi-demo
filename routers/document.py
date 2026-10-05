from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from services.auth import get_current_user
from models.user import User
from schemas.document import (
  DocumentResponse,
  DocumentChunkResponse,
  DocumentPreviewResponse
)
from services.document import (
  create_document_service,
  rag_answer_service,
  create_conversation_document_service,
  get_documents_by_project_id_service,
  delete_projects_documents_by_document_id_service,
  get_projects_documents_preview_service
)
router = APIRouter()

# 上传文档给指定的project
@router.post(
  "/projects/{project_id}/documents",
  response_model=DocumentResponse,
  summary="Create Document - 上传文档给指定的 Project",
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
  summary="检索增强并生成回答"
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
  response_model=DocumentResponse,
  summary="普通conversation上传对话内临时文件"
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


@router.get(
  "/projects/{project_id}/documents",
  response_model=list[DocumentResponse]
)
def get_documents_by_project_id(
  project_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
): 
  return get_documents_by_project_id_service(
    project_id,
    db,
    current_user
  )

@router.delete(
  "/projects/{project_id}/documents/{document_id}",
  status_code = 204
)
def delete_projects_documents_by_document_id(
  project_id: int,
  document_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return delete_projects_documents_by_document_id_service(
    project_id,
    document_id,
    db,
    current_user
  )

@router.get(
  "/projects/{project_id}/documents/{document_id}/preview",
  response_model=DocumentPreviewResponse
)
def get_projects_documents_preview(
  project_id: int,
  document_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  return get_projects_documents_preview_service(
    project_id,
    document_id,
    db,
    current_user
  )