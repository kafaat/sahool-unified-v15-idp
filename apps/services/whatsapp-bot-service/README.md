# SAHOOL WhatsApp Bot Service

> خدمة روبوت واتساب - محادثات ذكية للمزارعين

WhatsApp messaging service for SAHOOL farmers using the WhatsApp Business API (Cloud API).

## Overview

This service handles WhatsApp messaging for SAHOOL farmers, providing:

- **Crop Disease Detection**: Send photos of crops for AI-powered disease diagnosis
- **Irrigation Advice**: Get personalized irrigation recommendations
- **Weather Information**: Location-based weather forecasts
- **Fertilizer Recommendations**: Soil and crop-based fertilizer advice
- **Pest Detection**: Identify and get advice on pest management
- **Bilingual Support**: Full Arabic and English support

## Port

- **Service Port**: 8240

## Architecture

```
+-------------------+     +----------------------+     +------------------------+
|  WhatsApp Cloud   | --> |  WhatsApp Bot       | --> |  LLM Orchestrator      |
|  API Webhook      |     |  Service (8240)      |     |  Service (8220)        |
+-------------------+     +----------------------+     +------------------------+
                                    |
                                    v
                          +----------------------+
                          |  YOLO Vision         |
                          |  Service (8150)      |
                          +----------------------+
```

## API Endpoints

### Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/webhook` | Webhook verification (Meta) |
| POST | `/webhook` | Receive incoming messages |

### Send Message Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/send` | Send message (text, image, location, interactive) |
| POST | `/api/v1/send-template` | Send template message |
| POST | `/api/v1/mark-read` | Mark message as read |

### Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe |
| GET | `/` | Service info |
| GET | `/docs` | OpenAPI documentation |

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `WHATSAPP_TOKEN` | WhatsApp Business API access token | `EAAxx...` |
| `WHATSAPP_PHONE_ID` | WhatsApp phone number ID | `123456789012345` |
| `WHATSAPP_VERIFY_TOKEN` | Webhook verification token | `sahool_whatsapp_verify_2026` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `WHATSAPP_API_VERSION` | WhatsApp API version | `v17.0` |
| `LLM_ORCHESTRATOR_URL` | LLM Orchestrator Service URL | `http://llm-orchestrator-service:8220` |
| `VISION_SERVICE_URL` | Vision Service URL | `http://yolo26-vision-service:8150` |
| `REDIS_URL` | Redis URL for sessions | `redis://localhost:6379` |
| `SESSION_TTL` | Session TTL in seconds | `3600` |
| `DEFAULT_LANGUAGE` | Default response language | `ar` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Message Types Supported

### Incoming Messages

- **Text**: Natural language queries in Arabic or English
- **Image**: Crop photos for disease/pest detection
- **Location**: For location-based weather and advice
- **Interactive**: Button and list responses

### Outgoing Messages

- **Text**: Plain text responses
- **Interactive Buttons**: Quick action buttons (max 3)
- **Interactive Lists**: Multi-section menus
- **Templates**: Pre-approved template messages

## Session Management

The service maintains conversation context using Redis:

- **Session TTL**: 1 hour (configurable)
- **Context Limit**: Last 10 messages
- **Stored Data**: Language preference, location, crops, conversation history

## Local Development

### Prerequisites

- Python 3.12+
- Redis (optional, for session persistence)
- WhatsApp Business API credentials (for testing with real WhatsApp)

### Setup

```bash
# Navigate to service directory
cd apps/services/whatsapp-bot-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Run the service
uvicorn src.main:app --reload --port 8240
```

### Testing Webhook Locally

Use ngrok or similar to expose your local server:

```bash
ngrok http 8240
```

Then configure the ngrok URL as your webhook URL in the Meta WhatsApp Business settings.

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

## Docker

```bash
# Build
docker build -t sahool/whatsapp-bot-service:latest -f Dockerfile ../..

# Run
docker run -p 8240:8240 \
  -e WHATSAPP_TOKEN=your_token \
  -e WHATSAPP_PHONE_ID=your_phone_id \
  -e WHATSAPP_VERIFY_TOKEN=your_verify_token \
  sahool/whatsapp-bot-service:latest
```

## Integration with Other Services

### LLM Orchestrator Service (8220)

All natural language queries are forwarded to the LLM Orchestrator for:
- Intent classification
- Response generation
- Action recommendations

### Vision Service (8150)

Image messages are forwarded to YOLO Vision Service for:
- Crop disease detection
- Pest identification
- Weed detection

### Notification Service (8110)

Integrates with notification service for:
- Sending proactive alerts
- Marketing messages
- OTP verification

## WhatsApp Business API Setup

1. Create a Meta Business Account
2. Create a WhatsApp Business App
3. Add a phone number
4. Generate a permanent access token
5. Configure webhook URL: `https://your-domain.com/webhook`
6. Subscribe to webhook fields: `messages`

## Security

- Webhook verification using verify token
- HTTPS required in production
- No storage of message content (processed in memory)
- Phone numbers are masked in logs

## Rate Limits

WhatsApp Cloud API limits:
- 80 messages per second (business-initiated)
- 1000 template messages per phone number per day
- 250 unique recipients per 24 hours (for new numbers)

---

## License

Proprietary - KAFAAT

## Contact

- **Technical Support**: support@sahool.io
- **Documentation**: https://docs.sahool.io
