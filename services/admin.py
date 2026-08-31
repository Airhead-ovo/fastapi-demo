from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.user import get_all_user
from models.user import User

def admin_users(
  db: Session,
  current_user: User
):
  if current_user.role != "admin":
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="管理者のみアクセスできます"
    )
  
  user = get_all_user(db)

  return user
  
