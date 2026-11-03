from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str

# 用户信息基础数据模型
class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")

class UserInfoResponse(UserInfoBase):
    id:int
    username: str
    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True, #aliaz
        from_attributes=True #允许从orm属性中取值
    )

#data 数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info:UserInfoResponse = Field(..., alias="userInfo")  #指定别名，前端返回的字段名为userInfo

    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True, #aliaz
        from_attributes=True #允许从orm属性中取值
    )