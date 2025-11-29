import subprocess
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def run_xpu_cmd(args: List[str]) -> str:
    """
    执行底层 XPU 管理 CLI 命令并返回 stdout。

    默认优先使用 XPU Manager 提供的 `xpumcli`，在不存在时回退到旧的 `xpu-smi`，
    这样在只安装 XPU Manager 或只安装 xpu-smi 的环境中都可以正常工作。
    """
    for base_cmd in ("xpumcli", "xpu-smi"):
        try:
            cmd = [base_cmd] + args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.error(f"{base_cmd} {' '.join(args)} failed: {result.stderr}")
                # 如果 xpumcli 失败，再尝试 xpu-smi；如果已经是 xpu-smi，则直接返回空
                if base_cmd == "xpumcli":
                    continue
                return ""
            return result.stdout.strip()
        except FileNotFoundError:
            # 当前 CLI 不存在，尝试下一个
            logger.debug("%s not found in PATH, try next CLI", base_cmd)
            continue
        except Exception as e:
            logger.exception("Failed to run %s: %s", base_cmd, e)
            # 发生异常时，如果是 xpumcli 则回退到 xpu-smi；如果已经是 xpu-smi 则终止
            if base_cmd == "xpumcli":
                continue
            return ""

    # 两个 CLI 都不可用
    logger.error("Neither xpumcli (XPU Manager) nor xpu-smi is available in PATH")
    return ""

def parse_discovery_output(output: str) -> List[Dict[str, Any]]:
    """解析 discovery 的 JSON 输出"""
    try:
        data = json.loads(output)
        return data.get("device_list", [])
    except json.JSONDecodeError:
        return []

def get_devices() -> List[Dict[str, Any]]:
    """获取 GPU 设备列表（JSON 格式）"""
    output = run_xpu_cmd(["discovery", "-j"])
    return parse_discovery_output(output)

def get_stats(device_id: str = "0") -> Dict[str, Any]:
    """获取指定设备的统计信息（JSON）"""
    output = run_xpu_cmd(["stats", "-d", device_id, "-j"])
    try:
        return json.loads(output) if output else {}
    except json.JSONDecodeError:
        return {}

def get_health(device_id: str = "0") -> Dict[str, Any]:
    """获取设备健康状态"""
    output = run_xpu_cmd(["health", "-d", device_id, "-j"])
    try:
        return json.loads(output) if output else {}
    except json.JSONDecodeError:
        return {}


def get_processes(device_id: str = "0") -> Dict[str, Any]:
    """获取正在使用 GPU 的进程信息（JSON）"""
    output = run_xpu_cmd(["ps", "-d", device_id, "-j"])
    try:
        return json.loads(output) if output else {}
    except json.JSONDecodeError:
        return {}