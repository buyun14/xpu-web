# main.py (更新版)
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from xpu_utils import get_devices, get_stats, get_health

app = FastAPI(
    title="Intel XPU Web Monitor",
    description="Web interface for xpu-smi based on FastAPI",
    version="0.1.0"
)

# 模板设置
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/devices")
async def list_devices():
    devices = get_devices()
    if not devices:
        raise HTTPException(status_code=500, detail="No GPU devices found")
    return {"devices": devices}

@app.get("/stats/{device_id}")
async def device_stats(device_id: str):
    stats = get_stats(device_id)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Stats for device {device_id} not available")
    return stats

@app.get("/health/{device_id}")
async def device_health(device_id: str):
    health = get_health(device_id)
    if not health:
        raise HTTPException(status_code=404, detail=f"Health info for device {device_id} not available")
    return health