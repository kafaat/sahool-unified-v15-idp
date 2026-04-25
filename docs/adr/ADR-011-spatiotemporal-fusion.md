# ADR-011: Spatio-Temporal Fusion via Digital-Twin Extension

## Status

Accepted (2026-04-25, Phase 4 complete: align_streams + resample_cubic + EKF + FactorGraph + 22 unit tests)

## Context

The v3.1 target architecture requires physics-grade spatio-temporal fusion across
heterogeneous sensors (drone imagery, IoT soil/weather sensors, satellite NDVI,
ground vision) with:

- Full Extended Kalman Filter (EKF) — not Kalman-lite
- Factor-graph optimization (g2o-style) for batch refinement
- Sliding-window time alignment of ±500 ms across sensor streams
- Cubic-spline interpolation for resampling

The v16 codebase already provides:

- `shared/digital_twin/assimilation.py` — Kalman-lite / EnKF-lite primitives
- `apps/services/digital-twin-engine/` (port 8253) — running service with NATS
  integration and tenant-scoped subjects
- `shared/digital_twin/` — twin state model

The Phase 1 Gap Analysis
([GAP_ANALYSIS_v3.1_vs_v16.md](../architecture/GAP_ANALYSIS_v3.1_vs_v16.md), row #4)
reclassified this gap from 🔴 (new service) to 🟠 (extend existing).

## Decision

Implement spatio-temporal fusion as an **extension of `digital-twin-engine`**,
backed by a new module `shared/spatiotemporal/`. No new service.

- `shared/spatiotemporal/ekf.py` — full EKF (state, covariance, process & obs Jacobians)
- `shared/spatiotemporal/factor_graph.py` — factor-graph optimizer (sparse Cholesky)
- `shared/spatiotemporal/alignment.py` — sliding-window time alignment ±500 ms
- `shared/spatiotemporal/interpolation.py` — cubic-spline resampling
- `digital-twin-engine` exposes new endpoints under `/api/v1/twin/fusion/*` and
  publishes `sahool.twin.fusion.completed` (tenant-scoped via `get_tenant_subject`)
- Existing `assimilation.py` Kalman-lite path is preserved as a fallback for
  low-resource edge deployments

## Consequences

### Positive

- Zero new service to operate, deploy, observe, or secure
- Reuses existing tenant-scoped NATS subjects, JWT auth, `/healthz` `/readyz` `/metrics`
- The `shared/spatiotemporal/` module is reusable by `edge-orchestrator-service`
  for on-device fusion when bandwidth is low
- Backward compatible: Kalman-lite remains available behind a feature flag

### Negative

- `digital-twin-engine` grows in code size and CPU footprint; vertical scaling
  may be required for large tenants
- Factor-graph optimization is non-trivial to test deterministically; requires
  golden datasets

### Neutral

- Factor-graph optimization and KD-tree nearest-neighbor support are
  implemented in pure Python in this phase, so no new `scipy.sparse`,
  `scikit-sparse`, or `sksparse` container dependencies are introduced
- Public API surface grows but no existing endpoint changes

## Alternatives Considered

### Alternative 1: New `spatiotemporal-fusion-service`

Originally proposed in the earlier draft. Rejected because:

- `digital-twin-engine` already owns the twin state and assimilation loop;
  splitting fusion off would introduce a chatty inter-service call on every
  sensor frame (latency + NATS load)
- Doubles the operational surface (deploy, RBAC, secrets, dashboards, alerts)
  for what is essentially a math library
- Risks state divergence between the twin and the fusion service

### Alternative 2: Keep Kalman-lite only

Rejected because v3.1 explicitly requires factor-graph batch refinement and
±500 ms alignment, which Kalman-lite cannot provide.

## References

- [Phase 1 Gap Analysis row #4](../architecture/GAP_ANALYSIS_v3.1_vs_v16.md)
- `shared/digital_twin/assimilation.py`
- `apps/services/digital-twin-engine/`
- `shared/events/subjects.py::get_tenant_subject`
