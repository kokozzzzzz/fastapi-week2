
from fastapi.testclient import TestClient



def test_upload_valid_txt(client: TestClient):
    # 测试上传合法的 .txt 文件
    files = {
        "file":(
            "hello.txt",
            b"hello FastAPI",
            "text/plain",
        )
    }

    response = client.post(
        "/files/",
        files=files,
    )

    assert response.status_code == 201
    assert "hello.txt" in response.json()["filename"]


def test_upload_invalid_file_type(client: TestClient, auth_headers):
    # 测试上传非法的 .exe 文件：期望 400
    files = {
        "file": ("virus.exe", b"fake exe content", "application/x-msdownload")
    }
    
    response = client.post(
        "/files/",
        files=files,
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "不支持该文件格式" in response.json()["detail"]

