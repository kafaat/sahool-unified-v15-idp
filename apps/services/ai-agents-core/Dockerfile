FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Set ownership to non-root user
RUN chown -R sahool:sahool /app

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8120

# Switch to non-root user
USER sahool

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8120/healthz')"

# Run with uvicorn for production ASGI server
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8120"]
