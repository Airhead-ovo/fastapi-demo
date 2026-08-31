from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from services.admin import admin_users
from services.auth import get_current_user
from schemas.user import AdminUsersResponse

router = APIRouter( 
  prefix="/admin",
  tags=["Admin"]
)
@router.get("/users", response_model=list[AdminUsersResponse])
def get_admin_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
  ):
  return admin_users(
    db,
    current_user
  )