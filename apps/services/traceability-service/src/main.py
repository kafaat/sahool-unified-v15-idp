"""
Traceability Service - خدمة التتبع
Product traceability and supply chain tracking
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield

app = FastAPI(
    title="Traceability Service",
    description="Product traceability and supply chain tracking - تتبع المنتجات وسلسلة التوريد",
    version="16.0.0",
    lifespan=lifespan,
)

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "traceability-service", "version": "16.0.0"}

@app.get("/readyz")
def readiness():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "service": "traceability-service",
        "version": "16.0.0",
        "description": "Product traceability and supply chain tracking",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8123")))
