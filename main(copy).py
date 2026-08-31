from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Request Model（请求模型 / リクエストモデル）
class UserCreate(BaseModel):
    username: str
    age: int
    password: str
    email: str

# Response Model（レスポンスモデル）
class UserResponse(BaseModel):
    username: str
    age: int
    email: str
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    return user

class BookCreate(BaseModel):
    title: str
    price: int
    author: str

@app.post("/books")
def create_book(book: BookCreate):
    return {
        "message": "Book Created",
        "book": book.title
    }

class ProductCreate(BaseModel):
    name: str
    price: int
    description: str
    secret_code: str


class ProductResponse(BaseModel):
    name: str
    price: int
    description: str

@app.post("/products", response_model=ProductResponse)
def create_products(product: ProductCreate):
    return product





class orderCreate(BaseModel):
    product_name: str
    quantity: int
    price: int
    customer: str
    internal_code: str

class orderResponse(BaseModel):
    product_name: str
    quantity: int
    price: int
    customer: str

@app.post("/orders", response_model=orderResponse)
def create_order(order: orderCreate):
    # FastAPI 接管返回值    按照 OrderResponse 规则处理它。 
    return order 














class RegisterCreate(BaseModel):
    username: str
    email: str
    password:str
    age: int
    invite_code: str
    # 不传avatar也不会报错
    avatar: str | None = None


class RegisterResponse(BaseModel):
    username: str
    email: str
    age: int

@app.post("/register", response_model=RegisterResponse)
def register_user(user: RegisterCreate):
    return user



products = [
    {
        "id":1,
        "name":"MacBook",
        "price":10000
    },
    {
        "id":2,
        "name":"iPhone",
        "price":8000
    }
]
class CreateProducts(BaseModel):
    name: str
    price: int

class ResponseProducts(BaseModel):
    name: str
    price: int

# POST /products
@app.post("/products")
def add_product(product: CreateProducts):
    products.append(product)
    return {
        "message": "add scussess"
    }

@app.get("/products", response_model=list[ResponseProducts])
def get_products():
    return products

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            products.remove(product)
            return product
    return {
        "message": "delete failed"
    }    
    
@app.get("/products/{product_id}", response_model=ResponseProducts)
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return {
        "message": "can not found"
    }

@app.post("/products")
def post_product(product: CreateProducts):
    product["id"] = len(products) + 1
    products.append(product)
    return {
        "message": "add sucess"
    }

class CreateProcucts(BaseModel):
    id: int
    price: int
    name: str
@app.put("/products/{product_id}")
def update_product(product_id: int, product: CreateProcucts):
    for p in products:
        if p["id"] == product_id:
            p["price"] = product.price
            p["name"] = product.name
            return {
                "message": "update success"
            }
    return {
        "message": "can not find product"
    }

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str]
    age: Mapped[int]


# 创建 engine（连接 sqlite:///school.db）
# 创建 SessionLocal
# 创建一个 session
# 最后关闭 session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///test.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
user = User(
    username="Tom",
    email="tom@example.com",
    age=20
)
session.add(user)
session.commit()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str]
    age: Mapped[str]

# User指查哪个表 1是主键 查id为1的
user = session.get(User, 1) 
print(user.username)

from sqlalchemy import select
users = session.scalars(select(User)).all()
# 年齢が20歳以上の最初のユーザーを取得します。 しゅとく
user = session.scalars(
    select(User).where(User.age >= 20)
).first()





session.scalars(
    select(User).where(
        User.country.in_(
            ["Japan", "China"]
        )
    )
).all()




session.scalars(
    select(User).where(
        User.name.like("%to%")
    )
).all()

session.scalars(
    select(User).where(
        User.name.like(f"%{keyword}%")
    )
).all()

@app.delete("/product/{product_id}")
def delete_product(product_id: int):
    product = session.get(Product, product_id)
    if product is None: 
        return {
            "message": "can not find this product"
        }
    session.delete(product)
    session.commit()
    return {
        "message": "delete ok"
    }