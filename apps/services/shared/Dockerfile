# SAHOOL Shared Services Dockerfile
# ⚠️ Note: This is a library/package, not a standalone service
# Services should include shared/ as a dependency rather than running this container
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel

# Install dependencies
COPY apps/services/shared/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Copy shared modules
COPY apps/services/shared/ ./shared/

# Set ownership and switch to non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Note: This is a library container - services should import from it
# No exposed port or CMD - this is meant to be used as a base or copied into service containers
CMD ["python", "-c", "print('SAHOOL Shared Services Library - Import from services, do not run directly')"]
