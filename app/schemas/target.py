from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.target import TargetType


class SyncTargetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="目标名称")
    type: TargetType = Field(..., description="同步类型 rsync/rclone")

    # rsync 用
    host: Optional[str] = Field(None, description="目标主机IP")
    auth_user: Optional[str] = Field(None, description="用户名")
    auth_pass: Optional[str] = Field(None, description="密码")
    ssh_key_path: Optional[str] = Field(None, description="SSH Key路径")

    # rclone 用
    remote_name: Optional[str] = Field(None, description="rclone remote名称")


class SyncTargetCreate(SyncTargetBase):
    pass


class SyncTargetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    host: Optional[str] = None
    auth_user: Optional[str] = None
    auth_pass: Optional[str] = None
    ssh_key_path: Optional[str] = None
    remote_name: Optional[str] = None


class SyncTargetOut(SyncTargetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # 密码不返回给前端
    auth_pass: Optional[str] = Field(None, exclude=True)

    class Config:
        from_attributes = True