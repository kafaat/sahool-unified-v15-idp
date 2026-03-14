FROM python:3.11-slim-bookworm

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install system dependencies with mirror fallback (tini for PID 1 signal handling)
COPY docker/apt-update.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/apt-update.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    curl tini && rm -rf /var/lib/apt/lists/*

# Configure pip for network resilience
RUN mkdir -p /root/.pip && \
    printf '[global]\ntimeout = 300\nretries = 10\nindex-url = https://pypi.org/simple/\nextra-index-url = https://mirrors.aliyun.com/pypi/simple/\n                  https://pypi.tuna.tsinghua.edu.cn/simple/\n                  https://mirrors.cloud.tencent.com/pypi/simple\n[install]\nprefer-binary = true\n' > /root/.pip/pip.conf

# Copy and install dependencies with multi-mirror fallback
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
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

# Use tini as init system for proper signal handling and zombie reaping
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run application
CMD ["python", "-m", "src.main"]
