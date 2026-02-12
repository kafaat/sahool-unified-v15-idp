# SAHOOL AI Agents Core Service
# Port: 8161

FROM python:3.11-slim-bookworm

WORKDIR /app

# Create non-root user for security
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Install dependencies
COPY apps/services/ai-agents-core/requirements.txt .
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

# Copy shared modules (required for imports from shared/)
COPY apps/services/shared/ ./shared/

# Copy source
COPY apps/services/ai-agents-core/src/ ./src/

# Set ownership to non-root user
RUN chown -R sahool:sahool /app

# Set Python path and default port
ENV PYTHONPATH=/app/src \
    PORT=8161

# Expose port
EXPOSE 8161

# Switch to non-root user
USER sahool

# Health check - uses PORT env var via shell
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8161)}/healthz')"

# Run with uvicorn for production ASGI server - uses PORT env var
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
