import subprocess
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


@app.get("/api/gpu/processes")
def gpu_processes():
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-compute-apps=pid,process_name,used_gpu_memory",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        compute_lines = result.stdout.strip().splitlines() if result.stdout.strip() else []

        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-graphics-apps=pid,process_name,used_gpu_memory",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        graphics_lines = result.stdout.strip().splitlines() if result.stdout.strip() else []

        seen = {}
        for line in compute_lines + graphics_lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                continue
            pid = int(parts[0])
            if pid in seen:
                continue
            name = parts[1] if parts[1] != "[N/A]" else "unknown"
            try:
                mem = int(parts[2]) * 1024 * 1024
            except (ValueError, TypeError):
                mem = 0
            seen[pid] = {
                "pid": pid,
                "name": name,
                "used_gpu_memory_bytes": mem,
            }

        return {"processes": list(seen.values())}
    except Exception as e:
        return {"error": str(e)}
