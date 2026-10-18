
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import find_user_by_name

from app.core.security import verify_password


# 注册
def register_user(
    db: Session,
    data: UserCreate
) -> User|None:
    existing = find_user_by_name(db, data.name)

    if existing:
        return None

    hashed = hash_password(
        data.password
    )

    user = User(
        name=data.name,
        password_hash=hashed,
        age=data.age
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# 登录
def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> User|None:
    user = find_user_by_name(db, username)
    if user is None:
        return None

    if not verify_password(password,user.password_hash):
        return None

    return user
    



