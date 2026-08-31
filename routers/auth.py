from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from database import get_db
from schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from services.user import register_user, login_user
from utils.security import  create_access_token
from services.auth_service import authenticate_user

router = APIRouter( 
  prefix="/auth",
  tags=["Auth"]
)

@router.post(
  "/register",
  response_model=UserResponse
)
def register(
  user: UserCreate,
  db: Session = Depends(get_db)
):
  return register_user(
    db,
    user.email,
    user.password
  )

@router.post(
  "/login",
  response_model=TokenResponse
)
def login(
  data: UserLogin,
  db: Session = Depends(get_db)
): 
  return login_user(
    db,
    data.email,
    data.password
  )

@router.post("/token")
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_user(
      db,
      form_data.username,
      form_data.password
    )