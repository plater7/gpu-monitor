# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-19

### Added

- **Fan mode detection** for GPUs with zero-RPM mode (#5)
  - New `fan_mode` field in `/api/gpu` response
  - Detects `active`, `stopped`, `not_supported`, and `unknown` states
- **Host PID namespace** support in Docker (#7)
  - Container now sees all host GPU processes
  - PIDs match `nvidia-smi` output

### Fixed

- `used_gpu_memory_bytes` now returns `0` instead of `null` when unavailable
- GPU processes endpoint now lists all host processes (not just container processes)

### Changed

- Improved README with badges, better structure, and more examples
- Added AI-assisted development attribution

## [1.0.0] - 2025-01-15

### Added

- Initial release
- FastAPI backend with NVML integration
- Temperature monitoring endpoint
- Fan speed monitoring endpoint
- GPU processes listing endpoint
- Web dashboard with Chart.js temperature history
- Docker support with NVIDIA Container Toolkit
- Live auto-refresh every 5 seconds

[1.1.0]: https://github.com/plater7/gpu-monitor/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/plater7/gpu-monitor/releases/tag/v1.0.0
