FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src

# Set ownership
RUN chown -R sahool:sahool /app

# Set environment
ENV PYTHONPATH=/app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE {{port}}

# Run application
CMD ["python", "-m", "src.main"]
