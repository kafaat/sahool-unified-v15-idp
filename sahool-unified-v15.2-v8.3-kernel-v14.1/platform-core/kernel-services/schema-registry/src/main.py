"""
Schema Registry Service
Layer 1: Platform Core

المسؤول عن حوكمة وإدارة مخططات الأحداث
Manages event schemas with versioning and validation

Key Responsibilities:
1. Store and serve JSON schemas
2. Validate events against schemas
3. Handle schema versioning
4. Track schema compatibility
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, List
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import jsonschema
from jsonschema import validate, ValidationError

# Add shared to path
sys.path.insert(0, '/app')
from shared.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging(service_name="schema-registry")
logger = get_logger(__name__)

# Configuration
SERVICE_NAME = "schema-registry"
SERVICE_LAYER = "platform-core"
SCHEMAS_DIR = Path("/app/shared/schemas")


# ============================================
# Schema Storage
# ============================================

class SchemaStore:
    """In-memory schema storage with file backing"""
    
    def __init__(self, schemas_dir: Path):
        self.schemas_dir = schemas_dir
        self.schemas: Dict[str, Dict[str, dict]] = {}  # domain -> version -> schema
        self.metadata: Dict[str, dict] = {}  # schema_id -> metadata
    
    def load_from_disk(self):
        """Load all schemas from disk"""
        if not self.schemas_dir.exists():
            logger.warning("schemas_dir_missing", path=str(self.schemas_dir))
            return
        
        for domain_dir in self.schemas_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                self.schemas[domain] = {}
                
                for schema_file in domain_dir.glob("*.json"):
                    try:
                        with open(schema_file) as f:
                            schema = json.load(f)
                        
                        version = schema.get("version", "1.0.0")
                        event_type = schema.get("$id", schema_file.stem)
                        
                        self.schemas[domain][version] = schema
                        
                        schema_id = f"{domain}.{event_type}"
                        self.metadata[schema_id] = {
                            "domain": domain,
                            "event_type": event_type,
                            "version": version,
                            "file": str(schema_file),
                            "loaded_at": datetime.utcnow().isoformat()
                        }
                        
                        logger.info("schema_loaded", 
                                   domain=domain, 
                                   event_type=event_type,
                                   version=version)
                    
                    except Exception as e:
                        logger.error("schema_load_failed", 
                                    file=str(schema_file), 
                                    error=str(e))
        
        total = sum(len(v) for v in self.schemas.values())
        logger.info("schemas_loaded", total=total)
    
    def get_schema(self, domain: str, version: str = "latest") -> Optional[dict]:
        """Get schema by domain and version"""
        if domain not in self.schemas:
            return None
        
        versions = self.schemas[domain]
        if not versions:
            return None
        
        if version == "latest":
            # Return highest version
            latest = max(versions.keys())
            return versions[latest]
        
        return versions.get(version)
    
    def register_schema(self, domain: str, schema: dict) -> dict:
        """Register a new schema"""
        if domain not in self.schemas:
            self.schemas[domain] = {}
        
        version = schema.get("version", "1.0.0")
        event_type = schema.get("$id", "unknown")
        
        # Check compatibility with existing versions
        if self.schemas[domain]:
            # Simple check: ensure new version is higher
            existing_versions = list(self.schemas[domain].keys())
            if version in existing_versions:
                raise ValueError(f"Version {version} already exists")
        
        self.schemas[domain][version] = schema
        
        schema_id = f"{domain}.{event_type}"
        self.metadata[schema_id] = {
            "domain": domain,
            "event_type": event_type,
            "version": version,
            "registered_at": datetime.utcnow().isoformat()
        }
        
        logger.info("schema_registered", domain=domain, version=version)
        
        return self.metadata[schema_id]
    
    def validate_event(self, event: dict) -> dict:
        """Validate an event against its schema"""
        event_type = event.get("event_type", "")
        schema_version = event.get("schema_version", "1.0.0")
        
        # Parse domain from event_type (e.g., "astro.star.rising" -> "astro")
        parts = event_type.split(".")
        if not parts:
            return {"valid": False, "error": "Invalid event_type"}
        
        domain = parts[0]
        schema = self.get_schema(domain, schema_version)
        
        if not schema:
            return {
                "valid": False,
                "error": f"No schema found for domain '{domain}' version '{schema_version}'"
            }
        
        try:
            validate(instance=event, schema=schema)
            return {"valid": True, "schema_version": schema_version}
        except ValidationError as e:
            return {
                "valid": False,
                "error": str(e.message),
                "path": list(e.path)
            }
    
    def list_schemas(self) -> List[dict]:
        """List all registered schemas"""
        return list(self.metadata.values())


# ============================================
# Global Store
# ============================================

store = SchemaStore(SCHEMAS_DIR)


# ============================================
# FastAPI Application
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("service_starting", layer=SERVICE_LAYER)
    
    # Load schemas from disk
    store.load_from_disk()
    
    logger.info("service_started")
    yield
    logger.info("service_stopped")


app = FastAPI(
    title="Schema Registry",
    description="SAHOOL Platform - Event Schema Management",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# API Models
# ============================================

class RegisterSchemaRequest(BaseModel):
    domain: str
    schema_def: dict


class ValidateEventRequest(BaseModel):
    event: dict


# ============================================
# API Endpoints
# ============================================

@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    schema_count = len(store.metadata)
    return {
        "status": "ready",
        "schemas_loaded": schema_count
    }


@app.get("/api/schemas")
async def list_schemas():
    """List all registered schemas"""
    return {"schemas": store.list_schemas()}


@app.get("/api/schemas/{domain}")
async def get_schema(domain: str, version: str = "latest"):
    """Get schema by domain"""
    schema = store.get_schema(domain, version)
    if not schema:
        raise HTTPException(404, f"Schema not found: {domain}@{version}")
    return schema


@app.post("/api/schemas")
async def register_schema(request: RegisterSchemaRequest):
    """Register a new schema"""
    try:
        # Validate the schema itself
        jsonschema.Draft7Validator.check_schema(request.schema_def)
        
        metadata = store.register_schema(request.domain, request.schema_def)
        return {"message": "Schema registered", "metadata": metadata}
    
    except jsonschema.SchemaError as e:
        raise HTTPException(400, f"Invalid JSON Schema: {e.message}")
    except ValueError as e:
        raise HTTPException(409, str(e))


@app.post("/api/validate")
async def validate_event(request: ValidateEventRequest):
    """Validate an event against its schema"""
    result = store.validate_event(request.event)
    
    if not result["valid"]:
        raise HTTPException(400, result)
    
    return result


@app.get("/api/schemas/{domain}/versions")
async def list_versions(domain: str):
    """List all versions of a schema"""
    if domain not in store.schemas:
        raise HTTPException(404, f"Domain not found: {domain}")
    
    versions = list(store.schemas[domain].keys())
    return {"domain": domain, "versions": sorted(versions)}


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("SCHEMA_REGISTRY_PORT", "8082")),
        reload=os.getenv("ENV") == "development"
    )
