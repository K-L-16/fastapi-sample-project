from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, desc
from models.news import Category, News


async def crud_get_categories(db:AsyncSession, skip: int = 0, limit: int=100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def crud_get_news_lists(db:AsyncSession, category_id:int, skip: int = 0, limit: int = 10):
    #查询指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

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


