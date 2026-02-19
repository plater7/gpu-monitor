"""
GPU Monitor - FastAPI application for NVIDIA GPU monitoring.
AI-assisted development with OpenCode.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
    NVML_TEMPERATURE_GPU,
    NVMLError,
)

app = FastAPI(
    title="GPU Monitor",
    description="Real-time NVIDIA GPU monitoring via NVML",
    version="1.1.0",
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
def startup():
    nvmlInit()


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

        response = {
            "temperature_c": temperature,
            "fan_speed_percent": fan_speed,
            "fan_mode": fan_mode,
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
