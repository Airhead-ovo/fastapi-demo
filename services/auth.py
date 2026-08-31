import jwt

from fastapi import (
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from crud.user import get_user_by_id
from utils.security import (
    SECRET_KEY,
    ALGORITHM
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="認証情報が無効です",
    headers={
      "WWW-Authenticate": "Bearer"
    }
  )

  try: 
    payload = jwt.decode( # 把带过来的token解压了
      token,
      SECRET_KEY,
      algorithms=[ALGORITHM]
    )
    user_id = payload.get("sub")
    if user_id is None: 
      raise credentials_exception

  except jwt.PyJWTError: # jwtの検証に失敗した場合
    raise credentials_exception

  user = get_user_by_id(db, int(user_id))
  if user is None: 
    raise credentials_exception
  
  return user

