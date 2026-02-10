FROM python:3.11-slim-bookworm

# Non-root user
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash sahool

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies with fallback to Aliyun mirror
COPY apps/services/irrigation-cycle-engine/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

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
