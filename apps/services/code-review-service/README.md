# Real-time Code Review Service

Real-time code review service using Ollama + DeepSeek model to review codebase changes, especially focusing on containers and infrastructure code.

## Features

- 🔍 **Real-time Monitoring**: Watches for file changes in the codebase
- 🤖 **AI-Powered Reviews**: Uses DeepSeek model via Ollama for intelligent code review
- 🌐 **HTTP API**: REST API endpoints for on-demand code reviews
- 📊 **Structured Reviews**: Provides JSON-formatted reviews with scores and recommendations
- 🔒 **Security Focus**: Identifies security vulnerabilities and concerns
- 🐳 **Container-Aware**: Special focus on Docker and containerization best practices
- 📝 **Comprehensive Logging**: Logs all reviews to JSONL format for analysis

## API Endpoints

### Health Check
```bash
GET http://localhost:8096/health
```

Returns service health status and Ollama connectivity.

### Review Code Content
```bash
POST http://localhost:8096/review
Content-Type: application/json

{
  "code": "def hello():\n    print('world')",
  "language": "python",
  "filename": "example.py"
}
```

Reviews the provided code and returns a structured review.

**Response:**
```json
{
  "summary": "Code looks good with proper Python syntax...",
  "critical_issues": [],
  "suggestions": ["Consider adding docstring"],
  "security_concerns": [],
  "score": 85
}
```

### Review File from Codebase
```bash
POST http://localhost:8096/review/file
Content-Type: application/json

{
  "file_path": "infrastructure/core/pgbouncer/pgbouncer.ini"
}
```

Reviews a file from the mounted codebase.

## Configuration

### Environment Variables

- `OLLAMA_URL`: Ollama API URL (default: `http://ollama:11434`)
- `OLLAMA_MODEL`: Model to use (default: `deepseek`)
- `WATCH_PATHS`: Colon-separated paths to watch (default: `infrastructure:docker-compose.yml:docker`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `REVIEW_ON_CHANGE`: Enable/disable reviews on file changes (default: `true`)
- `MAX_FILE_SIZE`: Maximum file size to review in bytes (default: `1000000`)
- `API_HOST`: API server host (default: `0.0.0.0`)
- `API_PORT`: API server port (default: `8096`)

### Watched Paths

By default, the service monitors:
- `infrastructure/` - Infrastructure and configuration files
- `docker-compose.yml` - Main Docker Compose configuration
- `docker/` - Docker-related files

## Usage

### Start the Service

```bash
docker compose up -d code-review-service
```

The service will:
1. Start the HTTP API server on port 8096
2. Start watching configured paths for file changes (if `REVIEW_ON_CHANGE=true`)

### Access the API

```bash
# Check service health
curl http://localhost:8096/health

# Review code snippet
curl -X POST http://localhost:8096/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "console.log(\"hello\")",
    "language": "javascript"
  }'

# Review a file
curl -X POST http://localhost:8096/review/file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "docker-compose.yml"}'
```

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8096/docs`
- ReDoc: `http://localhost:8096/redoc`

### View Logs

```bash
# Service logs
docker logs -f sahool-code-review

# Review logs (JSONL format)
docker exec sahool-code-review cat /app/logs/reviews.jsonl
```

### Review Log Format

Each review is logged as a JSON line:

```json
{
  "timestamp": "2026-01-02T15:30:45.123456",
  "file": "/app/codebase/infrastructure/core/pgbouncer/pgbouncer.ini",
  "review": {
    "summary": "Configuration looks good with proper SCRAM authentication setup...",
    "critical_issues": [],
    "suggestions": ["Consider adding connection timeout settings"],
    "security_concerns": [],
    "score": 85
  }
}
```

## Review Criteria

The service reviews code for:

1. **Code Quality**: Best practices, readability, maintainability
2. **Security**: Vulnerabilities, insecure configurations, exposed secrets
3. **Performance**: Optimization opportunities, resource usage
4. **Docker Best Practices**: Containerization patterns, image optimization
5. **Configuration Errors**: Invalid settings, missing required fields
6. **Potential Bugs**: Logic errors, edge cases, error handling

## Integration

The service automatically starts when:
- Ollama service is healthy
- Codebase is mounted at `/app/codebase`

It will automatically review any changes to files in the watched paths.

## Troubleshooting

### Service not starting
- Check Ollama is running: `docker logs sahool-ollama`
- Verify model is downloaded: `docker exec sahool-ollama ollama list`

### No reviews generated
- Check file paths are in watched directories
- Verify file extensions are supported
- Check file size is under `MAX_FILE_SIZE`

### Slow reviews
- Reduce `MAX_FILE_SIZE` to review smaller files
- Check Ollama resource limits in docker-compose.yml
- Consider using a smaller model variant

