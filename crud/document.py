from models.document import Document
from models.document_chunk import DocumentChunk
from sqlalchemy import select

def create_document(
  file_name,
  file_path,
  file_size,
  project,
  db,
  current_user
):
  document = Document(
    filename = file_name,
    file_path = file_path,
    file_size = file_size,
    user_id = current_user.id,
    project_id = project.id,
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
  project,
  db,
  limit: int = 3
):
  distance = DocumentChunk.embedding.cosine_distance(
    question_embedding
  )
  query = (
    select(
      DocumentChunk,
      distance.label("distance")
    )
    .join(Document, DocumentChunk.document_id == Document.id)
    .where(Document.project_id == project.id)
    .order_by(distance) # 最相似的排前面
    .limit(limit)
  )

  return db.execute(query).all()