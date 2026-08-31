from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256" # 署名アルゴリズム
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 有効期限

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str: # パスワードハッシュ化
    return pwd_context.hash(password)

def verify_password(
    plain_password: str, # ユーザーが入力したパスワード
    hashed_password: str # dbにハッシュ化して保存したパスワード
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub":str(user_id), # このTokenは誰のものか
        "exp": expire # いつまで有効か
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )