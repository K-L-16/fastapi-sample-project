#根据用户名查询数据库
import uuid
from datetime import datetime, timedelta
from idlelib.debugger_r import restart_subprocess_debugger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.users import User, UserToken
from schemas.users import UserRequest
from utils.secutity import get_hash_password, verify_password


async def get_user_by_username(db: AsyncSession, username: str):
    #查询指定用户名的用户
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()  #返回单个结果，如果没有则返回None

#创建用户
async def create_user(db:AsyncSession, user_data: UserRequest):
    #先密码加密处理 -> add
    hashed_password = get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  #刷新对象，重新获取数据库生成的id等信息
    return user

#生成token
async def create_token(db:AsyncSession, user_id:int):
    #生成tokne + 设置过期时间，查询数据库当前用户是否有token，如果有就更新，没有就创建
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)  #设置过期时间为7天后
    query = select(UserToken).where(UserToken.id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        #更新token和过期时间
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        #创建新的token记录
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()
    return token

# 验证token
async def authenticate_user(db:AsyncSession, username:str, password:str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    #验证密码
    if not verify_password(password, user.password):
        return None
    return user