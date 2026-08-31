from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.user import (
  get_user_by_email
)
from utils.security import (
  verify_password,
  create_access_token
)

def authenticate_user(
    db: Session,
    email: str,
    password: str
): 
  user = get_user_by_email(db, email)

  if user is None: 
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="このメールアドレスはまだ登録されていません"
    )
  if not verify_password(
    password,
    user.password_hash
  ):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="メールアドレスまたはパスワードが正しくありません"
    )
  return user