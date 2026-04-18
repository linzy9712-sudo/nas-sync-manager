from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from app.models.task import SyncMode


@dataclass
class SyncResult:
    """同步执行结果，统一格式"""
    success: bool
    files_transferred: int = 0
    bytes_transferred: int = 0
    output: str = ""
    error_msg: Optional[str] = None
    return_code: int = 0


@dataclass
class SyncContext:
    """同步执行上下文，传入引擎的参数"""
    source_path: str
    target_path: str
    sync_mode: SyncMode

    # rsync 专用
    host: Optional[str] = None
    auth_user: Optional[str] = None
    auth_pass: Optional[str] = None
    ssh_key_path: Optional[str] = None

    # rclone 专用
    remote_name: Optional[str] = None

    # 额外选项
    dry_run: bool = False           # 试运行，不实际执行
    extra_args: list = field(default_factory=list)


class BaseEngine(ABC):
    """同步引擎抽象基类"""

    @abstractmethod
    def sync(self, ctx: SyncContext) -> SyncResult:
        """执行同步，返回结果"""
        pass

    @abstractmethod
    def test_connection(self, ctx: SyncContext) -> tuple[bool, str]:
        """测试连接，返回 (是否成功, 消息)"""
        pass

    def _parse_output(self, output: str) -> tuple[int, int]:
        """
        从输出中解析传输文件数和字节数
        子类可以重写此方法
        返回 (files_transferred, bytes_transferred)
        """
        return 0, 0