FROM python:3.11-slim-bookworm

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Install dependencies
COPY apps/services/soil-analysis-service/requirements.txt .
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt

# Copy application
COPY apps/services/soil-analysis-service/src/ ./src/

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8124/healthz || exit 1

EXPOSE 8124

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8124"]
