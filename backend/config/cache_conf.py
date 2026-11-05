import os

import redis.asyncio as redis
import json
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

#创建redis的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True #是否将字节数据解码为字符串
)

#设置和读取（字符串 和 列表或字典） “【{}】”
#读取：字符串
async def get_cache(key: str):
    # value = await redis_client.get(key)
    try:
        return redis_client.get(key)
    except Exception as e:
        print(f"Error getting cache for key {key}: {e}")
        return None

#读取： 列表或字典
async def get_json_cache(key: str):
    try:
        value = await redis_client.get(key)
        if value is not None:
            return json.loads(value)
        return None
    except Exception as e:
        print(f"Error getting JSON cache for key {key}: {e}")
        return None

#设置缓存 setex
async def set_cache(key: str, value, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            #将字典或列表转换为JSON字符串
            value = json.dumps(value)
        await redis_client.set(key, value, ex=expire)
        return True
    except Exception as e:
        print(f"Error setting cache for key {key}: {e}")
        return False