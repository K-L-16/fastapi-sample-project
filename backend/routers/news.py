from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud.news import *
from fastapi import Depends, HTTPException
#NOTE模块化路由
#创建APIRouter实例
router = APIRouter(prefix="/api/news", tags=["news"])
#这里的prefix就是这个路由的所有的prefix，路由前缀
#tag就是文档里的分类

#接口实现流程
#1.模块化路由 -》 api接口规范文档
#2. 定义模型类 -》数据库表
#3.在crud文件夹里面创建文件，封装操作数据库的方法
#4. 在路由处理函数里面调用crud封装好的方法，响应结果

@router.get("/categories")
async def get_categories(skip: int=0, limit: int=100,db:AsyncSession = Depends(get_db)):
    #先获取数据库里面的新闻分裂数据，先定义模型类，封装查询数据的方法
    categories = await crud_get_categories(db,skip, limit)
    return {
        "code":200,
        "message":"获取新闻分类成功",
        "data": categories
    }

@router.get("/list")
async def get_news_list( #NOTE:注意这里的category_id前端转递的是categroyId所以我们需要用aliaz来映射
        category_id: int = Query(...,alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize",lt=100),
        db:AsyncSession = Depends(get_db),
):
    #处理扉页规则，查询新闻列表，计算总量，计算是否还有更多
    offset = (page-1)*page_size
    new_list = await crud_get_news_lists(db,category_id,offset,page_size)
    total = await get_news_count(db,category_id)
    #跳过的 + 当前列表里面的数量） 《 总量
    has_more = (offset+ len(new_list)) < total
    return {
        "code":200,
        "message":"获取新闻列表",
        "data":{
            "list": new_list,
            "total":total,
            "hasMore":has_more
        }
    }