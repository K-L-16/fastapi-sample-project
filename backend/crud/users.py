#根据用户名查询数据库
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import secutity
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

#根据token查询用户信息
async def get_user_by_token(db:AsyncSession, token:str):
    #查询token是否存在且未过期
    stmt = select(UserToken).where(UserToken.token == token, UserToken.expires_at > datetime.now())
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()
    if db_token is None:
        return None
    #查询用户信息
    stmt = select(User).where(User.id == db_token.user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

#跟新用户信息
async def update_user(db:AsyncSession, username:str, user_data: UserUpdateRequest):
    #没有设置值的不更新
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_none=True,
        exclude_unset=True
    ))
    result = await db.execute(query)
    await db.commit()
    #检查更新
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    #获取更新后的用户信息
    update_user = await get_user_by_username(db, username)
    return update_user

#修改密码
async def change_password(db:AsyncSession, user:User, old_password:str, new_password:str):
    if not verify_password(old_password, user.password):
         return False
    hashed_new_password = get_hash_password(new_password)
    user.password = hashed_new_password
    #更新
    #这里用add是因为user是一个已经存在的对象，add会将其标记为已修改状态，然后commit会将修改保存到数据库中，
    #如果直接使用update语句，可能会导致一些问题，比如无法触发ORM的事件机制，或者无法正确处理关联关系等，所以这里使用add是更安全和可靠的方式
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True