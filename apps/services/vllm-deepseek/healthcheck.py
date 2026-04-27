#!/usr/bin/env python3
"""
SAHOOL vLLM DeepSeek Healthcheck
=================================
Standalone script called by Docker HEALTHCHECK to verify the vLLM
OpenAI-compatible HTTP server is up and accepting requests.

Usage (from Dockerfile or shell):
    python healthcheck.py [--port 8270] [--timeout 10]

Exit codes:
    0 — healthy
    1 — unhealthy (server not reachable or returned non-2xx)
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request


def check(port: int, timeout: int) -> bool:
    """
    Probe GET /health on the vLLM HTTP server.

    Returns True when the server responds with HTTP 200, False otherwise.
    """
    url = f"http://localhost:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="vLLM healthcheck probe")
    parser.add_argument("--port", type=int, default=8270, help="vLLM server port")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    args = parser.parse_args()

    if not (1 <= args.port <= 65535):
        print(f"invalid port: {args.port} (must be 1–65535)", file=sys.stderr)
        sys.exit(1)

    if check(args.port, args.timeout):
        print(f"healthy: vLLM server responding on port {args.port}")
        sys.exit(0)
    else:
        print(f"unhealthy: vLLM server not responding on port {args.port}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
