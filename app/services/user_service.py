
from app.schemas.user import UserCreate,UserUpdate
from app.models.user import User

from sqlalchemy.orm import Session
from app.core.security import hash_password



#查列表
def list_users(
    db: Session,
    page: int,
    size: int
) -> list[User]:
    start = (page - 1) * size
    return db.query(User).offset(start).limit(size).all()


#查单个
def find_user(
    db: Session,
    user_id: int
) -> User|None:
    return db.query(User).filter(User.id==user_id).first()


# ---------- 按名字查（用于查重名） ----------
def find_user_by_name(db: Session, name: str) -> User | None:
    return db.query(User).filter(User.name == name).first()


# 创建用户
def create_user(db: Session,user_data: UserCreate) -> User|None:
    if find_user_by_name(db,user_data.name):
        return None

    user = User(
        name = user_data.name,
        password_hash = hash_password(user_data.password),
        age= user_data.age
    )
    db.add(user)        # 加入会话
    db.commit()         # 提交，写数据库
    db.refresh(user)    # 从数据库刷新，拿到 id
    return user
    


# 更新用户信息
def update_user(
    db: Session,
    user_id: int,
    data: UserUpdate
) -> User|None:
    user = find_user(db,user_id)
    if not user:
        return None  # 没找到，让路由层去抛 404
        
    if data.name is not None:
        user.name = data.name
    if data.age is not None:
        user.age = data.age

    db.commit()
    db.refresh(user)
    
    return user


# 删除用户
def delete_user(
    db: Session,
    user_id: int
) -> bool:
    user = find_user(db,user_id)
    if not user:
        return False  # 没找到
        
    db.delete(user)
    db.commit()
    return True

