# Real-time Code Review Service

Real-time code review service using Ollama + DeepSeek model to review codebase changes, especially focusing on containers and infrastructure code.

## Features

- 🔍 **Real-time Monitoring**: Watches for file changes in the codebase
- 🤖 **AI-Powered Reviews**: Uses DeepSeek model via Ollama for intelligent code review
- 📊 **Structured Reviews**: Provides JSON-formatted reviews with scores and recommendations
- 🔒 **Security Focus**: Identifies security vulnerabilities and concerns
- 🐳 **Container-Aware**: Special focus on Docker and containerization best practices
- 📝 **Comprehensive Logging**: Logs all reviews to JSONL format for analysis

## Configuration

### Environment Variables

- `OLLAMA_URL`: Ollama API URL (default: `http://ollama:11434`)
- `OLLAMA_MODEL`: Model to use (default: `deepseek`)
- `WATCH_PATHS`: Colon-separated paths to watch (default: `infrastructure:docker-compose.yml:docker`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `REVIEW_ON_CHANGE`: Enable/disable reviews on file changes (default: `true`)
- `MAX_FILE_SIZE`: Maximum file size to review in bytes (default: `1000000`)

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

