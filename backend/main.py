from fastapi import FastAPI
from routers import news #导入router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

#添加中间加（用于解决cors前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

#NOTE:注册路由
app.include_router(news.router)

