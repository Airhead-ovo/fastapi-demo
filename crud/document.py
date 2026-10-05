from models.document import Document
from models.project import Project
from models.conversation import Conversation
from models.document_chunk import DocumentChunk
from sqlalchemy import select, delete

def create_document(
  db,
  current_user,
  file_name,
  file_path,
  file_size,
  project: Project | None = None,
  conversation: Conversation | None = None,
):
  document = Document(
    filename = file_name,
    file_path = file_path,
    file_size = file_size,
    user_id = current_user.id,
    project_id = project.id if project is not None else None,
    conversation_id = conversation.id if conversation is not None else None
  )

  db.add(document)
  db.flush()
  return document

def create_document_chunk(
  document_id,
  chunk,
  index,
  embedding,
  db
):
  document_chunk = DocumentChunk(
    document_id=document_id,
    content=chunk,
    chunk_index=index,
    embedding=embedding
  )
  db.add(document_chunk)
  db.flush()
  return document_chunk

def search_chunks(
  question_embedding,
  db,
  project: Project | None = None,
  conversation: Conversation | None = None,
  limit: int = 3
):
  if project is None and conversation is None:
    raise ValueError("project　または　conversation　を指定してください")
  
  if project is not None and conversation is not None:
    raise ValueError("project　と　conversation　を同時に指定することはできません")
  
  distance = DocumentChunk.embedding.cosine_distance(
    question_embedding
  )

  where = (
    Document.project_id == project.id 
    if project is not None 
    else Document.conversation_id == conversation.id
  )

  query = (
    select(
      DocumentChunk,
      distance.label("distance")
    )
    .join(Document, DocumentChunk.document_id == Document.id)
    .where(where)
    .order_by(distance) # 最相似的排前面
    .limit(limit)
  )

  return db.execute(query).all()

def get_documents_by_project_id(
  project_id,
  db
):
  query = (
    select(Document)
    .where(
      Document.project_id == project_id
    )
    .order_by(
      Document.created_at.desc()
    )
  )
  return db.scalars(query).all()

def get_project_document(
  project_id,
  document_id,
  db
):
  query = (
    select(Document)
    .where(
      Document.project_id == project_id,
      Document.id == document_id
    )
  )
  return db.scalar(query)
  
def delete_projects_documents_by_document_id(
  document,
  db,
):
  db.delete(document)