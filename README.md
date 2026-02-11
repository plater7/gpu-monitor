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

La API queda disponible en `http://localhost:8001`.

## Endpoints

| Metodo | Ruta          | Descripcion                              |
|--------|---------------|------------------------------------------|
| GET    | `/api/health` | Healthcheck                              |
| GET    | `/api/gpu`    | Temperatura y fan speed de la GPU (JSON) |

## Ejemplo de respuesta

```bash
curl http://localhost:8001/api/gpu
```

```json
{
  "temperature_c": 45,
  "fan_speed_percent": 30
}
```

## Licencia

MIT
