from fastapi import FastAPI
from pydantic import BaseModel,Field


app=FastAPI()

@app.get("/users/{user_id}")
def root(user_id: int):
    return {
        "message":"Hello FastAPI",
        "user_id" : user_id
    }

@app.get("/search")
def search(
    keyword: str,
    page: int = 1,
    size: int = 10,
):
    return {
        "keyword": keyword,
        "page": page,
        "size": size,
    }

class UserCreate(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(user: UserCreate):
    return{
        "name": user.name,
        "age": user.age
    }


# goods = FastAPI()


# @goods.get("/products/{product_id}")
# def products(product_id: int):
#     return {
#         "product_id": product_id
#     }


# @goods.get("/products")
# def search(category: str):
#     return{
#         "category": category
#     }


# class ProductCreate(BaseModel):
#     name: str = Field(min_length=1)
#     price: float = Field(gt=0)

# @goods.post("/products")
# def create_product(product: ProductCreate):
#     return{
#         "name": product.name,
#         "price": product.price,
#     }



