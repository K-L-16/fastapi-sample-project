from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse
from crud import users
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(user_data: UserRequest,  db:AsyncSession = Depends(get_db)): #用户信息和db
    #注册逻辑：验证哟个胡是否存在 -》 创建用户 -》生成token ——》 响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    #创建用户
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)
    # return {
    #     "code": 200,
    #     "message": "用户注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo":{
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar,
    #         }
    #     }
    #
    # }
    response_data = UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="用户注册成功", data=response_data)