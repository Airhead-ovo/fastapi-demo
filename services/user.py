from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.user import (
  create_user,
  get_user_by_email
)
from utils.security import (
  hash_password,
  verify_password,
  create_access_token
)
from services.auth_service import authenticate_user

def register_user(
    db: Session,
    email: str,
    password: str
):
  
  # 既存ユーザー確認　　きぞん
  existing_user = get_user_by_email(
    db,
    email
  )
  if existing_user:
    raise HTTPException(
      status_code=400,
      detail="このメールアドレスはすでに登録されています"
    )
  
  # パスワードハッシュ化
  password_hash = hash_password(password)
  # db保存
  user = create_user(
    db,
    email,
    password_hash
  )

  return user

def login_user(
    db: Session,
    email: str,
    password: str
): 
  user = authenticate_user(db, email, password)

  access_token = create_access_token(user.id)
  return {
    "access_token": access_token,
    "token_type": "bearer"
  }