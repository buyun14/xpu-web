# xpu_utils.py
import subprocess
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def run_xpu_cmd(args: List[str]) -> str:
    """执行 xpu-smi 命令并返回 stdout"""
    try:
        cmd = ["xpu-smi"] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logger.error(f"xpu-smi {' '.join(args)} failed: {result.stderr}")
            return ""
        return result.stdout.strip()
    except Exception as e:
        logger.exception(f"Failed to run xpu-smi: {e}")
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