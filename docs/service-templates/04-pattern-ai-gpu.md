# 04 · Python AI / GPU Inference Template

**Gold standard:** `apps/services/yolo26-vision-service/`
**Use when:** the service needs CUDA / GPU / heavy-weight ML models
(YOLO, ONNX, PyTorch, TensorRT, vLLM, LLMs).

> قالب خدمات الذكاء الاصطناعي بطبقة GPU — نماذج ثقيلة وتسريع CUDA.

---

## Why `yolo26-vision-service`?

- **5-stage Dockerfile** (base · builder · production · development · cpu-only) —
  the only production template on the platform showing a dual
  GPU/CPU build.
- NVIDIA CUDA 12.1 + cuDNN8 runtime base image with a clean fallback
  to `python:3.11-slim-bookworm` for CPU-only environments.
- LRU model cache (5 models max in memory) with warm-up endpoint.
- 7 detection tasks × 5 model variants (n / s / m / l / x) share the
  same infrastructure — shows how to multiplex related models in one
  service.
- **26 typed error codes** across 8 categories, all bilingual
  (EN / AR).
- Circuit-breaker + retry pattern for external calls.
- FP16 half-precision + optional TensorRT optimization wired through
  env vars — no code changes required.

Other reasonable picks for this pattern family:
- `copilot-api` — multi-LLM router + RAG (use when the workload is
  text, not vision).
- `ground-vision-service` — ground-level image analysis (shallower
  than yolo26).

---

## Delta from Pattern 02 (FastAPI CRUD)

AI/GPU services are a **superset** of Pattern 02 with the following
mandatory additions. Keep everything else (lifespan, middleware,
error envelope, structlog, `/healthz`, `/readyz`, NATS) identical.

### 1 · Base image: `nvidia/cuda`, not `python:slim`

```dockerfile
ARG CUDA_VERSION=12.1.1
ARG CUDNN_VERSION=8
FROM nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-runtime-ubuntu22.04 AS base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3.11 python3.11-venv python3.11-dev python3-pip \
      libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 \
    && ln -sf /usr/bin/python3.11 /usr/local/bin/python \
    && rm -rf /var/lib/apt/lists/*
```

### 2 · CPU fallback stage

Offer a second `FROM python:3.11-slim-bookworm AS cpu-only` stage so
CI, airgapped environments, and laptops without a GPU can still build
and run the service. Select via `docker build --target cpu-only`.

### 3 · Model manager

```
src/
├── main.py
├── models/
│   ├── manager.py          # load / unload / LRU cache
│   ├── registry.py         # known versions + checksums
│   └── <task>_model.py     # wraps one ultralytics/onnx model
├── inference/
│   └── pipeline.py         # resize → run → post-process → NMS
```

**Non-negotiables:**

- Models loaded **lazily** on first request — startup must stay fast
  (< 5 s) so K8s readiness doesn't flap.
- LRU cap via env (`MODEL_CACHE_SIZE=5`) — out-of-memory is the #1
  cause of GPU service outages.
- Warm-up endpoint `/api/v1/models/warmup` pre-loads a named list so a
  canary deploy can hit the first request fast.
- Model files live in a **separate volume** (`/app/models`) so the
  container image doesn't balloon to multi-GB.
- Every inference response includes `{model_variant, model_version,
  inference_ms, device}`.

### 4 · GPU awareness

```python
import torch

def device() -> str:
    want = os.getenv("DEVICE", "cuda:0")
    if want.startswith("cuda") and not torch.cuda.is_available():
        logger.warning("cuda_requested_but_unavailable_falling_back_to_cpu")
        return "cpu"
    return want
```

Export a Prometheus gauge for `gpu_memory_used_mb`, `gpu_utilization_pct`,
`model_cache_size`.

### 5 · Batch-size limits & concurrency

- Max **upload size** = `MAX_UPLOAD_SIZE_MB` env (default 50).
- Max **batch** = `MAX_BATCH_SIZE` env (default 16).
- Max **concurrent inferences** (a semaphore) so PyTorch doesn't OOM
  under a burst.

### 6 · Timeouts

GPU inference is slower than DB queries — every endpoint has an
explicit `asyncio.wait_for(..., timeout=INFERENCE_TIMEOUT_S)` wrapper
that returns `504` with the bilingual timeout error code.

### 7 · Error codes

Use the yolo26 scheme or a parallel one. 26 codes across 8 categories:
Validation (E1xxx), Model (E2xxx), Processing (E3xxx), Resource
(E4xxx), External (E5xxx), Rate limit (E6xxx), Timeout (E7xxx), Auth
(E8xxx). Every code must have `{code, message, message_ar, http_status}`
registered in a single `errors.py`.

### 8 · Events

Publish only **high-signal** events — do NOT publish one event per
inference. Typical subjects:

```
sahool.vision.pest_detected           # only if detection count > 0
sahool.vision.critical.alert          # RPW, locust, etc.
sahool.vision.analysis_completed      # batch jobs only
```

### 9 · Testing

- Unit tests mock the model manager — no GPU required.
- **Golden dataset** tests (in `tests/golden-datasets/`) verify
  inference determinism on a canonical image set. These SHOULD run
  with a real GPU in a nightly CI job, not on every PR.
- Load / throughput tests with Locust or k6 — target 10 concurrent
  inferences at P95 < 500 ms on the reference hardware.

### 10 · Ops

- Resource requests in Helm: `nvidia.com/gpu: 1`, `memory: 8Gi`,
  `cpu: 2` minimum.
- `nodeSelector: accelerator: nvidia` in staging/prod.
- Separate `Deployment` per model-family — don't share pods across
  unrelated workloads.
- Grafana dashboard: GPU util, model latency histogram, cache hit
  rate, OOM count.

---

## Coverage matrix

| Service | GPU base image | LRU cache | Warm-up endpoint | Bilingual errors | Golden dataset | Last audit |
|---|---|---|---|---|---|---|
| yolo26-vision-service | ✅ gold | ✅ | ✅ | 26 codes | ✅ | 2026-03 |
| ground-vision-service | ✅ | — | — | partial | — | — |
| copilot-api | 🚫 (LLM-only) | ✅ multi-LLM | — | ✅ | — | — |
| llm-orchestrator-service | 🚫 (routing) | — | — | ✅ | — | — |
| ai-advisor | 🚫 | — | — | ✅ | — | — |
| vllm-deepseek | ✅ | n/a | — | — | — | — |
