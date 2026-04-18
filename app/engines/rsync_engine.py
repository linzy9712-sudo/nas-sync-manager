import subprocess
import re
import shutil
from app.engines.base import BaseEngine, SyncContext, SyncResult
from app.models.task import SyncMode


class RsyncEngine(BaseEngine):
    """
    基于 rsync 的同步引擎，用于 NAS → NAS 局域网同步
    """

    def sync(self, ctx: SyncContext) -> SyncResult:
        cmd = self._build_command(ctx)
        return self._execute(cmd)

    def test_connection(self, ctx: SyncContext) -> tuple[bool, str]:
        """测试 rsync 目标是否可达"""
        if not shutil.which("rsync"):
            return False, "rsync 未安装"

        if ctx.host:
            # 远程目标：尝试列出目录
            cmd = self._build_base_cmd(ctx)
            cmd += ["--list-only", f"{ctx.auth_user}@{ctx.host}:{ctx.target_path}"]
        else:
            # 本地目标：检查目录是否存在
            import os
            if os.path.exists(ctx.target_path):
                return True, "本地目标路径可访问"
            else:
                return False, f"本地路径不存在: {ctx.target_path}"

        result = self._execute(cmd)
        if result.success:
            return True, "连接成功"
        return False, result.error_msg or "连接失败"

    def _build_command(self, ctx: SyncContext) -> list[str]:
        cmd = self._build_base_cmd(ctx)

        # 同步模式
        if ctx.sync_mode == SyncMode.MIRROR:
            cmd.append("--delete")          # 源删除，目标也删除
            cmd.append("--delete-excluded") # 排除的文件也删除

        elif ctx.sync_mode == SyncMode.INCREMENTAL:
            cmd.append("--backup")          # 保留被覆盖的旧文件
            cmd.append("--suffix=.bak")

        # 试运行
        if ctx.dry_run:
            cmd.append("--dry-run")

        # 额外参数
        cmd.extend(ctx.extra_args)

        # 源路径（末尾加 / 表示同步目录内容而非目录本身）
        source = ctx.source_path.rstrip("/") + "/"

        # 目标路径
        if ctx.host:
            target = f"{ctx.auth_user}@{ctx.host}:{ctx.target_path}"
        else:
            target = ctx.target_path

        cmd += [source, target]
        return cmd

    def _build_base_cmd(self, ctx: SyncContext) -> list[str]:
        cmd = [
            "rsync",
            "-avz",          # archive + verbose + compress
            "--progress",    # 显示进度
            "--stats",       # 输出统计信息（用于解析文件数/字节数）
            "--checksum",    # 用校验和判断文件变化（更准确）
        ]

        # SSH 认证
        if ctx.host:
            ssh_opt = "ssh"
            if ctx.ssh_key_path:
                ssh_opt += f" -i {ctx.ssh_key_path}"
            cmd += ["-e", ssh_opt]

        return cmd

    def _execute(self, cmd: list[str]) -> SyncResult:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 最长1小时
            )
            output = proc.stdout + proc.stderr
            files, size = self._parse_output(proc.stdout)

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
                error_msg="同步超时（超过1小时）",
                return_code=-1,
            )
        except Exception as e:
            return SyncResult(
                success=False,
                error_msg=str(e),
                return_code=-1,
            )

    def _parse_output(self, output: str) -> tuple[int, int]:
        """解析 rsync --stats 输出"""
        files = 0
        size = 0

        # Number of regular files transferred: 12
        m = re.search(r"Number of regular files transferred:\s+(\d+)", output)
        if m:
            files = int(m.group(1))

        # Total transferred file size: 1,234,567 bytes
        m = re.search(r"Total transferred file size:\s+([\d,]+)\s+bytes", output)
        if m:
            size = int(m.group(1).replace(",", ""))

        return files, size