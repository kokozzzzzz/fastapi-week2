

from fastapi.testclient import TestClient


# 辅助函数
def register_user(client: TestClient, username="alice", password="123456", age=20):
    """辅助注册用户"""
    return client.post(
        "/auth/register",
        json={
            "name": username,
            "password": password,
            "age": age,
        }
    )

def get_auth_headers(client: TestClient, username="alice", password="123456"):
    """辅助注册并登录，返回带 Token 的 Header"""
    register_user(client, username, password)
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password} # 注意这里用 data 发表单，不是 json
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}



# 测试用例
def test_register(client: TestClient):
    response = register_user(client)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "alice"
    assert data["age"] == 20
    
    
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_register(client: TestClient):
    # 第一次注册，应该成功
    register_user(client)
    # 第二次用同样的 username 注册，应该失败 400
    response = register_user(client)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "用户已经存在" 


def test_login_success(client: TestClient):
    register_user(client)
    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "123456"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    register_user(client)
    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "wrong-password"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "账号或密码不正确"


def test_me_without_token(client: TestClient):
    # 不带 token 访问受保护接口
    response = client.get("/auth/me")
    
    # 应该返回 401 Unauthorized
    assert response.status_code == 401


def test_me_with_token(client: TestClient):
    # 获取带有 Token 的 headers
    headers = get_auth_headers(client)
    
    # 带 Token 请求
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["name"] == "alice"