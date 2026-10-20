import os

import httpx
from fastapi import APIRouter,HTTPException


from dotenv import load_dotenv


router = APIRouter(
    prefix="/external",
    tags=["External API"]
)

BASE_URL = "https://api.github.com"
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("未找到 GITHUB_TOKEN，请检查 .env 文件是否配置正确")

HEADERS = {
        "Authorization": f"token {TOKEN}",
        "User-Agent": "MyApp/1.0"  # GitHub API 要求必须提供 User-Agent[reference:4]
    }



@router.get("/github/{username}")
async def get_github_user(username: str):
    url = f"{BASE_URL}/users/{username}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url,headers=HEADERS)

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="无法得到外部服务",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="没有找到该GitHub用户",
        )
    
    if response.is_error:
        raise HTTPException(
            status_code=502,
            detail="外部 API 返回错误",
        )

    data = response.json()
    
    return {
        "username": data["login"],
        "public_repos": data["public_repos"],
        "followers": data["followers"],
        "html_url": data["html_url"],
    }



