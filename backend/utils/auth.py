#整合 根据token查询用户，返回用户
from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import users


async def get_current_user(authorization: str = Header(..., alias="Authorization"),
                           db: AsyncSession = Depends(get_db)
                            ):
    #根据token查询用户信息
    token = authorization.split(" ")[1] if " " in authorization else authorization
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的token")
    return user