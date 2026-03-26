ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

# Non-root user
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash sahool

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies with fallback to Aliyun mirror
COPY constraints.txt .
COPY apps/services/irrigation-cycle-engine/requirements.txt ./requirements.txt
# Install dependencies with resilient multi-mirror fallback strategy
# Try Aliyun mirror first with long timeout, then fallback to PyPI, finally Tencent
# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# Copy root shared modules (shared.ai, shared.events, etc.)
COPY shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py/, shared.middleware/, etc.)
COPY apps/services/shared/ ./shared/

# Copy service code
COPY apps/services/irrigation-cycle-engine/src ./src/

USER sahool

ENV PORT=8250
EXPOSE 8250

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8250/healthz')" || exit 1

CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
