from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.target import SyncTarget
from app.schemas.target import SyncTargetCreate, SyncTargetUpdate
from app.engines import SyncEngineFactory, SyncContext
from app.models.task import SyncMode


def get_all(db: Session):
    return db.query(SyncTarget).order_by(SyncTarget.created_at.desc()).all()


def get_by_id(db: Session, target_id: int) -> SyncTarget:
    obj = db.query(SyncTarget).filter(SyncTarget.id == target_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"目标 {target_id} 不存在")
    return obj


def create(db: Session, data: SyncTargetCreate) -> SyncTarget:
    # 检查名称重复
    exists = db.query(SyncTarget).filter(SyncTarget.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"目标名称 '{data.name}' 已存在")

    obj = SyncTarget(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, target_id: int, data: SyncTargetUpdate) -> SyncTarget:
    obj = get_by_id(db, target_id)
    for field, value in data.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, target_id: int):
    obj = get_by_id(db, target_id)
    # 检查是否有任务在使用
    if obj.tasks:
        raise HTTPException(
            status_code=400,
            detail=f"该目标下还有 {len(obj.tasks)} 个任务，请先删除任务"
        )
    db.delete(obj)
    db.commit()


def test_connection(db: Session, target_id: int) -> dict:
    obj = get_by_id(db, target_id)
    engine = SyncEngineFactory.get_engine(obj.type)
    ctx = SyncContext(
        source_path="",
        target_path=obj.host or "",
        sync_mode=SyncMode.APPEND,
        host=obj.host,
        auth_user=obj.auth_user,
        ssh_key_path=obj.ssh_key_path,
        remote_name=obj.remote_name,
    )
    success, msg = engine.test_connection(ctx)
    return {"success": success, "message": msg}