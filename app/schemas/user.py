from pydantic import BaseModel, ConfigDict, Field

# 用户响应类
class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    model_config = ConfigDict(from_attributes=True)

# 用户创建类
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    age: int = Field(gt=0, lt=150)

# 用户更新类
class UserUpdate(BaseModel):
    name: str
    age: int