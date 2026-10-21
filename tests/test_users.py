
from fastapi.testclient import TestClient


def test_users_without_token(client: TestClient):
    # 无token
    response = client.get("/users")
    assert response.status_code == 401


def test_users_with_token(client: TestClient,auth_headers):
    # 有token
    response = client.get("/users",headers=auth_headers)

    assert response.status_code == 200
    assert isinstance(response.json(),list)


def test_get_user_not_found(client: TestClient, auth_headers):
    """测试查询不存在的用户（ID=99999）：期望 404"""
    response = client.get("/users/99999", headers=auth_headers)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "未找到用户"



