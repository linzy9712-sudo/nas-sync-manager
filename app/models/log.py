from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class LogStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 关联任务
    task_id = Column(Integer, ForeignKey("sync_tasks.id"), nullable=False)
    task = relationship("SyncTask", backref="logs")

    # 执行状态
    status = Column(SAEnum(LogStatus), nullable=False, default=LogStatus.RUNNING)
    trigger_type = Column(String(20), nullable=True, comment="触发方式")

    # 时间
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    # 统计
    files_transferred = Column(Integer, default=0, comment="传输文件数")
    bytes_transferred = Column(BigInteger, default=0, comment="传输字节数")

    # 日志
    error_msg = Column(String(500), nullable=True, comment="错误信息")
    output = Column(Text, nullable=True, comment="完整输出")