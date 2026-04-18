from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.target import SyncTargetCreate, SyncTargetUpdate, SyncTargetOut
from app.services import target_service
from typing import List

router = APIRouter(prefix="/targets", tags=["同步目标"])


@router.get("/", response_model=List[SyncTargetOut])
def list_targets(db: Session = Depends(get_db)):
    return target_service.get_all(db)


@router.get("/{target_id}", response_model=SyncTargetOut)
def get_target(target_id: int, db: Session = Depends(get_db)):
    return target_service.get_by_id(db, target_id)


@router.post("/", response_model=SyncTargetOut, status_code=201)
def create_target(data: SyncTargetCreate, db: Session = Depends(get_db)):
    return target_service.create(db, data)


@router.put("/{target_id}", response_model=SyncTargetOut)
def update_target(target_id: int, data: SyncTargetUpdate, db: Session = Depends(get_db)):
    return target_service.update(db, target_id, data)


@router.delete("/{target_id}", status_code=204)
def delete_target(target_id: int, db: Session = Depends(get_db)):
    target_service.delete(db, target_id)


@router.post("/{target_id}/test", summary="测试连接")
def test_connection(target_id: int, db: Session = Depends(get_db)):
    return target_service.test_connection(db, target_id)