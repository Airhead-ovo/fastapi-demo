from fastapi import APIRouter, UploadFile, File, HTTPException, status

from crud.document import (
  create_document,
  create_document_chunk,
  search_chunks
)
from models.project import Project
from models.conversation import Conversation
from services.project import (
  get_project_service
)
from services.file import save_file
from services.embedding import get_embedding
from utils.text import split_text
from schemas.document import DocumentChunkResponse
from clients.llm_client import (
  stream_chat_with_llm
)
from services.conversation import get_conversation_by_id_service


async def create_document_common(
  file,
  db,
  current_user,
  project: Project | None = None,
  conversation: Conversation | None = None
):
    # if file.content_type not in [
    #   "text/plain"
    # ]:
    if not file.filename.lower().endswith(".txt"):
      raise HTTPException(
        status_code=400,
        detail="txtのみアップロードできます"
      )
    
    content = await file.read()
    if len(content) > 5*1024*1024:
      raise HTTPException(
        status_code=400,
        detail="ファイルサイズは５mb以下です"
      )
  
    await file.seek(0) # 把文件指针重新指向开头
  
    file_path = save_file(file)
  
    document = create_document(
      db,
      current_user,
      file.filename,
      file_path,
      len(content),
      project,
      conversation,
    )
  
    # 拆分chunk
    chunks = split_text(content.decode("utf-8"))
  
    # 存入document_chunk
    for index, chunk in enumerate(chunks):
      embedding = get_embedding(chunk)
      create_document_chunk(
        document.id,
        chunk,
        index,
        embedding,
        db
      )
    db.commit()
    return document
  
# 上传文档 同时把内容分成chunk及vector保存在数据库
async def create_document_service(
  project_id: int,
  file,
  db,
  current_user
):

  project = get_project_service(db, current_user, project_id)
  return await create_document_common(
    file,
    db,
    current_user,
    project,
    None
  )

# 上传到普通对话中的临时文件
async def create_conversation_document_service(
  conversation_id,
  file,
  db,
  current_user
):
  conversation = get_conversation_by_id_service(conversation_id, db, current_user)
  if conversation.project_id is not None:
    raise HTTPException(
      status_code = 400,
      detail = "无法在项目对话中上传普通文档"
    )
  return await create_document_common(
    file,
    db,
    current_user,
    None,
    conversation
  )
def search_chunks_service(
  db,
  current_user,
  question: str,
  conversation_id: int,
):
  conversation = get_conversation_by_id_service(conversation_id, db, current_user)

  project = None

  # 如果对话里有projecId说明他是属于项目对话
  if conversation.project_id is not None:
    project = get_project_service(db, current_user, conversation.project_id)

  question_embedding = get_embedding(question)

  results = search_chunks(
    question_embedding, 
    db,
    project = project, 
    conversation = conversation if project is None else None
  )

  chunks = [
    DocumentChunkResponse(
      id=chunk.id,
      chunk_index=chunk.chunk_index,
      content=chunk.content,
      document_id=chunk.document_id,
      distance=distance
    )
    for chunk, distance in results
  ]

  return chunks

def rag_answer_service(
  conversation_id,
  question,
  db,
  current_user
):
  chunks = search_chunks_service(
    db,
    current_user,
    question,
    conversation_id,
  )
  context = augment_context_service(chunks)
  return generate_rag_answer(
    question,
    context
  )


# 增强搜索
def augment_context_service(
  chunks: list[DocumentChunkResponse]
) -> str:
  contents = []
  for chunk in chunks:
    if chunk.distance <= 0.6:
      contents.append(chunk.content)

  if not contents:
    return ""

  return "\n\n".join(contents)

RAG_SYSTEM_PROMPT = """
  你是一个知识库问答助手。

  请仅根据提供的知识库内容回答用户的问题。
  如果知识库内容不足以回答问题，请明确回答“根据当前知识库无法回答该问题”。
  不要使用知识库之外的信息补充或猜测答案。
"""

# 生成最终的答案
def generate_rag_answer(
  question: str,
  context: str
):
  if not context:
    return "根据当前知识库无法得出答案"

  messages = [
    {
      "role": "system",
      "content": RAG_SYSTEM_PROMPT
    },
    {
      "role": "user",
      "content": f"""
        知识库内容:
        {context}
        用户问题:
        {question}
      """
    }
  ]

  res = stream_chat_with_llm(messages)
  answer = "".join(res)

  return answer