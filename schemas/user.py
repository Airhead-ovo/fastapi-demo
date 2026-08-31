from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
  email: EmailStr
  password: str

class UserResponse(BaseModel):
  id: int
  email: EmailStr    

  class Config:
    from_attributes = True # 需要从对象中读取属性

class UserLogin(BaseModel):
  email: EmailStr
  password: str

class TokenResponse(BaseModel):
  access_token: str
  token_type: str

class AdminUsersResponse(BaseModel):
  id: int
  email: EmailStr
  role: str
  
  class Config:
    from_attributes = True