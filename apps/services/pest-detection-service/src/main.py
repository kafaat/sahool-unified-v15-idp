"""
pest-detection-service - Pest detection and management - كشف الآفات وإدارتها
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield

app = FastAPI(
    title="pest-detection-service",
    description="Pest detection and management - كشف الآفات وإدارتها",
    version="16.0.0",
    lifespan=lifespan,
)

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "pest-detection-service", "version": "16.0.0"}

@app.get("/readyz")
def readiness():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "service": "pest-detection-service",
        "version": "16.0.0",
        "description": "Pest detection and management - كشف الآفات وإدارتها",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8125")))
