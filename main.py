# main.py
from fastapi import FastAPI, HTTPException
from xpu_utils import get_devices, get_stats, get_health

app = FastAPI(
    title="Intel XPU Web Monitor",
    description="Web interface for xpu-smi based on FastAPI",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Intel XPU Web Monitor", "docs": "/docs"}

@app.get("/devices")
async def list_devices():
    """列出所有 GPU 设备"""
    devices = get_devices()
    if not devices:
        raise HTTPException(status_code=500, detail="No GPU devices found or xpu-smi error")
    return {"devices": devices}

@app.get("/stats/{device_id}")
async def device_stats(device_id: str):
    """获取指定设备的实时统计"""
    stats = get_stats(device_id)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Device {device_id} stats not available")
    return stats

@app.get("/health/{device_id}")
async def device_health(device_id: str):
    """获取设备健康状态"""
    health = get_health(device_id)
    if not health:
        raise HTTPException(status_code=404, detail=f"Device {device_id} health info not available")
    return health