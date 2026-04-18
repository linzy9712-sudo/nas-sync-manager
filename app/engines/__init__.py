from app.engines.base import BaseEngine, SyncContext, SyncResult
from app.engines.rsync_engine import RsyncEngine
from app.engines.rclone_engine import RcloneEngine
from app.models.target import TargetType


class SyncEngineFactory:
    """根据目标类型返回对应的同步引擎"""

    _engines = {
        TargetType.RSYNC: RsyncEngine,
        TargetType.RCLONE: RcloneEngine,
    }

    @classmethod
    def get_engine(cls, target_type: TargetType) -> BaseEngine:
        engine_cls = cls._engines.get(target_type)
        if not engine_cls:
            raise ValueError(f"不支持的同步类型: {target_type}")
        return engine_cls()


__all__ = [
    "SyncEngineFactory",
    "SyncContext",
    "SyncResult",
    "BaseEngine",
]