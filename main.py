import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from app.db.init_db import init_db
from app.api import api_router
from app.core import scheduler, watcher

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    init_db()
    scheduler.start()
    watcher.start()
    yield
    # 关闭
    scheduler.stop()
    watcher.stop()


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "NAS Sync Manager is running 🚀"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}