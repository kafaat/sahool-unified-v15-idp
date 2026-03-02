FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

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
[install]
prefer-binary = true
EOF

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -r requirements.txt

# Copy application code
COPY src ./src

# Set ownership
RUN chown -R sahool:sahool /app

# Set environment
ENV PYTHONPATH=/app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE {{port}}

# Run application
CMD ["python", "-m", "src.main"]
