FROM python:3.11-slim-bookworm

WORKDIR /app

RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl tini && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -r requirements.txt

# Copy shared library + service code
COPY shared/prescription_safety /app/shared/prescription_safety
COPY src ./src

RUN chown -R sahool:sahool /app

ENV PYTHONPATH=/app \
    PORT=8275 \
    SERVICE_NAME=prescription-safety-gateway \
    SERVICE_LAYER=decision \
    SERVICE_VERSION=0.1.0

USER sahool
EXPOSE 8275

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8275/healthz || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8275"]
