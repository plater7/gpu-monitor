import re
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
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip() or "nvidia-smi failed"}

        processes = []
        seen = set()
        for match in re.finditer(
            r"\|\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\w+\s+(.+?)\s+(\d+)\s*MiB\s*\|",
            result.stdout,
        ):
            pid = int(match.group(1))
            if pid in seen:
                continue
            seen.add(pid)
            processes.append({
                "pid": pid,
                "name": match.group(2).strip(),
                "used_gpu_memory_bytes": int(match.group(3)) * 1024 * 1024,
            })

        return {"processes": processes}
    except Exception as e:
        return {"error": str(e)}
