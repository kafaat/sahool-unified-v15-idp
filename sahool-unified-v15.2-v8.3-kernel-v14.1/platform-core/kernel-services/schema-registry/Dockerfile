FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY services/schema-registry/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ ./shared/

# Copy service code
COPY services/schema-registry/src/ ./src/

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8082/healthz')"

EXPOSE 8082

CMD ["python", "-m", "src.main"]
