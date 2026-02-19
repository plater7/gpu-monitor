# GPU Monitor

<p align="center">
  <img src="https://img.shields.io/badge/NVIDIA-GPU-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="NVIDIA GPU">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/plater7/gpu-monitor?style=flat-square" alt="License">
  <img src="https://img.shields.io/github/stars/plater7/gpu-monitor?style=flat-square" alt="Stars">
  <img src="https://img.shields.io/github/issues/plater7/gpu-monitor?style=flat-square" alt="Issues">
  <img src="https://img.shields.io/github/actions/workflow/status/plater7/gpu-monitor/ci.yml?branch=main&style=flat-square" alt="CI Status">
</p>

> Real-time NVIDIA GPU monitoring dashboard with REST API

A Dockerized web application for monitoring NVIDIA GPUs using the NVIDIA Container Toolkit. Exposes a FastAPI REST API reporting temperature, fan speed, and running processes in real-time, running inside a container with direct hardware access via NVML.

---

## Features

- **Real-time Dashboard** - Live GPU metrics with auto-refresh
- **Temperature Monitoring** - Current temp + historical chart
- **Fan Speed Detection** - Smart zero-RPM mode detection
- **Process Listing** - See all GPU processes (PIDs, names, memory)
- **REST API** - Clean JSON endpoints for integration
- **Docker Ready** - One-command deployment

---

## Requirements

- **Docker** with [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- **NVIDIA GPU** with drivers installed on host

Configure Docker for NVIDIA runtime:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

For rootless Docker:

```bash
nvidia-ctk runtime configure --runtime=docker --config=$HOME/.config/docker/daemon.json
```

---

## Quick Start

```bash
docker compose up --build
```

Access the dashboard at **http://localhost:8001**

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web dashboard with live metrics |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/gpu` | GPU temperature and fan info |
| `GET` | `/api/gpu/processes` | Active GPU processes |

### Examples

**Get GPU metrics:**
```bash
curl http://localhost:8001/api/gpu
```

```json
{
  "temperature_c": 54,
  "fan_speed_percent": 0,
  "fan_mode": "stopped"
}
```

**Fan modes:**
- `"active"` - Fans spinning
- `"stopped"` - Zero-RPM mode (fans idle)
- `"not_supported"` - GPU has no fans (e.g., datacenter cards)
- `"unknown"` - Unable to determine

**Get GPU processes:**
```bash
curl http://localhost:8001/api/gpu/processes
```

```json
{
  "processes": [
    {
      "pid": 1234,
      "name": "/usr/bin/python3",
      "used_gpu_memory_bytes": 524288000
    },
    {
      "pid": 5678,
      "name": "/usr/lib/firefox/firefox",
      "used_gpu_memory_bytes": 209715200
    }
  ]
}
```

---

## Screenshots

The dashboard features:
- Temperature card with live updates
- Fan speed card with mode indicator
- Temperature history chart (60-point rolling window)
- Connection status indicator

---

## Development

### Project Structure

```
gpu-monitor/
├── app/
│   ├── main.py         # FastAPI application
│   └── static/
│       └── index.html  # Dashboard frontend
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Local Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

---

## License

[MIT](LICENSE)

---

<p align="center">
  <sub>Built with 🤖 AI assistance by <a href="https://github.com/features/copilot">OpenCode</a></sub>
</p>
