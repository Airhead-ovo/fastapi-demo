from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.admin import router as admin_router
from routers.project import router as project_router
from database import engine, Base
from models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(project_router)