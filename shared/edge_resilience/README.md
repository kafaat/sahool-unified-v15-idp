# shared/edge_resilience — Edge Hardware Resilience (ADR-014)

> **Status:** Skeleton (Phase 3). No runtime logic yet. See
> [ADR-014](../../docs/adr/ADR-014-edge-hardware-resilience.md).

Reusable primitives for edge devices (Jetson Orin and similar) consumed by
`apps/services/edge-orchestrator-service` (port 8180) and, optionally, by
`shared/mobile_sync/` for device-side persistence.

## Modules

| File              | Responsibility                                                  |
| ----------------- | --------------------------------------------------------------- |
| `models.py`       | `PowerState`, `WALEntry`, `BackpressureLevel`, `ResilienceConfig` |
| `power_monitor.py`| Subscribes to GPIO/sysfs power-good signals; emits `SHUTDOWN_SOON` |
| `wal.py`          | Append-only WAL with `O_DSYNC` + `fdatasync` barriers           |
| `backpressure.py` | 80/60 % hysteresis controller for ingestion stall / resume      |

## Capability detection

Supercap presence is detected via `EDGE_SUPERCAP_GPIO` — if unset, the
`PowerMonitor` runs in **best-effort** mode (still flushes WAL, no
shutdown grace window). This keeps the package usable on commodity edge
hardware while letting Jetson + supercap deployments get the full SLA.

## Env vars (planned)

| Var                       | Default              | Meaning                             |
| ------------------------- | -------------------- | ----------------------------------- |
| `EDGE_WAL_PATH`           | `/var/sahool/wal`    | eMMC path for append-only segments  |
| `EDGE_WAL_MAX_BYTES`      | `1073741824` (1 GiB) | Rotation threshold                  |
| `EDGE_SUPERCAP_GPIO`      | unset                | GPIO line index for power-good      |
| `EDGE_BACKPRESSURE_HIGH`  | `0.80`               | Stall ingestion above this fill     |
| `EDGE_BACKPRESSURE_LOW`   | `0.60`               | Resume ingestion below this fill    |

## Metrics (planned, Prometheus)

- `edge_wal_fill_ratio`
- `edge_wal_fsync_seconds` (histogram)
- `edge_wal_replay_seconds` (histogram)
- `edge_backpressure_events_total`
- `edge_supercap_shutdown_seconds` (histogram)
