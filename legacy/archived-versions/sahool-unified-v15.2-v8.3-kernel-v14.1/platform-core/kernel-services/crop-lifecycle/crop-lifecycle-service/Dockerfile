FROM python:3.11-slim

WORKDIR /app

COPY services/crop-lifecycle-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY services/crop-lifecycle-service/src/ ./src/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=crop-lifecycle-service
ENV SERVICE_LAYER=decision

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8086/healthz')"

EXPOSE 8086

CMD ["python", "-m", "src.main"]
