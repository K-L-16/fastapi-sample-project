from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

#数据库url
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app"

#创建异步引擎
async_engin = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True, #可选输出sql日志
    pool_size = 10,
    max_overflow = 20
)

#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engin,
    class_=AsyncSession,
    expire_on_commit=False,
)

#依赖项,用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        # try:
        #     yield session
        #     await session.commit()
        # except Exception:
        #     await session.rollback()
        #     raise
        # finally:
        #     await session.close()
        #NOTE:上面这些有些重复
        yield session