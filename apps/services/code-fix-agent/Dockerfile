# ============================================================================
# SAHOOL Code Fix Agent - Docker Image
# وكيل إصلاح الكود - صورة دوكر
# ============================================================================

FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to avoid pip root user warning
# إنشاء بيئة افتراضية لتجنب تحذير المستخدم الجذر
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements first for caching
COPY apps/services/code-fix-agent/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# ============================================================================
# Production Image
# ============================================================================

FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Copy virtual environment from builder
# نسخ البيئة الافتراضية من البناء
COPY --from=builder /opt/venv /opt/venv

# Set virtual environment path
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy application code
COPY apps/services/code-fix-agent/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8090 \
    HOST=0.0.0.0 \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8090/healthz').raise_for_status()"

# Run application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8090"]
