from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.log import SyncLogOut, SyncLogListOut
from app.services import sync_service
from typing import List

router = APIRouter(prefix="/logs", tags=["执行日志"])


@router.get("/", response_model=List[SyncLogListOut], summary="获取最近日志")
def get_recent_logs(limit: int = 50, db: Session = Depends(get_db)):
    return sync_service.get_recent_logs(db, limit)


@router.get("/{log_id}", response_model=SyncLogOut, summary="获取日志详情")
def get_log_detail(log_id: int, db: Session = Depends(get_db)):
    return sync_service.get_log_detail(db, log_id)