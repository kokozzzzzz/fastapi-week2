
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel,Field


app = FastAPI()

class UserResponse(BaseModel):
    id: int
    name: str
    age: int

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(gt=0, lt=150)

class UserUpdate(BaseModel):
    name: str
    age: int


users = []
next_id = 1

def find_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user

    return None

# 创建
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
)
def create_user(user: UserCreate):
    for User in users:
        if User["name"]==user.name:
            raise HTTPException(
                status_code=400,
                detail="用户名已存在"
            )
    global next_id
    new_user = {
        "id": next_id,
        "name": user.name,
        "age": user.age,
    }
    
    users.append(new_user)
    next_id+=1

    return new_user


# 读取list
@app.get(
    "/users",
    response_model=list[UserResponse]
)
def get_users(
    page: int = Query(default=1,ge=1,le=100,description="页码"),
    size: int = Query(default=10,ge=1,le=100,description="每页数量")
):
    start = (page - 1) * size
    end = start + size
    return users[start:end]

# 读取one

@app.get(
    "/users/{user_id}",
    response_model = UserResponse
)
def search(user_id: int = Path(gt=0)):
    tmp= find_user(user_id)

    if tmp!=None:
        return tmp
    
    raise HTTPException(
        status_code=404,
        detail="用户未找到"
    )


# 更新
@app.put(
    "/users/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    data: UserUpdate
):
    for user in users:
        if user["id"] == user_id :
            user["name"] = data.name
            user["age"] = data.age
            return user

    raise HTTPException(
        status_code=404,
        detail="用户未找到"
    )


# 删除
@app.delete(
    "/users/{user_id}",
    status_code=204
)
def delete_user(
    user_id: int
):
    for user in users:
        if user["id"] == user_id :
            users.remove(user)
            return

    raise HTTPException(
        status_code=404,
        detail="用户未找到"
    )
    




