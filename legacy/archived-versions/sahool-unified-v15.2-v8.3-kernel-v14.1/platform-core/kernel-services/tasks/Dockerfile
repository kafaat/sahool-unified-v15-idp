FROM python:3.11-slim
WORKDIR /app
COPY services/tasks-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY services/tasks-service/src/ ./src/
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8089/healthz')"
EXPOSE 8089
CMD ["python", "-m", "src.main"]
