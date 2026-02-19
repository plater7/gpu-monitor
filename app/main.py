"""
GPU Monitor - FastAPI application for NVIDIA GPU monitoring.
AI-assisted development with OpenCode.
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pynvml import (
    nvmlInit,
    nvmlShutdown,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetTemperature,
    nvmlDeviceGetFanSpeed,
    nvmlDeviceGetNumFans,
    nvmlDeviceGetComputeRunningProcesses,
    nvmlDeviceGetGraphicsRunningProcesses,
    nvmlSystemGetProcessName,
    nvmlDeviceGetClockInfo,
    NVML_TEMPERATURE_GPU,
    NVML_CLOCK_GRAPHICS,
    NVML_CLOCK_MEM,
    NVMLError,
)

app = FastAPI(
    title="GPU Monitor",
    description="Real-time NVIDIA GPU monitoring via NVML",
    version="1.2.0",
)

static_dir = Path(__file__).parent / "static"
data_dir = Path("/data")
data_dir.mkdir(exist_ok=True)
db_path = data_dir / "alerts.db"

app.mount("/static", StaticFiles(directory=static_dir), name="static")


class Alert(BaseModel):
    alert_type: str
    metric: str
    value: float
    threshold: float
    severity: str = "warning"


def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            metric TEXT NOT NULL,
            value REAL NOT NULL,
            threshold REAL NOT NULL,
            severity TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    nvmlInit()
    init_db()


@app.on_event("shutdown")
def shutdown():
    nvmlShutdown()


@app.get("/")
def dashboard():
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/gpu")
def gpu_metrics():
    try:
        handle = nvmlDeviceGetHandleByIndex(0)
        temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)

        fan_speed, fan_mode = _get_fan_info(handle)
        
        gpu_clock = _get_clock_safe(handle, NVML_CLOCK_GRAPHICS)
        mem_clock = _get_clock_safe(handle, NVML_CLOCK_MEM)

        response = {
            "temperature_c": temperature,
            "fan_speed_percent": fan_speed,
            "fan_mode": fan_mode,
            "gpu_clock_mhz": gpu_clock,
            "memory_clock_mhz": mem_clock,
        }
        return response
    except NVMLError as e:
        return {"error": str(e)}


def _get_fan_info(handle):
    try:
        num_fans = nvmlDeviceGetNumFans(handle)
    except NVMLError:
        num_fans = 0

    if num_fans == 0:
        return None, "not_supported"

    try:
        fan_speed = nvmlDeviceGetFanSpeed(handle)
        if fan_speed == 0:
            return 0, "stopped"
        return fan_speed, "active"
    except NVMLError:
        return None, "unknown"


def _get_clock_safe(handle, clock_type):
    try:
        return nvmlDeviceGetClockInfo(handle, clock_type)
    except NVMLError:
        return None


@app.get("/api/gpu/processes")
def gpu_processes():
    try:
        handle = nvmlDeviceGetHandleByIndex(0)
        compute = nvmlDeviceGetComputeRunningProcesses(handle)
        graphics = nvmlDeviceGetGraphicsRunningProcesses(handle)

        seen = {}
        for proc in compute + graphics:
            if proc.pid in seen:
                continue
            try:
                name = nvmlSystemGetProcessName(proc.pid)
            except NVMLError:
                name = "unknown"

            used_memory = proc.usedGpuMemory
            if used_memory is None:
                used_memory = 0

            seen[proc.pid] = {
                "pid": proc.pid,
                "name": name,
                "used_gpu_memory_bytes": used_memory,
            }

        return {"processes": list(seen.values())}
    except NVMLError as e:
        return {"error": str(e)}


@app.post("/api/alerts")
def create_alert(alert: Alert):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO alert_history (timestamp, alert_type, metric, value, threshold, severity) VALUES (?, ?, ?, ?, ?, ?)",
        (timestamp, alert.alert_type, alert.metric, alert.value, alert.threshold, alert.severity)
    )
    conn.commit()
    conn.close()
    return {"status": "created", "timestamp": timestamp}


@app.get("/api/alerts")
def get_alerts(limit: int = 100):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM alert_history ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return {
        "alerts": [
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "alert_type": row["alert_type"],
                "metric": row["metric"],
                "value": row["value"],
                "threshold": row["threshold"],
                "severity": row["severity"],
            }
            for row in rows
        ]
    }
