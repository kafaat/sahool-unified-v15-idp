FROM python:3.11-slim

WORKDIR /app

# Configure apt to use HTTPS and install system dependencies (curl for healthcheck)
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/*.list /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends curl ca-certificates apt-transport-https && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8093

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8093/healthz || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8093"]
