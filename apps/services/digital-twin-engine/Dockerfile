ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash sahool

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY apps/services/digital-twin-engine/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

# Copy root shared modules (shared.ai, shared.events, etc.)
COPY shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py/, shared.middleware/, etc.)
COPY apps/services/shared/ ./shared/

COPY apps/services/digital-twin-engine/src ./src/

USER sahool

ENV PORT=8253
EXPOSE 8253

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8253/healthz')" || exit 1

CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
