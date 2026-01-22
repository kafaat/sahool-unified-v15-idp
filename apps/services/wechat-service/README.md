# SAHOOL WeChat Integration Service

## Overview

WeChat messaging and social integration service for SAHOOL agricultural platform. Provides messaging, contact management, moments publishing, and AI-powered chat analysis capabilities.

| Property | Value |
|----------|-------|
| Service Name | wechat-service |
| Arabic Name | خدمة تكامل ويتشات |
| Port | 8133 |
| Version | 16.0.0 |

## Features

- **Message Management**: Fetch and send messages across WeChat chats and groups
- **Contact Management**: Add friends, join groups, follow official accounts
- **Moments Publishing**: Post to WeChat Moments with visibility controls
- **Chat Summarization**: AI-powered conversation summaries
- **Chat Insights**: Extract sentiment, topics, action items, and key decisions
- **Bilingual Support**: Arabic and English responses

## API Endpoints

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Liveness probe |
| `/readyz` | GET | Readiness probe |
| `/health` | GET | Detailed health status |
| `/metrics` | GET | Prometheus metrics |

### Message Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/messages/fetch` | POST | Fetch messages from chat |
| `/api/v1/messages/send` | POST | Send message to chat |

### Contact Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/contacts/add` | POST | Add new contact |

### Moments Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/moments/publish` | POST | Publish moment |

### Chat Analysis Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat/summarize` | POST | Generate chat summary |
| `/api/v1/chat/insights` | POST | Extract chat insights |

## Configuration

### Environment Variables

```bash
# Service Configuration
SERVICE_PORT=8133

# Database
DATABASE_URL=postgresql://user:pass@host:5432/sahool

# Redis Cache
REDIS_URL=redis://redis:6379

# NATS Messaging
NATS_URL=nats://nats:4222

# WeChat API
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# JWT Authentication
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
```

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8133 --reload
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

### Docker

```bash
# Build image
docker build -t sahool/wechat-service:latest -f apps/services/wechat-service/Dockerfile .

# Run container
docker run -p 8133:8133 \
  -e JWT_SECRET_KEY=your_secret \
  -e WECHAT_APP_ID=your_app_id \
  -e WECHAT_APP_SECRET=your_app_secret \
  sahool/wechat-service:latest
```

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/api/v1/messages/fetch` | 60/minute |
| `/api/v1/messages/send` | 30/minute |
| `/api/v1/contacts/add` | 20/minute |
| `/api/v1/moments/publish` | 10/minute |
| `/api/v1/chat/summarize` | 10/minute |
| `/api/v1/chat/insights` | 10/minute |

## NATS Events

The service publishes the following events:

| Event Subject | Description |
|---------------|-------------|
| `sahool.{tenant_id}.wechat.messages.fetched` | Messages fetched from chat |
| `sahool.{tenant_id}.wechat.message.sent` | Message sent successfully |
| `sahool.{tenant_id}.wechat.contact.added` | New contact added |
| `sahool.{tenant_id}.wechat.moment.published` | Moment published |
| `sahool.{tenant_id}.wechat.chat.summarized` | Chat summary generated |
| `sahool.{tenant_id}.wechat.chat.insights_extracted` | Chat insights extracted |

## Error Codes

| Code | Description (EN) | Description (AR) |
|------|------------------|------------------|
| `VALIDATION_ERROR` | Validation error | خطأ في التحقق |
| `NOT_FOUND` | Resource not found | المورد غير موجود |
| `FORBIDDEN` | Access denied | تم رفض الوصول |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | تم تجاوز الحد الأقصى للطلبات |
| `WECHAT_*` | WeChat API error | خطأ في واجهة ويتشات |
| `INVALID_INPUT` | Invalid input | إدخال غير صالح |
| `SERVICE_UNAVAILABLE` | Service unavailable | الخدمة غير متاحة |

## Architecture

```
wechat-service/
├── Dockerfile
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   └── main.py          # FastAPI application
└── tests/
    ├── __init__.py
    ├── conftest.py      # Test fixtures
    └── test_main.py     # Comprehensive tests
```

## Dependencies

- FastAPI 0.126.0+
- Pydantic v2.10+
- Redis 5.0+
- NATS 2.9+
- asyncpg 0.30+
- structlog 24.0+

## Security

- JWT-based authentication required for all API endpoints
- Rate limiting to prevent abuse
- Tenant isolation for multi-tenancy
- Non-root Docker container
- Input validation on all endpoints

## Author

SAHOOL Platform Team - KAFAAT

## License

Proprietary - KAFAAT
