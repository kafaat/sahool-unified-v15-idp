#!/bin/bash
# Simple test script for the Code Review Service API
# This demonstrates the API endpoints using curl

echo "======================================================================"
echo "Code Review Service API Test Script"
echo "======================================================================"
echo ""
echo "This script demonstrates the REST API endpoints that have been added"
echo "to the code-review-service. The endpoints are:"
echo ""
echo "  1. GET  /health             - Health check"
echo "  2. POST /review             - Review code content"
echo "  3. POST /review/file        - Review a file from codebase"
echo ""
echo "When the service is running with Docker Compose, you can test it with:"
echo ""
echo "# Health check"
echo "curl http://localhost:8096/health"
echo ""
echo "# Review Python code"
echo 'curl -X POST http://localhost:8096/review \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{
    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
    "language": "python",
    "filename": "factorial.py"
  }'"'"
echo ""
echo "# Review JavaScript code"
echo 'curl -X POST http://localhost:8096/review \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{
    "code": "function greet(name) {\n  console.log('"'"'"'"'"'"'"'"'Hello, '"'"'"'"'"'"'"'"' + name);\n}",
    "language": "javascript"
  }'"'"
echo ""
echo "# Review a file from the codebase"
echo 'curl -X POST http://localhost:8096/review/file \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{"file_path": "docker-compose.yml"}'"'"
echo ""
echo "# Access API documentation"
echo "Open http://localhost:8096/docs in your browser"
echo ""
echo "======================================================================"
echo "To start the service, run:"
echo "  docker compose up -d code-review-service"
echo "======================================================================"
