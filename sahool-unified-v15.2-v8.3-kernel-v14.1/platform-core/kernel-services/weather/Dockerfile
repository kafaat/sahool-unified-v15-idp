FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/weather/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ ./shared/

# Copy service code
COPY services/weather/src/ ./src/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=weather-service
ENV SERVICE_LAYER=signal-producer

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8084/healthz')"

# Layer 2: NO public ports - only expose internally
EXPOSE 8084

CMD ["python", "-m", "src.main"]
