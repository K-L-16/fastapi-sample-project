from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from select import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import favorite
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(news_id: int = Query(...,alias="newsId"),
                         user:User = Depends(get_current_user),
                         db:AsyncSession = Depends(get_db)
                         ):
    is_favorite = await favorite.is_news_favorite(db,user.id,news_id)
    return success_response(message="查询收藏状态成功", data=FavoriteCheckResponse(isFavorite= is_favorite))

@router.post("/add")
async def add_favorite(
                       data: FavoriteAddRequest,
                       user:User = Depends(get_current_user),
                       db:AsyncSession = Depends(get_db)
                       ):
    res_add = await favorite.get_news_favorite(db, user.id, data.news_id)
    return success_response(message="收藏成功",data=res_add)

@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(...,alias="newsId"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
        ):
    res_remove = await favorite.remove_news_favorite(db, user.id, news_id)
    if not res_remove:
        raise HTTPException(status_code=400, detail="取消收藏失败")
    return success_response(message="取消收藏成功",data=res_remove)

@router.get("/list")
async def get_favorite_list(
        page: int = Query(1, ge =1),
        page_size: int = Query(10, alias="pageSize", lt=100),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows,total = await favorite.get_favorite_list(db, user.id,page,page_size)
    favorite_lit= [{
        **news.__dict__,
       "favorite_time": favorite_time,
        "favorite_id":favorite_id

    } for news, favorite_time, favorite_id in rows]
    has_more = total > page * page_size
    data = FavoriteListResponse(list=favorite_lit, total=total, hasMore=has_more)
    return success_response(message="获取收藏列表成功", data=data)


@router.delete("/clear")
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await favorite.remove_all_favorite(db, user.id)
    return success_response(message="清空收藏成功", data={"removed_count": count})



