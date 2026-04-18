from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.task import SyncTask
from app.schemas.task import SyncTaskCreate, SyncTaskUpdate
from app.services.target_service import get_by_id as get_target


def get_all(db: Session):
    return db.query(SyncTask).order_by(SyncTask.created_at.desc()).all()


def get_by_id(db: Session, task_id: int) -> SyncTask:
    obj = db.query(SyncTask).filter(SyncTask.id == task_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return obj


def create(db: Session, data: SyncTaskCreate) -> SyncTask:
    # 检查名称重复
    exists = db.query(SyncTask).filter(SyncTask.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"任务名称 '{data.name}' 已存在")

    # 检查目标存在
    get_target(db, data.target_id)

    obj = SyncTask(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, task_id: int, data: SyncTaskUpdate) -> SyncTask:
    obj = get_by_id(db, task_id)

    if data.target_id:
        get_target(db, data.target_id)

    for field, value in data.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, task_id: int):
    obj = get_by_id(db, task_id)
    db.delete(obj)
    db.commit()


def toggle_enabled(db: Session, task_id: int) -> SyncTask:
    obj = get_by_id(db, task_id)
    obj.enabled = not obj.enabled
    db.commit()
    db.refresh(obj)
    return obj