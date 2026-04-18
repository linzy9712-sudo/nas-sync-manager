from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.task import SyncTask, TriggerType
from app.services.sync_service import run_task
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


def _run_task_job(task_id: int):
    """APScheduler 调用的任务函数"""
    db: Session = SessionLocal()
    try:
        logger.info(f"[Scheduler] 定时触发任务 task_id={task_id}")
        run_task(db, task_id, trigger_type="cron")
    except Exception as e:
        logger.error(f"[Scheduler] 任务 {task_id} 执行失败: {e}")
    finally:
        db.close()


def load_all_jobs():
    """从数据库加载所有启用的 cron 任务"""
    db: Session = SessionLocal()
    try:
        tasks = (
            db.query(SyncTask)
            .filter(
                SyncTask.enabled == True,
                SyncTask.trigger_type == TriggerType.CRON,
            )
            .all()
        )
        for task in tasks:
            add_job(task)
        logger.info(f"[Scheduler] 已加载 {len(tasks)} 个定时任务")
    finally:
        db.close()


def add_job(task: SyncTask):
    """添加或更新一个定时任务"""
    job_id = f"task_{task.id}"
    # 先移除旧的（如果存在）
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    if task.enabled and task.cron_expr:
        scheduler.add_job(
            _run_task_job,
            trigger=CronTrigger.from_crontab(task.cron_expr, timezone="Asia/Shanghai"),
            id=job_id,
            args=[task.id],
            replace_existing=True,
        )
        logger.info(f"[Scheduler] 注册任务 {task.name} cron={task.cron_expr}")


def remove_job(task_id: int):
    """移除一个定时任务"""
    job_id = f"task_{task_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"[Scheduler] 移除任务 job_id={job_id}")


def start():
    load_all_jobs()
    scheduler.start()
    logger.info("[Scheduler] 调度器已启动")


def stop():
    scheduler.shutdown(wait=False)
    logger.info("[Scheduler] 调度器已停止")