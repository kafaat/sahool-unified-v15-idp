"""
cooperative-service - Cooperative management - إدارة التعاونيات
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="cooperative-service",
    description="Cooperative management - إدارة التعاونيات",
    version="16.0.0",
    lifespan=lifespan,
)


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "cooperative-service", "version": "16.0.0"}


@app.get("/readyz")
def readiness():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "service": "cooperative-service",
        "version": "16.0.0",
        "description": "Cooperative management - إدارة التعاونيات",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8127")))
