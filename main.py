from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from app.db.init_db import init_db

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS（前端开发时需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    init_db()


@app.get("/")
async def root():
    return {"message": "NAS Sync Manager is running 🚀"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}