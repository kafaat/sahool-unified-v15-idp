# SAHOOL skill-router-service — Phase 1 (ADR-010)
# Build context: repository root (needs access to .claude/skills/index.yaml)
#
# Build:
#   docker build -t sahool/skill-router-service:latest \
#     -f apps/services/skill-router-service/Dockerfile .
#
# Run:
#   docker run -p 8205:8205 sahool/skill-router-service:latest

FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# Deterministic install: pip consults all indexes in one invocation and picks
# the same version every time. Extra-index-url provides availability without
# fallback-induced non-determinism.
COPY apps/services/skill-router-service/requirements.txt .
RUN pip install --no-cache-dir \
    --index-url https://pypi.org/simple \
    --extra-index-url https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt

# Service code
COPY apps/services/skill-router-service/app ./app

# Registry artifact (read at startup; override via SKILLS_INDEX_PATH)
COPY .claude/skills/index.yaml /app/.claude/skills/index.yaml

# Non-root user per SAHOOL security policy
RUN groupadd --system --gid 1000 sahool \
    && useradd --system --uid 1000 --gid sahool --create-home sahool \
    && chown -R sahool:sahool /app
USER sahool

ENV SKILLS_INDEX_PATH=/app/.claude/skills/index.yaml \
    PORT=8205 \
    HOST=0.0.0.0

EXPOSE 8205

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8205/healthz', timeout=3)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8205"]
