from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.task import SyncMode, TriggerType


class SyncTaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    source_path: str = Field(..., description="源路径")
    target_path: str = Field(..., description="目标路径")
    target_id: int = Field(..., description="同步目标ID")
    sync_mode: SyncMode = Field(SyncMode.APPEND, description="同步模式")
    trigger_type: TriggerType = Field(TriggerType.MANUAL, description="触发方式")
    cron_expr: Optional[str] = Field(None, description="Cron表达式，如 0 2 * * *")
    watch_delay: Optional[int] = Field(10, ge=1, le=1440, description="文件静止N分钟后触发")
    enabled: bool = Field(True, description="是否启用")

    @validator("cron_expr")
    def validate_cron(cls, v, values):
        if values.get("trigger_type") == TriggerType.CRON and not v:
            raise ValueError("触发方式为 cron 时，cron_expr 不能为空")
        if v:
            from croniter import croniter
            if not croniter.is_valid(v):
                raise ValueError(f"无效的 Cron 表达式: {v}")
        return v

    @validator("watch_delay")
    def validate_watch_delay(cls, v, values):
        if values.get("trigger_type") == TriggerType.WATCH and not v:
            raise ValueError("触发方式为 watch 时，watch_delay 不能为空")
        return v


class SyncTaskCreate(SyncTaskBase):
    pass


class SyncTaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_path: Optional[str] = None
    target_path: Optional[str] = None
    target_id: Optional[int] = None
    sync_mode: Optional[SyncMode] = None
    trigger_type: Optional[TriggerType] = None
    cron_expr: Optional[str] = None
    watch_delay: Optional[int] = Field(None, ge=1, le=1440)
    enabled: Optional[bool] = None


class SyncTaskOut(SyncTaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True