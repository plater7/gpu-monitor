# GPU Monitor

Aplicacion web dockerizada de monitoreo de GPU usando NVIDIA Container Toolkit.

Expone una API REST (FastAPI) que reporta temperatura y velocidad de fans de la GPU en tiempo real, corriendo dentro de un container con acceso directo al hardware NVIDIA via NVML.

## Requisitos

- Docker con [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) instalado
- GPU NVIDIA con drivers instalados en el host

Configurar Docker para usar el runtime de NVIDIA:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Para rootless Docker:

```bash
nvidia-ctk runtime configure --runtime=docker --config=$HOME/.config/docker/daemon.json
```

## Como correrlo

```bash
docker compose up --build
```

La app queda disponible en `http://localhost:8001`.

## Frontend

Dashboard web con metricas en tiempo real accesible en `/`. Muestra cards con temperatura y fan speed de la GPU, con auto-refresh cada 5 segundos. Incluye un grafico de linea (Chart.js) con el historial de temperatura.

## Endpoints

| Metodo | Ruta          | Descripcion                              |
|--------|---------------|------------------------------------------|
| GET    | `/`           | Dashboard web con metricas en tiempo real |
| GET    | `/api/health`         | Healthcheck                               |
| GET    | `/api/gpu`            | Temperatura y fan speed de la GPU (JSON)  |
| GET    | `/api/gpu/processes`  | Procesos activos en la GPU (PID y nombre) |

## Ejemplos de respuesta

```bash
curl http://localhost:8001/api/gpu
```

```json
{
  "temperature_c": 45,
  "fan_speed_percent": 30
}
```

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
    }
  ]
}
```

## Notas

El container usa `pid: host` en docker-compose para compartir el PID namespace del host. Esto permite que NVML vea todos los procesos del sistema que usan la GPU (no solo los del container).

## Licencia

MIT
