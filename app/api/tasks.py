from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.task import SyncTaskCreate, SyncTaskUpdate, SyncTaskOut
from app.schemas.log import SyncLogListOut, SyncLogOut
from app.services import task_service, sync_service
from typing import List

router = APIRouter(prefix="/tasks", tags=["同步任务"])


@router.get("/", response_model=List[SyncTaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return task_service.get_all(db)


@router.get("/{task_id}", response_model=SyncTaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return task_service.get_by_id(db, task_id)


@router.post("/", response_model=SyncTaskOut, status_code=201)
def create_task(data: SyncTaskCreate, db: Session = Depends(get_db)):
    return task_service.create(db, data)


@router.put("/{task_id}", response_model=SyncTaskOut)
def update_task(task_id: int, data: SyncTaskUpdate, db: Session = Depends(get_db)):
    return task_service.update(db, task_id, data)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_service.delete(db, task_id)


@router.post("/{task_id}/toggle", response_model=SyncTaskOut, summary="启用/禁用任务")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    return task_service.toggle_enabled(db, task_id)


@router.post("/{task_id}/run", response_model=SyncLogOut, summary="手动执行任务")
def run_task(task_id: int, db: Session = Depends(get_db)):
    return sync_service.run_task(db, task_id, trigger_type="manual")


@router.get("/{task_id}/logs", response_model=List[SyncLogListOut], summary="获取任务日志")
def get_task_logs(task_id: int, limit: int = 20, db: Session = Depends(get_db)):
    return sync_service.get_logs(db, task_id, limit)