from sqlalchemy.orm import Session
from sqlalchemy import select

from models.user import User

def create_user(
    db: Session,
    email: str,
    password_hash: str
):
  user = User(
    email=email,
    password_hash=password_hash
  )

  db.add(user)
  db.commit()
  db.refresh(user)

  return user

def get_user_by_email(
    db: Session,
    email: str
): 
  return db.scalar(
    select(User)
    .where(User.email == email)
  )

def get_user_by_id(
    db: Session,
    user_id: int
):
  return db.get(User, user_id)

def get_all_user(
    db: Session
): 
  return db.scalars(
    select(User)
  ).all() # 複数件取得するため、scalars().all()を使用します