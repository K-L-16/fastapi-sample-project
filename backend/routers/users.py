from fastapi import APIRouter, Query, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from crud import users
from utils.auth import get_current_user
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


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    #登录逻辑：验证用户名是否存在 -》 验证密码是否正确 -》生成token -》 响应结果
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户或密码错误")
    #生成token
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="用户登录成功", data=response_data)

#获取用户信息 _>封装crud -》 功能整合成为一个工具函数->路由导入使用：依赖注入
@router.get("/info")
async def get_user_info(user:User =Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))

#修改用户信息，验证tokne-》更新（用户苏输入数据 put提交-》请求体参数
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="用户信息更新成功", data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=400, detail="旧密码错误")

    return success_response(message="密码修改成功")
