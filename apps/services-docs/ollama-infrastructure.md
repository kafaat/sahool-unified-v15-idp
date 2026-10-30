# Ollama AI Infrastructure Analysis

## Overview

The SAHOOL platform integrates Ollama as a local LLM server to provide AI-powered code analysis, code review, and advisory capabilities. This infrastructure enables offline-capable AI features essential for the platform's low-connectivity agricultural environments.

**Service**: Ollama Local LLM Server
**Image**: `ollama/ollama:0.5.4`
**Profile**: `gpu` (requires NVIDIA GPU)
**Port**: 11434
**Container Name**: `sahool-ollama`

---

## Architecture

```
+------------------+     +---------------------+     +-------------------------+
|  code-review-    |     |   ollama            |     |   ollama-model-loader   |
|  service         |---->|   (LLM Server)      |<----|   (Model Downloader)    |
|  Port: 8102      |     |   Port: 11434       |     |   curl-based init       |
+------------------+     +---------------------+     +-------------------------+
         |                        |
         v                        v
+------------------+     +---------------------+
|  shared/ai/      |     |   ollama_data       |
|  ollama_client   |     |   (Docker Volume)   |
+------------------+     +---------------------+
```

---

## Docker Configuration

### Ollama Service (Main LLM Server)

```yaml
ollama:
  profiles:
    - gpu
  image: ollama/ollama:0.5.4
  container_name: sahool-ollama
  volumes:
    - ollama_data:/root/.ollama
  ports:
    - "127.0.0.1:11434:11434"
  environment:
    - OLLAMA_HOST=0.0.0.0
    - OLLAMA_ORIGINS=${OLLAMA_ORIGINS:-*}
    - OLLAMA_KEEP_ALIVE=24h
    - OLLAMA_NUM_PARALLEL=24
    - OLLAMA_MAX_LOADED_MODELS=2
    - OLLAMA_NUM_GPU=${OLLAMA_NUM_GPU:-1}
    - CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
    - OLLAMA_GPU_LAYERS=${OLLAMA_GPU_LAYERS:-999}
  healthcheck:
    test: ["CMD-SHELL", "ollama list || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
      reservations:
        cpus: '1'
        memory: 2G
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

### Ollama Model Loader (Initialization Service)

```yaml
ollama-model-loader:
  profiles:
    - gpu
  image: curlimages/curl:8.11.1
  container_name: sahool-ollama-model-loader
  depends_on:
    ollama:
      condition: service_healthy
  entrypoint: ["/bin/sh", "-c"]
  command:
    - |
      echo "Waiting for Ollama to be ready..."
      sleep 5
      echo "Pulling deepseek model..."
      curl -X POST http://ollama:11434/api/pull -d '{"name":"deepseek"}' --max-time 3600
      echo "Model download complete!"
      sleep 10
  restart: "no"
```

---

## Environment Variables

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `0.0.0.0` | Host address to bind to |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama server URL for client connections |
| `OLLAMA_MODEL` | `llama3.2` | Default model to use |
| `OLLAMA_ORIGINS` | `*` | CORS origins (restrict in production) |
| `OLLAMA_KEEP_ALIVE` | `24h` | How long to keep models loaded in memory |

### Parallelism & Performance

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_NUM_PARALLEL` | `24` | Number of parallel request handlers |
| `OLLAMA_MAX_LOADED_MODELS` | `2` | Maximum number of models loaded simultaneously |

### GPU Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_NUM_GPU` | `1` | Number of GPUs to use |
| `CUDA_VISIBLE_DEVICES` | `0` | GPU device IDs (use "0,1" for multiple GPUs) |
| `OLLAMA_GPU_LAYERS` | `999` | Number of layers to offload to GPU (999 = all) |

### Client Configuration (shared/ai/ollama_client.py)

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base URL for Ollama API client |
| `OLLAMA_DEFAULT_MODEL` | `codellama:13b` | Default model for code tasks |
| `OLLAMA_TIMEOUT` | `60` | Request timeout in seconds |

---

## Supported Models

### Pre-configured Models

| Model | Size | Use Case | Pulled By |
|-------|------|----------|-----------|
| `deepseek` / `deepseek-coder-v2` | 6.7B | Primary code review model | ollama-model-loader |
| `deepseek-coder` | 6.7B | Fallback code model | Manual/on-demand |
| `codellama` | 7B/13B | Code analysis and generation | Manual/on-demand |
| `starcoder` | 7B | Code generation | Manual/on-demand |
| `llama2` / `llama3.2` | 7B | Fast inference, general tasks | Manual/on-demand |
| `nomic-embed-text` | - | Embeddings for RAG | Optional init |
| `qwen2.5` / `qwen2.5-coder` | 7B | Multilingual including Arabic | Optional init |
| `mistral` | 7B | General purpose with code capabilities | Manual/on-demand |

### Model Loading Process

1. **Automatic Loading**: The `ollama-model-loader` container automatically pulls the `deepseek` model on startup
2. **On-Demand Loading**: Additional models are pulled via API when first requested
3. **Persistent Storage**: Models are stored in the `ollama_data` Docker volume at `/root/.ollama`

---

## GPU Requirements

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | NVIDIA GTX 1080 (8GB) | NVIDIA RTX 3090/4090 (24GB) |
| VRAM | 8GB | 16-24GB |
| System RAM | 16GB | 32GB |
| CUDA Version | 11.x | 12.x |

### Docker GPU Support

1. **NVIDIA Container Toolkit Required**:
   ```bash
   # Install NVIDIA Container Toolkit
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

2. **Verify GPU Access**:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
   ```

### Resource Allocation

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      cpus: '1'
      memory: 2G
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

---

## Integration with Code Review Service

### Service Configuration

The `code-review-service` is the primary consumer of Ollama:

**Location**: `/home/user/sahool-unified-v15-idp/apps/services/code-review-service/`

```yaml
code-review-service:
  profiles:
    - gpu
  environment:
    - OLLAMA_URL=http://ollama:11434
    - OLLAMA_MODEL=deepseek
    - WATCH_PATHS=infrastructure:docker-compose.yml:docker
    - LOG_LEVEL=INFO
    - REVIEW_ON_CHANGE=true
    - MAX_FILE_SIZE=1000000
    - API_HOST=0.0.0.0
    - API_PORT=8102
  depends_on:
    ollama:
      condition: service_healthy
```

### Multi-Model Fallback Configuration

The code-review-service supports automatic model fallback:

```python
# Primary model
ollama_url: str = "http://ollama:11434"
ollama_model: str = "deepseek-coder-v2"

# Fallback models (priority order)
fallback_models: str = "deepseek-coder@http://ollama:11434,codellama@http://ollama:11434,starcoder@http://ollama:11434,llama2@http://ollama:11434"

# Model selection strategy
model_strategy: str = "primary_first"  # Options: "primary_first", "round_robin", "fastest"
enable_fallback: bool = True
max_retries: int = 3
retry_delay: float = 1.0
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with model availability |
| `/models` | GET | List available LLM models |
| `/review` | POST | Review code content |
| `/review/file` | POST | Review a file from codebase |
| `/review/pr` | POST | Review GitHub Pull Request |
| `/cache/stats` | GET | Get cache statistics |
| `/cache/clear` | POST | Clear review cache |

---

## Shared AI Client Library

### Location

`/home/user/sahool-unified-v15-idp/shared/ai/ollama_client.py`

### OllamaClient Class

```python
from shared.ai.ollama_client import OllamaClient, OllamaConfig

# Initialize client
config = OllamaConfig(
    base_url="http://ollama:11434",
    default_model="codellama:13b",
    timeout=120.0,
    max_retries=3,
    retry_delay=1.0
)
client = OllamaClient(config)

# Check availability
if await client.is_available():
    # Generate response
    response = await client.generate(
        prompt="Review this code...",
        model="codellama:13b",
        system="You are an expert code reviewer",
        options={"temperature": 0.1}
    )
    print(response.response)
    print(f"Tokens/sec: {response.tokens_per_second}")
```

### Helper Functions

```python
from shared.ai.ollama_client import (
    analyze_code_with_ollama,
    fix_code_with_ollama,
    generate_tests_with_ollama
)

# Analyze code
analysis = await analyze_code_with_ollama(
    code="def foo(): pass",
    language="python",
    model="codellama:13b"
)

# Fix code
fixed = await fix_code_with_ollama(
    code="x= 1",
    error="E225 missing whitespace",
    language="python",
    model="deepseek-coder:6.7b"
)

# Generate tests
tests = await generate_tests_with_ollama(
    code="def add(a, b): return a + b",
    language="python",
    framework="pytest"
)
```

---

## Model Training Capabilities

### Location

`/home/user/sahool-unified-v15-idp/shared/ai/model_training.py`

### Dataset Types

| Type | Description |
|------|-------------|
| `CODE_FIX` | Error to fix pairs |
| `CODE_REVIEW` | Code to review pairs |
| `CODE_GENERATION` | Prompt to code pairs |
| `TEST_GENERATION` | Code to tests pairs |
| `AGRICULTURAL` | SAHOOL-specific advisory |

### Training Example

```python
from shared.ai.model_training import (
    DatasetBuilder,
    ModelTrainer,
    TrainingConfig
)

# Build dataset
builder = DatasetBuilder()
builder.add_code_fix_example(
    original="x= 1",
    fixed="x = 1",
    error_message="E225 missing whitespace"
)
builder.add_agricultural_advisory_example(
    query="When should I irrigate wheat?",
    response="Irrigate every 10-14 days during tillering",
    crop_type="wheat"
)

dataset = builder.build(
    name="sahool-fixes",
    name_ar="fixes sahool"
)

# Train model
trainer = ModelTrainer(ollama_url="http://ollama:11434")
config = TrainingConfig(
    base_model="codellama:7b",
    output_model="sahool-codefix:latest",
    epochs=3
)

job = await trainer.create_training_job(dataset, config)
job = await trainer.start_training(job.id)

print(f"Accuracy: {job.evaluation_result.accuracy:.2%}")
```

---

## Health Monitoring

### Health Check Configuration

```yaml
healthcheck:
  test: ["CMD-SHELL", "ollama list || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

### API Health Endpoints

| Endpoint | Response |
|----------|----------|
| `GET /api/tags` | List of loaded models |
| `GET /api/ps` | Running model processes |
| `GET /api/version` | Ollama version info |

### Monitoring via Code-Review-Service

```json
{
  "status": "healthy",
  "service": "code-review-service",
  "ollama_connected": true,
  "available_models": ["deepseek-coder-v2", "codellama"],
  "cache_enabled": true,
  "github_enabled": false,
  "version": "2.0.0"
}
```

### Prometheus Metrics

The code-review-service exposes metrics including:
- Model availability status
- Request latency by model
- Cache hit/miss rates
- Review score distribution

---

## Recommended Optimizations

### 1. Production Security

```yaml
environment:
  # Restrict CORS to specific origins
  - OLLAMA_ORIGINS=https://sahool.app,https://api.sahool.app
```

### 2. Memory Management

```yaml
environment:
  # Reduce keep-alive for memory-constrained environments
  - OLLAMA_KEEP_ALIVE=1h

  # Limit loaded models
  - OLLAMA_MAX_LOADED_MODELS=1
```

### 3. GPU Optimization

```yaml
environment:
  # Force all layers to GPU (prevents CPU fallback)
  - OLLAMA_GPU_LAYERS=999

  # For multi-GPU systems
  - CUDA_VISIBLE_DEVICES=0,1
  - OLLAMA_NUM_GPU=2
```

### 4. High Concurrency

```yaml
environment:
  # Increase parallel handlers for high load
  - OLLAMA_NUM_PARALLEL=32
```

### 5. Model Pre-loading

Create a custom init script to pre-load multiple models:

```bash
#!/bin/sh
# Pull primary model
curl -X POST http://ollama:11434/api/pull -d '{"name":"deepseek-coder-v2"}'

# Pull embeddings model for RAG
curl -X POST http://ollama:11434/api/pull -d '{"name":"nomic-embed-text"}'

# Pull Arabic-capable model
curl -X POST http://ollama:11434/api/pull -d '{"name":"qwen2.5:7b"}'

# Warm up primary model
curl -X POST http://ollama:11434/api/generate -d '{"model":"deepseek-coder-v2","prompt":"Hello","stream":false}'
```

### 6. Caching Strategy

Configure code-review-service caching:

```python
# Enable Redis cache for distributed deployments
cache_backend: str = "redis"
redis_url: str = "redis://redis:6379/2"
cache_ttl: int = 3600  # 1 hour
```

### 7. Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      cpus: '1'
      memory: 2G
```

---

## Startup Commands

### Start with GPU Profile

```bash
# Full GPU stack
docker compose --profile gpu up -d

# GPU services only
docker compose --profile gpu up -d ollama ollama-model-loader code-review-service
```

### Alternative: CPU-Only Mode

Use the dedicated Ollama compose file for CPU-only deployments:

```bash
docker compose -f infrastructure/core/ollama/docker-compose.ollama.yml --profile cpu up -d
```

### Initialize Additional Models

```bash
# Pull additional models via API
curl -X POST http://localhost:11434/api/pull -d '{"name":"codellama:13b"}'
curl -X POST http://localhost:11434/api/pull -d '{"name":"qwen2.5-coder:7b"}'
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Container fails to start | Missing NVIDIA driver | Install nvidia-container-toolkit |
| Model download timeout | Network issues | Increase `--max-time` in model-loader |
| OOM (Out of Memory) | Model too large | Use smaller model or increase VRAM |
| Slow inference | CPU fallback | Set `OLLAMA_GPU_LAYERS=999` |
| CORS errors | Restricted origins | Configure `OLLAMA_ORIGINS` |

### Debug Commands

```bash
# Check container logs
docker logs sahool-ollama

# Verify GPU access
docker exec sahool-ollama nvidia-smi

# List loaded models
docker exec sahool-ollama ollama list

# Check model info
docker exec sahool-ollama ollama show deepseek-coder-v2

# Test API
curl http://localhost:11434/api/tags
```

---

## Related Files

| File | Purpose |
|------|---------|
| `/home/user/sahool-unified-v15-idp/docker-compose.yml` | Main Docker Compose with Ollama services |
| `/home/user/sahool-unified-v15-idp/infrastructure/core/ollama/docker-compose.ollama.yml` | Dedicated Ollama compose with CPU/GPU profiles |
| `/home/user/sahool-unified-v15-idp/shared/ai/ollama_client.py` | Python client library |
| `/home/user/sahool-unified-v15-idp/shared/ai/model_training.py` | Model training capabilities |
| `/home/user/sahool-unified-v15-idp/apps/services/code-review-service/` | Primary Ollama consumer service |
| `/home/user/sahool-unified-v15-idp/.env.example` | Environment variable templates |

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01 | 16.0.0 | Ollama 0.5.4, DeepSeek model, multi-model fallback |
| 2026-01 | 2.0.0 | Code review service with caching and GitHub integration |

---

*Last Updated: January 2026*
