# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ ⚠️  FROZEN SERVICE - DO NOT USE IN PRODUCTION                              ║
# ║ This service has been replaced by: advisory-service (port 8093)            ║
# ║ Port Conflict: 8093                                                         ║
# ║ See: docs/DEPRECATED_SERVICES.md                                           ║
# ╚════════════════════════════════════════════════════════════════════════════╝

FROM python:3.11-slim-bookworm

WORKDIR /app


# Upgrade pip to latest version
RUN pip install --no-cache-dir --upgrade pip

# Configure pip for better network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    cat > /root/.pip/pip.conf <<'EOF'
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://pypi.org/simple/
trusted-host = mirrors.aliyun.com
               pypi.tuna.tsinghua.edu.cn
               pypi.org
               files.pythonhosted.org
[install]
prefer-binary = true
EOF

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/fertilizer-advisor/requirements.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -r requirements.txt

# Copy shared modules
COPY apps/services/shared ./shared/

# Copy source code
COPY apps/services/fertilizer-advisor/src/ ./src/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (changed from 8093 to avoid conflict with advisory-service)
EXPOSE 8127

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8127/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8127"]
