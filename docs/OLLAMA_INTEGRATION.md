# Ollama Integration Guide
# دليل تكامل Ollama

SAHOOL platform supports local LLM inference using [Ollama](https://ollama.ai/), enabling offline-first AI capabilities and reduced dependency on cloud providers.

## Overview | نظرة عامة

Ollama provides a way to run large language models locally, which is beneficial for:

- **Offline Operation**: Run AI features without internet connectivity
- **Cost Reduction**: No API costs for inference
- **Data Privacy**: Keep all data on-premises
- **Low Latency**: No network round-trips for inference
- **Arabic Support**: Use models optimized for Arabic like qwen2.5

## Quick Start | البدء السريع

### 1. Start Ollama with Docker

```bash
# CPU-only deployment
docker compose -f infrastructure/core/ollama/docker-compose.ollama.yml --profile cpu up -d

# GPU deployment (NVIDIA)
docker compose -f infrastructure/core/ollama/docker-compose.ollama.yml --profile gpu up -d

# Initialize with default models
docker compose -f infrastructure/core/ollama/docker-compose.ollama.yml --profile init up
```

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_KEEP_ALIVE=24h
OLLAMA_NUM_PARALLEL=2
OLLAMA_MAX_LOADED_MODELS=1

# For GPU deployments
OLLAMA_NUM_GPU=1
CUDA_VISIBLE_DEVICES=0
```

### 3. Use Ollama as Primary Provider

```bash
# In your environment
PRIMARY_LLM_PROVIDER=ollama
```

Or in code:

```python
from llm.multi_provider import MultiLLMService

# Use Ollama as primary (falls back to cloud if unavailable)
service = MultiLLMService(primary_provider="ollama")
```

## Architecture | البنية

```
┌─────────────────────────────────────────────────────────────┐
│                    SAHOOL Platform                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │   AI Advisor     │    │   RAG Service    │              │
│  │    Service       │    │                  │              │
│  └────────┬─────────┘    └────────┬─────────┘              │
│           │                       │                         │
│           ▼                       ▼                         │
│  ┌────────────────────────────────────────────┐            │
│  │         MultiLLMService                     │            │
│  │  (Automatic fallback between providers)     │            │
│  └─────────────────────┬──────────────────────┘            │
│                        │                                    │
│      ┌─────────────────┼─────────────────┐                 │
│      │                 │                 │                  │
│      ▼                 ▼                 ▼                  │
│  ┌────────┐      ┌──────────┐      ┌────────┐             │
│  │Ollama  │      │Anthropic │      │OpenAI  │             │
│  │(Local) │      │(Cloud)   │      │(Cloud) │             │
│  └────────┘      └──────────┘      └──────────┘            │
│      │                                                      │
│      ▼                                                      │
│  ┌────────────────┐                                        │
│  │  Local GPU/CPU │                                        │
│  └────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Supported Models | النماذج المدعومة

### Chat/Completion Models

| Model | Size | Use Case | Arabic Support |
|-------|------|----------|----------------|
| `llama3.2` | 3B/8B | General chat, fast responses | Partial |
| `llama3.1` | 8B/70B | Complex reasoning | Partial |
| `mistral` | 7B | Efficient, fast | Limited |
| `mixtral` | 8x7B | High quality responses | Limited |
| `qwen2.5` | 7B/14B/32B | **Excellent Arabic support** | ✅ Full |
| `codellama` | 7B/13B | Code generation | No |
| `phi3` | 3.8B | Compact, efficient | Limited |
| `gemma2` | 2B/9B | Google's open model | Limited |

### Embedding Models

| Model | Dimensions | Use Case |
|-------|------------|----------|
| `nomic-embed-text` | 768 | General embeddings, RAG |
| `mxbai-embed-large` | 1024 | High quality embeddings |
| `snowflake-arctic-embed` | 1024 | Retrieval-optimized |

## API Usage | استخدام الواجهة البرمجية

### Chat Completion

```python
from llm.multi_provider import OllamaProvider, LLMMessage

provider = OllamaProvider()

messages = [
    LLMMessage(role="system", content="You are an agricultural advisor"),
    LLMMessage(role="user", content="What is the best time to plant wheat?"),
]

response = await provider.chat(
    messages=messages,
    model="llama3.2",
    max_tokens=500,
    temperature=0.7
)

print(response.content)
print(f"Tokens used: {response.tokens_used}")
print(f"Latency: {response.latency_ms}ms")
```

### Text Generation

```python
response = await provider.generate(
    prompt="Describe the symptoms of wheat rust disease:",
    model="llama3.2",
    max_tokens=500
)
```

### Embeddings

```python
# Single text
embeddings = await provider.embeddings(
    "Agricultural irrigation best practices",
    model="nomic-embed-text"
)

# Batch embedding
texts = [
    "Wheat cultivation",
    "Tomato farming",
    "Date palm care"
]
embeddings = await provider.embeddings(texts)
```

### Model Management

```python
# List available models
models = await provider.list_models()
for model in models:
    print(f"{model['name']}: {model['size'] / 1e9:.1f}GB")

# Pull a new model
success = await provider.pull_model("qwen2.5:7b")
```

## Multi-Provider Fallback | التبديل التلقائي

SAHOOL uses automatic fallback between providers:

```python
from llm.multi_provider import MultiLLMService, LLMMessage

# Priority: Ollama -> Anthropic -> OpenAI -> Google
service = MultiLLMService(primary_provider="ollama")

result = await service.chat([
    LLMMessage(role="user", content="Hello")
])

print(f"Provider used: {result.provider}")
print(f"Failed providers: {result.failed_providers}")
```

## Docker Deployment | النشر باستخدام Docker

### CPU-Only Deployment

```yaml
# docker-compose.yml override
services:
  ollama:
    extends:
      file: infrastructure/core/ollama/docker-compose.ollama.yml
      service: ollama
    profiles:
      - cpu
```

### GPU Deployment

Requirements:
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit installed
- `nvidia-docker` or Docker with GPU support

```yaml
# docker-compose.yml override
services:
  ollama:
    extends:
      file: infrastructure/core/ollama/docker-compose.ollama.yml
      service: ollama-gpu
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          limits:
            nvidia.com/gpu: 1  # For GPU deployment
        volumeMounts:
        - name: ollama-models
          mountPath: /root/.ollama
      volumes:
      - name: ollama-models
        persistentVolumeClaim:
          claimName: ollama-models-pvc
```

## Performance Tuning | تحسين الأداء

### Memory Configuration

```bash
# Keep models loaded longer (reduces cold start)
OLLAMA_KEEP_ALIVE=24h

# Concurrent request handling
OLLAMA_NUM_PARALLEL=4  # CPU: 2-4, GPU: 8-24

# Limit loaded models (reduces memory)
OLLAMA_MAX_LOADED_MODELS=2
```

### GPU Optimization

```bash
# Use all GPU layers (faster but more VRAM)
OLLAMA_GPU_LAYERS=999

# Specify GPU device
CUDA_VISIBLE_DEVICES=0

# For multi-GPU setups
OLLAMA_NUM_GPU=2
```

### Response Time Optimization

1. **Pre-load models**: Keep models warm in memory
2. **Use smaller models**: llama3.2:3b vs llama3.2:8b for faster responses
3. **Batch requests**: Process multiple requests together
4. **Reduce max_tokens**: Limit response length

## Monitoring | المراقبة

### Health Check

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check loaded models
curl http://localhost:11434/api/ps
```

### Prometheus Metrics

Ollama exposes metrics that can be scraped:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
```

## Troubleshooting | استكشاف الأخطاء

### Common Issues

1. **Model not found**
   ```bash
   # Pull the model first
   docker exec sahool-ollama ollama pull llama3.2
   ```

2. **Out of memory**
   ```bash
   # Use smaller model or reduce context
   OLLAMA_MODEL=llama3.2:3b
   OLLAMA_MAX_LOADED_MODELS=1
   ```

3. **Slow response times**
   - Check if GPU is being used: `nvidia-smi`
   - Verify model is loaded: `curl http://localhost:11434/api/ps`
   - Consider smaller model

4. **Connection refused**
   ```bash
   # Check container is running
   docker ps | grep ollama

   # Check logs
   docker logs sahool-ollama
   ```

### Logs

```bash
# View Ollama logs
docker logs -f sahool-ollama

# Verbose logging
OLLAMA_DEBUG=1
```

## Security Considerations | اعتبارات الأمان

1. **Network Isolation**: Ollama is bound to localhost by default
2. **No Authentication**: Ollama API has no built-in auth
3. **Model Verification**: Verify model sources before pulling
4. **Resource Limits**: Set memory and GPU limits

```yaml
# docker-compose security settings
services:
  ollama:
    ports:
      - "127.0.0.1:11434:11434"  # Localhost only
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
```

## Cost Comparison | مقارنة التكلفة

| Provider | Cost per 1M tokens (input) | Cost per 1M tokens (output) |
|----------|---------------------------|----------------------------|
| Ollama (Local) | $0 (hardware cost) | $0 (hardware cost) |
| Anthropic Claude | $3-15 | $15-75 |
| OpenAI GPT-4 | $10-30 | $30-60 |
| Google Gemini | $0.35-7 | $1.40-21 |

**Note**: Ollama has upfront hardware costs but zero marginal cost per request.

## References | المراجع

- [Ollama Official Documentation](https://ollama.ai/docs)
- [Ollama GitHub Repository](https://github.com/ollama/ollama)
- [Model Library](https://ollama.ai/library)
- [SAHOOL AI Advisor Service](../apps/services/ai-advisor/README.md)
