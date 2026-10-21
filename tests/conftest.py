import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import setting

from app.models import user

test_engine = create_engine(
    setting.test_database_url,
)

TestingSessionLocal = sessionmaker(
    bind = test_engine,
    autoflush=False,
    autocommit = False,    
)

def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


# 覆盖原get_db
app.dependency_overrides[get_db] = (
    override_get_db
)


# 删除重建数据库
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """全局fixture：注册并登录，返回带Token的Header"""
    # 注册
    client.post(
        "/auth/register",
        json={
            "name": "Alice",
            "password": "123456",
            "age": 20,
        }
    )
    # 登录
    response = client.post(
        "auth/login",
        data={"username": "Alice", "password": "123456"} 
    )

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}





