# SAHOOL AI Agents Core Service
# Port: 8122

FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Install dependencies
COPY apps/services/ai-agents-core/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules (required for imports from shared/)
COPY apps/services/shared/ ./shared/

# Copy source
COPY apps/services/ai-agents-core/src/ ./src/

# Set ownership to non-root user
RUN chown -R sahool:sahool /app

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8122

# Switch to non-root user
USER sahool

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8122/healthz')"

# Run with uvicorn for production ASGI server
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8122"]
