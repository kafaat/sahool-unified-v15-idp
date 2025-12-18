FROM python:3.11-slim
WORKDIR /app
COPY services/ndvi-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY services/ndvi-service/src/ ./src/
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8085/healthz')"
EXPOSE 8085
CMD ["python", "-m", "src.main"]
