import os
from fastapi import FastAPI
from fastapi.responses import Response
import structlog
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

SERVICE_NAME = os.getenv("SERVICE_NAME", "{{name}}")
SERVICE_LAYER = os.getenv("SERVICE_LAYER", "{{layer}}")

log = structlog.get_logger()
REQS = Counter(
    "http_requests_total", "Total HTTP requests", ["service", "path", "method"]
)

app = FastAPI(title=SERVICE_NAME)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/readyz")
def readyz():
    return {"status": "ready", "service": SERVICE_NAME}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root():
    REQS.labels(SERVICE_NAME, "/", "GET").inc()
    log.info("hello", service=SERVICE_NAME, layer=SERVICE_LAYER)
    return {"service": SERVICE_NAME, "layer": SERVICE_LAYER}
