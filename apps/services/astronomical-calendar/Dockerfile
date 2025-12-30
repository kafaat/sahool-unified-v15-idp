# SAHOOL Astronomical Calendar Service
# خدمة التقويم الفلكي الزراعي

FROM python:3.11-slim

LABEL maintainer="SAHOOL Team <dev@sahool.io>"
LABEL description="Astronomical Calendar Service for Traditional Yemeni Farming"
LABEL version="15.5.0"

# Set working directory
WORKDIR /app

# Upgrade pip first (better retry logic and connection handling)
RUN pip install --no-cache-dir --upgrade pip --default-timeout=100

# Install dependencies with retry logic
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt || \
    (sleep 5 && pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt)

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8111

# Expose port
EXPOSE 8111

# Health check (using urllib to avoid httpx dependency)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8111/healthz')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8111"]
