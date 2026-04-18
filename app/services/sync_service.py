from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.log import SyncLog, LogStatus
from app.models.task import SyncTask
from app.schemas.log import SyncLogOut, SyncLogListOut
from app.services.task_service import get_by_id as get_task
from app.engines import SyncEngineFactory, SyncContext


def run_task(db: Session, task_id: int, trigger_type: str = "manual") -> SyncLog:
    """执行同步任务，写入日志"""
    task: SyncTask = get_task(db, task_id)

    if not task.enabled:
        raise HTTPException(status_code=400, detail="任务已禁用，无法执行")

    target = task.target
    if not target:
        raise HTTPException(status_code=400, detail="任务未关联同步目标")

    # 创建运行中日志
    log = SyncLog(
        task_id=task_id,
        status=LogStatus.RUNNING,
        trigger_type=trigger_type,
        started_at=datetime.now(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    try:
        # 构建执行上下文
        ctx = SyncContext(
            source_path=task.source_path,
            target_path=task.target_path,
            sync_mode=task.sync_mode,
            host=target.host,
            auth_user=target.auth_user,
            auth_pass=target.auth_pass,
            ssh_key_path=target.ssh_key_path,
            remote_name=target.remote_name,
        )

        # 获取引擎并执行
        engine = SyncEngineFactory.get_engine(target.type)
        result = engine.sync(ctx)

        # 更新日志
        log.status = LogStatus.SUCCESS if result.success else LogStatus.FAILED
        log.finished_at = datetime.now()
        log.files_transferred = result.files_transferred
        log.bytes_transferred = result.bytes_transferred
        log.output = result.output
        log.error_msg = result.error_msg

    except Exception as e:
        log.status = LogStatus.FAILED
        log.finished_at = datetime.now()
        log.error_msg = str(e)

    db.commit()
    db.refresh(log)
    return log


def get_logs(db: Session, task_id: int, limit: int = 20) -> list:
    task = get_task(db, task_id)
    return (
        db.query(SyncLog)
        .filter(SyncLog.task_id == task_id)
        .order_by(SyncLog.started_at.desc())
        .limit(limit)
        .all()
    )


def get_log_detail(db: Session, log_id: int) -> SyncLog:
    log = db.query(SyncLog).filter(SyncLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"日志 {log_id} 不存在")
    return log


def get_recent_logs(db: Session, limit: int = 50) -> list:
    """获取所有任务的最近日志（首页概览用）"""
    return (
        db.query(SyncLog)
        .order_by(SyncLog.started_at.desc())
        .limit(limit)
        .all()
    )