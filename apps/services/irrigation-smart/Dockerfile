FROM python:3.11-slim

# Labels
LABEL org.opencontainers.image.title="SAHOOL irrigation-smart"
LABEL org.opencontainers.image.version="16.0.0"
LABEL maintainer="KAFAAT <dev@kafaat.sa>"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PORT=8094

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool


# Upgrade pip to latest version
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set ownership and switch to non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Expose port
EXPOSE 8094

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8094/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8094"]
