FROM python:3.11-slim-bookworm

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool


# Upgrade pip to latest version
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip

# Install dependencies
COPY apps/services/indicators-service/requirements.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Try official PyPI first with long timeout, then fallback to Aliyun, finally Tencent
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

# Copy shared modules
COPY apps/services/shared ./shared/

# Copy source code
COPY apps/services/indicators-service/src/ ./src/

# Set ownership and switch to non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Expose port
EXPOSE 8091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8091/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8091"]
