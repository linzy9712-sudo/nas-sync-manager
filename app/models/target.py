from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class TargetType(str, enum.Enum):
    RSYNC = "rsync"
    RCLONE = "rclone"


class SyncTarget(Base):
    __tablename__ = "sync_targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, comment="目标名称")
    type = Column(SAEnum(TargetType), nullable=False, comment="同步类型 rsync/rclone")

    # rsync 用
    host = Column(String(200), nullable=True, comment="目标主机IP")
    auth_user = Column(String(100), nullable=True, comment="用户名")
    auth_pass = Column(String(200), nullable=True, comment="密码")
    ssh_key_path = Column(String(500), nullable=True, comment="SSH Key路径")

    # rclone 用
    remote_name = Column(String(100), nullable=True, comment="rclone remote名称")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())