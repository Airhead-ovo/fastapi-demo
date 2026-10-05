from fastapi import FastAPI
import logging

from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.admin import router as admin_router
from routers.project import router as project_router
from routers.conversation import router as conversations_router
from routers.file import router as file_router
from routers.document import router as document_router
from database import engine, Base
from models.user import User
from models.project import Project
from models.document import Document
from models.document_chunk import DocumentChunk

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(project_router)
app.include_router(conversations_router)
app.include_router(file_router)
app.include_router(document_router)


logging.basicConfig(
  level=logging.INFO,
  format="pikaovo | %(asctime)s | %(levelname)s | %(name)s | %(message)s"
)