from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., description="是否收藏",alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., description="新闻ID",alias="newsId")

class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(..., description="收藏ID",alias="favoriteId")
    favorite_time: datetime = Field(..., description="收藏时间",alias="favoriteTime")

class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True, #aliaz
        from_attributes=True #允许从orm属性中取值
    )