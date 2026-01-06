FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool


# Upgrade pip to latest version
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
COPY apps/services/irrigation-smart/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY apps/services/shared ./shared/

# Copy source code
COPY apps/services/irrigation-smart/src/ ./src/

# Set ownership and switch to non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Expose port
EXPOSE 8094

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8094/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8094"]
