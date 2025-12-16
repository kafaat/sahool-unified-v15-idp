FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 sahool && \
    useradd --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install system and build dependencies required to compile native wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    python3-dev \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (build wheels if needed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove build-time packages to keep the runtime image small
RUN apt-get purge -y --auto-remove build-essential gcc python3-dev libpq-dev libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/* \
    || true

# Copy source code
COPY src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8099

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8099/healthz || exit 1

# Run service
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8099"]
