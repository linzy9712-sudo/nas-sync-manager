import time
import threading
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.task import SyncTask, TriggerType
from app.services.sync_service import run_task

logger = logging.getLogger(__name__)

# 全局 observer
observer = Observer()

# 记录每个路径最后变动时间 {source_path: last_event_time}
_last_event: dict[str, float] = {}
_lock = threading.Lock()


class SyncEventHandler(FileSystemEventHandler):
    def __init__(self, task_id: int, source_path: str, delay_minutes: int):
        self.task_id = task_id
        self.source_path = source_path
        self.delay_seconds = delay_minutes * 60
        super().__init__()

    def on_any_event(self, event):
        if event.is_directory:
            return
        with _lock:
            _last_event[self.source_path] = time.time()
        logger.debug(f"[Watcher] 检测到变动: {event.src_path}")


def _watch_loop():
    """后台线程：定期检查是否有路径静止超过 delay 时间"""
    while True:
        time.sleep(30)  # 每30秒检查一次
        now = time.time()
        with _lock:
            snapshot = dict(_last_event)

        for source_path, last_time in snapshot.items():
            db: Session = SessionLocal()
            try:
                task = (
                    db.query(SyncTask)
                    .filter(
                        SyncTask.source_path == source_path,
                        SyncTask.trigger_type == TriggerType.WATCH,
                        SyncTask.enabled == True,
                    )
                    .first()
                )
                if not task:
                    continue

                delay_seconds = (task.watch_delay or 10) * 60
                if now - last_time >= delay_seconds:
                    logger.info(f"[Watcher] 路径静止超过 {task.watch_delay} 分钟，触发任务: {task.name}")
                    with _lock:
                        _last_event.pop(source_path, None)
                    run_task(db, task.id, trigger_type="watch")
            except Exception as e:
                logger.error(f"[Watcher] 触发任务失败: {e}")
            finally:
                db.close()


def load_all_watchers():
    """从数据库加载所有启用的 watch 任务"""
    db: Session = SessionLocal()
    try:
        tasks = (
            db.query(SyncTask)
            .filter(
                SyncTask.enabled == True,
                SyncTask.trigger_type == TriggerType.WATCH,
            )
            .all()
        )
        for task in tasks:
            add_watcher(task)
        logger.info(f"[Watcher] 已加载 {len(tasks)} 个文件监控任务")
    finally:
        db.close()


def add_watcher(task: SyncTask):
    """为任务添加文件监控"""
    path = Path(task.source_path)
    if not path.exists():
        logger.warning(f"[Watcher] 路径不存在，跳过监控: {task.source_path}")
        return

    handler = SyncEventHandler(
        task_id=task.id,
        source_path=task.source_path,
        delay_minutes=task.watch_delay or 10,
    )
    observer.schedule(handler, str(path), recursive=True)
    logger.info(f"[Watcher] 开始监控: {task.source_path}")


def start():
    load_all_watchers()
    observer.start()
    # 启动静止检测后台线程
    t = threading.Thread(target=_watch_loop, daemon=True)
    t.start()
    logger.info("[Watcher] 文件监控已启动")


def stop():
    observer.stop()
    observer.join()
    logger.info("[Watcher] 文件监控已停止")