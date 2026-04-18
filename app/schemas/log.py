from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.log import LogStatus


class SyncLogOut(BaseModel):
    id: int
    task_id: int
    status: LogStatus
    trigger_type: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
    files_transferred: int
    bytes_transferred: int
    error_msg: Optional[str]
    output: Optional[str]

    class Config:
        from_attributes = True


class SyncLogListOut(BaseModel):
    """列表页不返回完整 output，减少流量"""
    id: int
    task_id: int
    status: LogStatus
    trigger_type: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
    files_transferred: int
    bytes_transferred: int
    error_msg: Optional[str]

    class Config:
        from_attributes = True