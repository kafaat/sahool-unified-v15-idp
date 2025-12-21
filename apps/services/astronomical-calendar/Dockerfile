# SAHOOL Astronomical Calendar Service
# خدمة التقويم الفلكي الزراعي

FROM python:3.11-slim

LABEL maintainer="SAHOOL Team <dev@sahool.io>"
LABEL description="Astronomical Calendar Service for Traditional Yemeni Farming"
LABEL version="15.5.0"

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8111

# Expose port
EXPOSE 8111

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8111/healthz').raise_for_status()" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8111"]
