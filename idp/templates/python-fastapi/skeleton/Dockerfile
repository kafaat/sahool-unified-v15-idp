FROM python:3.11-slim-bookworm

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install system dependencies with mirror fallback
COPY docker/apt-update.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/apt-update.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

# Configure pip for network resilience
RUN mkdir -p /root/.pip && \
    cat > /root/.pip/pip.conf <<'EOF'
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://mirrors.cloud.tencent.com/pypi/simple
                  https://pypi.org/simple/
trusted-host = mirrors.aliyun.com
               pypi.tuna.tsinghua.edu.cn
               mirrors.cloud.tencent.com
               pypi.org
               files.pythonhosted.org
[install]
prefer-binary = true
EOF

# Copy and install dependencies with multi-mirror fallback
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

# Copy application code
COPY src ./src

# Set ownership
RUN chown -R sahool:sahool /app

# Set environment
ENV PYTHONPATH=/app \
    PORT={{port}}

# Switch to non-root user
USER sahool

# Expose port
EXPOSE {{port}}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:{{port}}/healthz || exit 1

# Run application
CMD ["python", "-m", "src.main"]
