# SAHOOL vLLM Inference Server | خادم استدلال vLLM

vLLM-based inference server for **DeepSeek Coder 6.7B Instruct** with NVIDIA GPU acceleration.

خادم استدلال vLLM لنموذج ديب سيك كودر 6.7 مليار مع تسريع NVIDIA GPU.

## Prerequisites | المتطلبات

- NVIDIA GPU with >= 16GB VRAM (RTX 4090, A100, etc.)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed
- Docker with GPU support

## Quick Start | بدء سريع

```bash
# Create network if not exists
docker network create sahool-network 2>/dev/null || true

# Start vLLM server
docker compose -f infrastructure/core/vllm/docker-compose.vllm.yml up -d

# Check logs (model download may take several minutes on first run)
docker compose -f infrastructure/core/vllm/docker-compose.vllm.yml logs -f
```

## API Usage | استخدام الـ API

The server exposes an OpenAI-compatible API:

```bash
# Chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/deepseek-coder-6.7b-instruct",
    "messages": [{"role": "user", "content": "Write a Python function to sort a list"}],
    "temperature": 0.1,
    "max_tokens": 512
  }'

# List models
curl http://localhost:8000/v1/models

# Health check
curl http://localhost:8000/health
```

## Integration with SAHOOL | التكامل مع سهول

```python
from shared.llm import get_vllm_provider

provider = await get_vllm_provider(
    base_url="http://sahool-vllm:8000/v1",
    model="deepseek-ai/deepseek-coder-6.7b-instruct",
)

response = await provider.chat([
    {"role": "user", "content": "Explain NDVI calculation"}
])
```

## Environment Variables | متغيرات البيئة

| Variable | Default | Description |
|----------|---------|-------------|
| `VLLM_MODEL` | `deepseek-ai/deepseek-coder-6.7b-instruct` | Model to serve |
| `VLLM_PORT` | `8000` | Server port |
| `VLLM_MAX_MODEL_LEN` | `16384` | Maximum sequence length |
| `CUDA_VISIBLE_DEVICES` | `0` | GPU device index |
| `VLLM_GPU_COUNT` | `1` | Number of GPUs |
| `HF_TOKEN` | (empty) | HuggingFace token for gated models |

## GPU Memory Requirements | متطلبات ذاكرة GPU

| Model | VRAM Required | Recommended GPU |
|-------|---------------|-----------------|
| DeepSeek Coder 6.7B (FP16) | ~14GB | RTX 4090, A100 |
| DeepSeek Coder 6.7B (INT8) | ~8GB | RTX 3090, A10 |
