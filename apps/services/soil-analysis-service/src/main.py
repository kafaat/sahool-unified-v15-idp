"""
soil-analysis-service - Soil analysis and recommendations - تحليل التربة والتوصيات
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield

app = FastAPI(
    title="soil-analysis-service",
    description="Soil analysis and recommendations - تحليل التربة والتوصيات",
    version="16.0.0",
    lifespan=lifespan,
)

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "soil-analysis-service", "version": "16.0.0"}

@app.get("/readyz")
def readiness():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "service": "soil-analysis-service",
        "version": "16.0.0",
        "description": "Soil analysis and recommendations - تحليل التربة والتوصيات",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8124")))
