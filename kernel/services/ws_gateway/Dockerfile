FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 sahool && \
    useradd --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

# Set Python path
ENV PYTHONPATH=/app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8090/healthz || exit 1

# Run service
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8090"]
