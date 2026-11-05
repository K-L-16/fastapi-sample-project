from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, desc

from cache.news_cache import get_cached_categories, set_cached_categories, get_cached_news_list, set_cache_news_list
from models.news import Category, News


async def crud_get_categories(db:AsyncSession, skip: int = 0, limit: int=100):
    #现尝试从缓存
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories =  result.scalars().all()

    #写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cached_categories(categories)
    #返回数据
    return categories

async def crud_get_news_lists(db:AsyncSession, category_id:int, skip: int = 0, limit: int = 10):
    #先尝试从缓存获取
    #跳过的数量skip = （页面-1）*每页数量
    cached_list = await get_cached_news_list(category_id, (skip // limit +1), limit)
    if cached_list: #缓存数据json
        # return cached_list
        return [News(**item) for item in cached_list]
    #查询指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    new_list =  result.scalars().all()

    #写入缓存
    if new_list:
        new_list = jsonable_encoder(new_list)
        await set_cache_news_list(category_id, (skip // limit +1), limit, new_list)
    return new_list


async def get_news_count(db:AsyncSession, category_id:int):
    #查询的是指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one() #只能有一个结果，否则报错

async def get_news_detail(db:AsyncSession, news_id:int):
    #查询的是指定新闻的详情
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_news_views(db:AsyncSession, news_id:int):
    #增加新闻的浏览量
    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    #更新 -》 检查数据库知否真正命中数据 -》 命中返回TRue -》 没有命中返回False
    return result.rowcount > 0 if hasattr(result, "rowcount") else True

async def get_related_news(db:AsyncSession, news_id:int, category_id:int, limit:int = 5):
    #查询指定分类下的相关新闻，排除当前新闻
    stmt = (select(News).where(News.category_id == category_id, News.id != news_id)).order_by(News.views,desc(),
                      News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    related_news =  result.scalars().all()
    #列表推导式，推导出新闻的核心数据 ，然后再return
    return [{"id": news.id,
             "title": news.title,
             "content": news.content,
                "image": news.image,
                "author": news.author,
             "publish_time": news.publish_time,
             "category_id": news.category_id,
                "views": news.views
             } for news in related_news]


