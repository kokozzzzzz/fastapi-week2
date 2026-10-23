from fastapi import APIRouter

from app.cache.client import redis_client

import asyncio

router = APIRouter(
    prefix = "/cache",
    tags=["Cache"],
)

# 存入缓存
@router.post("/test/{key}")
async def set_cache(
    key: str,
    value: str,
):
    await redis_client.set(
        key,
        value,
        ex=60
    )

    return {
        "message": "cache saved",
        "key": key,
        "ttl": 60,
    }


# 读取缓存
@router.get("/test/{key}")
async def get_cache(key: str):
    value = await redis_client.get(key)

    if value is None:
        return{
            "hit": False,
            "value": None,
        }
    return {
        "key": key,
        "value": value
    }


# 删除缓存
@router.delete("/test/{key}")
async def delete_cache(key: str):
    deleted = await redis_client.delete(key)

    return {
        "deleted": bool(deleted)
    }

# 查看TTL
@router.get("/test/{key}/ttl")
async def get_cache_ttl(key: str):
    ttl = await redis_client.ttl(key)

    return {
        "key": key,
        "ttl": ttl,
    }


# 慢数据模拟
@router.get("/demo")
async def cache_demo():
    cached = await redis_client.get("demo:data")

    if cached is not None:
        return {
            "source": "redis",
            "data": cached
        }

    await asyncio.sleep(2)

    data = "expensive data"

    await redis_client.set(
        "demo:data",
        data,
        ex=60
    )

    return {
        "source": "slow source",
        "data": data
    }




