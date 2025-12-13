FROM python:3.11-slim

WORKDIR /app

COPY services/disease-risk/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY services/disease-risk/src/ ./src/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=disease-risk-service
ENV SERVICE_LAYER=decision

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8087/healthz')"

EXPOSE 8087

CMD ["python", "-m", "src.main"]
