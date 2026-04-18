import subprocess
import re
import shutil
from app.engines.base import BaseEngine, SyncContext, SyncResult
from app.models.task import SyncMode


class RcloneEngine(BaseEngine):
    """
    基于 rclone 的同步引擎，用于 NAS → 百度网盘等云存储同步
    """

    def sync(self, ctx: SyncContext) -> SyncResult:
        cmd = self._build_command(ctx)
        return self._execute(cmd)

    def test_connection(self, ctx: SyncContext) -> tuple[bool, str]:
        """测试 rclone remote 是否可用"""
        if not shutil.which("rclone"):
            return False, "rclone 未安装"

        if not ctx.remote_name:
            return False, "未配置 remote_name"

        cmd = ["rclone", "lsd", f"{ctx.remote_name}:{ctx.target_path}", "--max-depth", "1"]
        result = self._execute(cmd)
        if result.success:
            return True, "连接成功"
        return False, result.error_msg or "连接失败"

    def _build_command(self, ctx: SyncContext) -> list[str]:
        # rclone 子命令选择
        if ctx.sync_mode == SyncMode.MIRROR:
            sub_cmd = "sync"   # 完全同步（会删除目标多余文件）
        else:
            sub_cmd = "copy"   # 只复制，不删除目标文件

        cmd = [
            "rclone", sub_cmd,
            "--progress",           # 显示进度
            "--stats-one-line",     # 单行统计
            "--transfers", "4",     # 并发传输数
            "--checkers", "8",      # 并发检查数
            "--retries", "3",       # 失败重试次数
            "--low-level-retries", "10",
            "-v",                   # verbose 输出
        ]

        # 增量备份模式：在目标保留旧版本
        if ctx.sync_mode == SyncMode.INCREMENTAL:
            cmd += ["--backup-dir", f"{ctx.remote_name}:backup-history"]

        # 试运行
        if ctx.dry_run:
            cmd.append("--dry-run")

        # 额外参数
        cmd.extend(ctx.extra_args)

        # 源路径
        source = ctx.source_path

        # 目标路径：remote_name:path
        target = f"{ctx.remote_name}:{ctx.target_path}"

        cmd += [source, target]
        return cmd

    def _execute(self, cmd: list[str]) -> SyncResult:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=7200  # 最长2小时（云盘可能慢）
            )
            output = proc.stdout + proc.stderr
            files, size = self._parse_output(output)

            return SyncResult(
                success=proc.returncode == 0,
                files_transferred=files,
                bytes_transferred=size,
                output=output,
                error_msg=proc.stderr if proc.returncode != 0 else None,
                return_code=proc.returncode,
            )
        except subprocess.TimeoutExpired:
            return SyncResult(
                success=False,
                error_msg="同步超时（超过2小时）",
                return_code=-1,
            )
        except Exception as e:
            return SyncResult(
                success=False,
                error_msg=str(e),
                return_code=-1,
            )

    def _parse_output(self, output: str) -> tuple[int, int]:
        """解析 rclone 输出统计"""
        files = 0
        size = 0

        # Transferred: 12 / 12, 100%
        m = re.search(r"Transferred:\s+(\d+)\s*/", output)
        if m:
            files = int(m.group(1))

        # Transferred: 1.234 GBytes (...)  或  1,234 Bytes
        m = re.search(r"Transferred:\s+[\d.]+ \w+,\s+([\d.]+)\s+(\w+)", output)
        if m:
            val = float(m.group(1))
            unit = m.group(2).upper()
            unit_map = {"BYTES": 1, "KBYTES": 1024, "MBYTES": 1024**2, "GBYTES": 1024**3}
            size = int(val * unit_map.get(unit, 1))

        return files, size