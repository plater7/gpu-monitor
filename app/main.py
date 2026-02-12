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
    NVML_TEMPERATURE_GPU,
    NVMLError,
)

app = FastAPI(title="GPU Monitor")

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
        fan_speed = nvmlDeviceGetFanSpeed(handle)
        return {
            "temperature_c": temperature,
            "fan_speed_percent": fan_speed,
        }
    except NVMLError as e:
        return {"error": str(e)}
