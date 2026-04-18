from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class SyncMode(str, enum.Enum):
    MIRROR = "mirror"           # 镜像同步（同步删除）
    APPEND = "append"           # 单向追加（不删除）
    INCREMENTAL = "incremental" # 增量备份（保留历史）


class TriggerType(str, enum.Enum):
    CRON = "cron"       # 定时触发
    WATCH = "watch"     # 文件静止触发
    MANUAL = "manual"   # 手动触发


class SyncTask(Base):
    __tablename__ = "sync_tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, comment="任务名称")

    # 路径
    source_path = Column(String(500), nullable=False, comment="源路径")
    target_path = Column(String(500), nullable=False, comment="目标路径")

    # 关联目标
    target_id = Column(Integer, ForeignKey("sync_targets.id"), nullable=False)
    target = relationship("SyncTarget", backref="tasks")

    # 同步配置
    sync_mode = Column(SAEnum(SyncMode), nullable=False, default=SyncMode.APPEND)
    enabled = Column(Boolean, default=True, comment="是否启用")

    # 触发配置
    trigger_type = Column(SAEnum(TriggerType), nullable=False, default=TriggerType.MANUAL)
    cron_expr = Column(String(100), nullable=True, comment="Cron表达式，如 0 2 * * *")
    watch_delay = Column(Integer, nullable=True, default=10, comment="文件静止N分钟后触发")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())