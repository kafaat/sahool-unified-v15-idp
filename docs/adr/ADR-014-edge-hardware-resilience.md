# ADR-014: Edge Hardware Resilience (supercap + crash-safe WAL)

## Status

Proposed

## Context

SAHOOL edge devices (Jetson Orin and similar) operate in environments with
unreliable power and intermittent connectivity. v3.1 requires:

- Power-loss tolerance via **supercapacitor**-driven graceful shutdown (≥ 5 s budget)
- **Crash-safe write-ahead log** (WAL) flushed to eMMC with `fsync` barriers
- Backpressure and compaction policy when uplink to cloud is unavailable
- Jittered exponential retry on resume

v16 has `apps/services/edge-orchestrator-service/` (port 8180) and
`shared/mobile_sync/` for offline sync, but neither implements supercap-aware
shutdown or `fsync`-bounded WAL persistence. Phase 1 (row #14) flagged this
as 🔴 with no equivalent asset.

## Decision

Extend `edge-orchestrator-service` with:

- A pluggable **PowerMonitor** (`shared/edge_resilience/power_monitor.py`)
  that subscribes to GPIO / sysfs power-good signals and emits a `SHUTDOWN_SOON`
  event when supercap discharge starts
- A WAL writer (`shared/edge_resilience/wal.py`) that:
  - Writes append-only frames to eMMC with `O_DSYNC` + `fdatasync` barriers
  - Rotates and compacts segments when free space falls below threshold
  - Replays on startup before reconnecting to NATS
- A **backpressure controller** that stalls high-rate sensor ingestion when
  WAL fill > 80 % and resumes when < 60 % (hysteresis)
- Jittered retry with full-jitter exponential backoff on uplink resume

No new service. Edge devices that lack a supercap fall back to a "best-effort"
mode (still flushes WAL, but no shutdown grace window).

## Consequences

### Positive

- Power-loss does not corrupt the local sensor record
- Sensor data is replayable end-to-end (edge → cloud) after any outage
- Backpressure prevents OOM / thrash on long disconnects
- Centralized policy in `shared/edge_resilience/` lets the mobile app (`shared/mobile_sync`)
  reuse the same WAL primitives

### Negative

- `fsync` barriers cost ~5–15 ms per flush on eMMC; sustained ingestion rate
  drops accordingly. Mitigated by batched writes (configurable batch size)
- Requires per-device hardware capability detection (supercap presence is
  not standard); a config-driven feature flag is added

### Neutral

- New env vars: `EDGE_WAL_PATH`, `EDGE_WAL_MAX_BYTES`, `EDGE_SUPERCAP_GPIO`,
  `EDGE_BACKPRESSURE_HIGH`, `EDGE_BACKPRESSURE_LOW`
- New Prometheus metrics: WAL fill, fsync latency, replay duration, backpressure events

## Alternatives Considered

### Alternative 1: Rely on SQLite WAL mode only

Rejected. SQLite WAL is process-local and does not coordinate with NATS resume
or with supercap shutdown signaling. We would still need a higher-level
controller — which is exactly what this ADR adds.

### Alternative 2: New dedicated `edge-resilience-service`

Rejected. The resilience controller has to live in the same process that owns
the local socket / NATS client; splitting it off would re-introduce IPC and
make `fsync` barriers harder to reason about.

### Alternative 3: Cloud-side compensation (idempotent replay only)

Insufficient. Cloud-side idempotency is necessary but does not prevent local
data loss between the sensor read and the WAL write; only `fsync` does.

## References

- [Phase 1 Gap Analysis row #14](../architecture/GAP_ANALYSIS_v3.1_vs_v16.md)
- `apps/services/edge-orchestrator-service/`
- `shared/mobile_sync/`
- ADR-001: Offline-First Mobile Architecture
