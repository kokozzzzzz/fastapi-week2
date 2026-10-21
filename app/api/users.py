from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
)

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.services import user_service

from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)],
)

# 创建用户
@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
)
def create_user(
    user: UserCreate,
    db: Session =Depends(get_db)
):
    new_user = user_service.create_user(db,user)

    if new_user is None:
        raise HTTPException(status_code=400,detail="用户已存在")

    return new_user


# 查询全部用户
@router.get(
    "/",
    response_model=list[UserResponse],
)

def get_users(
    page: int = Query(
        default=1,
        ge=1,
    ),
    size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db)
):
    return user_service.list_users(
        db,
        page,
        size,
    )


# 查询单个用户
@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int = Path(gt=0),
    db: Session = Depends(get_db)
):
    user = user_service.find_user(db,user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="未找到用户",
        )

    return user


# 更新用户
@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int = Path(gt=0),
    data: UserUpdate = None,
    db: Session = Depends(get_db)
):
    user = user_service.update_user(db,user_id,data)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户未找到"
        )
    return user

# 删除用户
@router.delete(
    "/{user_id}",
    status_code = 204
)
def delete_user(
    user_id: int = Path(gt=0),
    db: Session =Depends(get_db)
):
    success = user_service.delete_user(db,user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户未找到")
    return None



