"""
drone-service - Drone integration and management - تكامل وإدارة الطائرات المسيرة
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="drone-service",
    description="Drone integration and management - تكامل وإدارة الطائرات المسيرة",
    version="16.0.0",
    lifespan=lifespan,
)


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "drone-service", "version": "16.0.0"}


@app.get("/readyz")
def readiness():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "service": "drone-service",
        "version": "16.0.0",
        "description": "Drone integration and management - تكامل وإدارة الطائرات المسيرة",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8126")))
