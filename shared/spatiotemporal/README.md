# shared/spatiotemporal — Spatio-Temporal Sensor Fusion (ADR-011)

> **Status:** Phase 4 — implemented. Alignment, cubic-spline interpolation,
> EKF, and dense-Cholesky factor-graph batch optimizer are live with unit
> tests. See [ADR-011](../../docs/adr/ADR-011-spatiotemporal-fusion.md).

This package will host the math primitives used by `digital-twin-engine`
(port 8253) for physics-grade spatio-temporal fusion of heterogeneous
agricultural sensor streams.

## Modules

| File              | Responsibility                                                 |
| ----------------- | -------------------------------------------------------------- |
| `models.py`       | Value objects: `SensorFrame`, `FusedState`, `FusionConfig`     |
| `alignment.py`    | Sliding-window time alignment of ±500 ms across sensor streams |
| `interpolation.py`| Cubic-spline resampling                                        |
| `ekf.py`          | Full Extended Kalman Filter (state, covariance, Jacobians)     |
| `factor_graph.py` | Factor-graph batch optimizer (dense pure-Python Cholesky)      |

## Boundaries (do not cross)

- **No I/O.** All functions are pure: `(inputs) → (outputs, diagnostics)`.
- **No NATS / DB calls.** The `digital-twin-engine` adapts these primitives
  to the network edge and emits `sahool.twin.fusion.completed`
  (tenant-scoped via `shared/events/subjects.py::get_tenant_subject`).
- **Backward compatible.** `shared/digital_twin/assimilation.py` (Kalman-lite)
  remains available as a fallback for low-resource edge deployments,
  selected by the `SPATIOTEMPORAL_FUSION_MODE` env var (`lite` | `full`).

## Test plan (Phase 4)

- Golden datasets in `tests/golden-datasets/spatiotemporal/`
- Numerical regression vs. analytical solutions for linear cases
- Property tests: idempotence, covariance positive-semidefiniteness
