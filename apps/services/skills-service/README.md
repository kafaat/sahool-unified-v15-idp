# SAHOOL Skills Service

**Version**: 16.0.0
**Port**: 8110

## Overview

The Skills Service manages AI model skill compression, memory storage/recall, and performance evaluation for the SAHOOL platform. This service provides capabilities for:

- **Skill Compression**: Reduce skill data size while maintaining functionality
- **Memory Management**: Store and recall skills with TTL support
- **Performance Evaluation**: Assess skill performance against configured metrics

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python src/main.py

# Service will be available at http://localhost:8110
```

### Docker

```bash
# Build
docker build -t sahool-skills-service .

# Run
docker run -p 8110:8110 \
  -e ENVIRONMENT=development \
  -e LOG_LEVEL=INFO \
  sahool-skills-service
```

### Docker Compose

```bash
# From project root
make dev

# Service starts automatically on port 8110
```

## API Endpoints

### Health Checks

- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe
- `GET /` - Service information

### Core Endpoints

#### 1. Compress Skill
```http
POST /compress
Content-Type: application/json

{
  "skill_id": "model-v1-compress",
  "skill_data": {
    "weights": [...],
    "config": {...}
  },
  "compression_level": 6,
  "target_size_kb": 512
}
```

**Response**: `CompressResponse` with compression metrics

#### 2. Store Skill in Memory
```http
POST /memory/store
Content-Type: application/json

{
  "skill_id": "model-v1",
  "namespace": "inference",
  "skill_data": {...},
  "ttl_seconds": 3600,
  "metadata": {
    "version": "1.0",
    "algorithm": "transformer"
  }
}
```

**Response**: `MemoryStoreResponse` with storage confirmation

#### 3. Recall Skill from Memory
```http
POST /memory/recall
Content-Type: application/json

{
  "skill_id": "model-v1",
  "namespace": "inference",
  "include_metadata": true
}
```

**Response**: `MemoryRecallResponse` with skill data if found

#### 4. Evaluate Skill
```http
POST /evaluate
Content-Type: application/json

{
  "skill_id": "model-v1",
  "input_data": {
    "text": "sample input"
  },
  "expected_output": {
    "prediction": "expected value"
  },
  "metrics": ["accuracy", "latency", "memory"]
}
```

**Response**: `EvaluateResponse` with performance metrics

## Architecture

### Service Stack

- **Framework**: FastAPI 0.115.5
- **Server**: Uvicorn
- **Serialization**: Pydantic v2.10+
- **Testing**: pytest, pytest-asyncio
- **Caching**: Redis (token revocation, optional in-memory)

### Data Flow

```
Client Request
    ↓
[Middleware: Request ID, Token Revocation]
    ↓
[Route Handler]
    ↓
[Business Logic]
    ↓
[Response]
```

## Configuration

### Environment Variables

| Variable        | Default       | Description              |
| --------------- | ------------- | ------------------------ |
| `PORT`          | `8110`        | Service port             |
| `ENVIRONMENT`   | `development` | Environment mode         |
| `LOG_LEVEL`     | `INFO`        | Logging level            |
| `REDIS_URL`     | (optional)    | Redis connection URL     |

### Docker Compose Variables

```bash
# From .env
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_compress.py -v
```

### Test Markers

- `@pytest.mark.unit` - Fast, no I/O
- `@pytest.mark.integration` - API/database tests
- `@pytest.mark.slow` - Long-running tests

## Security

### Authentication

- JWT token validation via `get_current_user` dependency
- Token revocation support (Redis-backed)
- Exempt paths: `/healthz`, `/readyz`, `/docs`

### Input Validation

- All request bodies validated with Pydantic
- Type hints enforce schema compliance
- Custom validators for business rules

### Container Security

- Non-root user (sahool)
- Read-only root filesystem (optional)
- No privilege escalation
- Resource limits configured

## Monitoring

### Health Endpoints

Both return `status: "ok"` when healthy:

```bash
curl http://localhost:8110/healthz
curl http://localhost:8110/readyz
```

### Logs

Structured JSON logging for observability:

```bash
# View logs
docker logs sahool-skills-service

# Follow logs
docker logs -f sahool-skills-service
```

## Development

### Project Structure

```
skills-service/
├── Dockerfile              # Container definition
├── .dockerignore           # Docker build exclusions
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── src/
│   ├── __init__.py
│   └── main.py             # FastAPI app + endpoints
└── tests/
    └── (test files)
```

### Code Style

- Python 3.11+
- Type hints required
- Pydantic models for validation
- Structured logging

### Adding Endpoints

1. Create request/response models in `main.py`
2. Add route handler with `@app.post()` or `@app.get()`
3. Include authentication if needed: `user: User = Depends(get_current_user)`
4. Add tests in `tests/`

### Adding Dependencies

1. Update `requirements.txt`
2. Rebuild: `docker build .`
3. Or reinstall locally: `pip install -r requirements.txt`

## Troubleshooting

### Service won't start

```bash
# Check logs
docker logs sahool-skills-service

# Verify port is available
lsof -i :8110

# Test connection
curl http://localhost:8110/healthz
```

### High memory usage

- Check compression level settings
- Monitor skill data sizes
- Review TTL configuration for memory storage
- Use evaluation metrics to optimize

## Performance Tuning

### Compression

- Lower `compression_level` for faster compression
- Higher `compression_level` for better compression ratio
- Use `target_size_kb` for size-constrained scenarios

### Memory

- Set appropriate `ttl_seconds` (avoid accumulation)
- Use namespaces to organize skills
- Monitor Redis memory usage

## References

- **Main Docs**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

## License

Proprietary - KAFAAT 2024-2026

---

**Service Owner**: KAFAAT Team
**Last Updated**: January 2026
