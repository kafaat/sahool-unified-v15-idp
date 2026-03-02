# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL vLLM Inference Server - DeepSeek Coder
# خادم استدلال vLLM - ديب سيك كودر
#
# Base: NVIDIA CUDA 12.1 + cuDNN 8 (Ubuntu 22.04)
# Model: deepseek-ai/deepseek-coder-6.7b-instruct
# Port: 8000 (OpenAI-compatible API)
#
# Version: 16.0.0
# Updated: March 2026
#
# Security:
#   - Non-root user (sahool, UID 1000)
#   - Read-only filesystem support
#   - No unnecessary packages
#   - Multi-mirror pip fallback (PyPI / Aliyun / Tencent)
# ═══════════════════════════════════════════════════════════════════════════════

ARG CUDA_VERSION=12.1.1
FROM nvidia/cuda:${CUDA_VERSION}-cudnn8-runtime-ubuntu22.04 AS base

# OCI Labels
LABEL org.opencontainers.image.title="SAHOOL vLLM DeepSeek Coder" \
      org.opencontainers.image.version="16.0.0" \
      org.opencontainers.image.vendor="KAFAAT" \
      org.opencontainers.image.description="GPU-accelerated LLM inference server for agricultural code intelligence" \
      org.opencontainers.image.licenses="Proprietary"

# ─────────────────────────────────────────────────────────────────────────────
# Build Arguments
# ─────────────────────────────────────────────────────────────────────────────
ARG PYTHON_VERSION=3.11
ARG VLLM_VERSION=0.6.6.post1

# ─────────────────────────────────────────────────────────────────────────────
# Environment Configuration
# ─────────────────────────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    # CUDA configuration
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    CUDA_HOME=/usr/local/cuda \
    # vLLM defaults
    VLLM_MODEL=deepseek-ai/deepseek-coder-6.7b-instruct \
    VLLM_PORT=8000 \
    VLLM_HOST=0.0.0.0 \
    VLLM_MAX_MODEL_LEN=16384 \
    # HuggingFace cache
    HF_HOME=/home/sahool/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/sahool/.cache/huggingface/hub

# ─────────────────────────────────────────────────────────────────────────────
# System Dependencies (minimal attack surface)
# ─────────────────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev \
    python3-pip \
    curl \
    ca-certificates \
    git \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ─────────────────────────────────────────────────────────────────────────────
# Non-root User (Security - UID/GID 1000 for consistency)
# ─────────────────────────────────────────────────────────────────────────────
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# ─────────────────────────────────────────────────────────────────────────────
# Install vLLM with Multi-Mirror Fallback (Pattern A)
# ─────────────────────────────────────────────────────────────────────────────
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    "vllm==${VLLM_VERSION}" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    "vllm==${VLLM_VERSION}" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    "vllm==${VLLM_VERSION}"

# ─────────────────────────────────────────────────────────────────────────────
# Prepare Model Cache & Working Directories
# ─────────────────────────────────────────────────────────────────────────────
RUN mkdir -p /home/sahool/.cache/huggingface/hub /models /tmp/vllm && \
    chown -R sahool:sahool /home/sahool /models /tmp/vllm

WORKDIR /home/sahool

# Switch to non-root user
USER sahool

# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=15s --start-period=180s --retries=5 \
    CMD curl -f http://localhost:${VLLM_PORT}/health || exit 1

EXPOSE ${VLLM_PORT}

# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint: vLLM serve
# ─────────────────────────────────────────────────────────────────────────────
CMD ["sh", "-c", \
    "vllm serve ${VLLM_MODEL} \
        --trust-remote-code \
        --host ${VLLM_HOST} \
        --port ${VLLM_PORT} \
        --max-model-len ${VLLM_MAX_MODEL_LEN} \
        --dtype auto \
        --gpu-memory-utilization 0.90 \
        --download-dir /models"]
