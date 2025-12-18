FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY mcp.json .

ENV PYTHONUNBUFFERED=1

# Server mode: "http" (FastAPI) or "mcp" (MCP stdio server)
ENV SERVER_MODE=http

EXPOSE 8111

# Entrypoint script to handle different server modes
CMD ["sh", "-c", "if [ \"$SERVER_MODE\" = \"mcp\" ]; then python -m src.mcp_server; else uvicorn src.main:app --host 0.0.0.0 --port 8111; fi"]
