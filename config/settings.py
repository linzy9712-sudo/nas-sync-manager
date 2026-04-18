from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/db/sync.db"

    # 日志目录
    LOG_DIR: str = str(BASE_DIR / "data" / "logs")

    # 时区
    TZ: str = "Asia/Shanghai"

    # 应用
    APP_TITLE: str = "NAS Sync Manager"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()