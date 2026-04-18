from app.db.database import engine, Base

from app.models.target import SyncTarget
from app.models.task import SyncTask
from app.models.log import SyncLog


def init_db():
    """创建所有数据表"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成")


if __name__ == "__main__":
    init_db()