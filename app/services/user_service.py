
from app.schemas.user import UserCreate,UserUpdate


users = []
next_id = 1


def list_users(
    page: int,
    size: int
) -> list[dict]:
    start = (page - 1) * size
    end = start + size

    return users[start:end]


def find_user(user_id: int) -> dict|None:
    for user in users:
        if user["id"] == user_id:
            return user

    return None

# 创建
def create_user(user: UserCreate) -> dict|None:
    for User in users:
        if User["name"]==user.name:
            return None
    global next_id
    new_user = {
        "id": next_id,
        "name": user.name,
        "age": user.age,
    }
    
    users.append(new_user)
    next_id+=1

    return new_user


# 更新
def update_user(
    user_id: int,
    data: UserUpdate
) -> dict|None:
    user = find_user(user_id)
    if not user:
        return None  # 没找到，让路由层去抛 404
        
    if data.name is not None:
        user["name"] = data.name
    if data.age is not None:
        user["age"] = data.age
    return user


# 删除
def delete_user(
    user_id: int
) -> bool:
    user = find_user(user_id)
    if not user:
        return False  # 没找到
        
    users.remove(user)
    return True

