# LLM Orchestrator Service | خدمة تنسيق نماذج اللغة الكبيرة

**Port**: 8220

Intelligent orchestration service for SAHOOL AI agents. This service routes user requests to appropriate AI agents, executes them in parallel, and synthesizes coherent responses.

خدمة تنسيق ذكية لوكلاء الذكاء الاصطناعي في سهول. توجه هذه الخدمة طلبات المستخدمين إلى وكلاء الذكاء الاصطناعي المناسبين، وتنفذهم بالتوازي، وتجمع استجابات متسقة.

## Features | الميزات

- **Intent Classification**: Automatically classifies user intents in Arabic and English
- **Multi-Agent Orchestration**: Coordinates multiple AI agents for comprehensive analysis
- **Parallel Execution**: Executes agent calls in parallel for optimal performance
- **Response Synthesis**: Combines results into human-friendly summaries
- **Action Recommendations**: Generates actionable recommendations with bilingual support
- **Caching**: Redis-based caching for improved response times

## API Endpoints | نقاط النهاية

### Main Orchestration

- `POST /api/v1/orchestrate` - Main orchestration endpoint
- `POST /api/v1/orchestrate/image` - Orchestration with image analysis
- `GET /api/v1/orchestrate/plans` - Get available execution plans
- `POST /api/v1/orchestrate/execute-action` - Execute recommended action

### Agent Management

- `GET /api/v1/agents` - List all registered agents
- `GET /api/v1/agents/health` - Check health of all agents

### Health

- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe

## Supported Intents | النوايا المدعومة

| Intent | Description EN | Description AR |
|--------|---------------|----------------|
| `crop_disease` | Crop disease diagnosis | تشخيص أمراض المحاصيل |
| `irrigation_query` | Irrigation queries | استفسارات الري |
| `fertilizer_advice` | Fertilizer recommendations | توصيات الأسمدة |
| `pest_detection` | Pest detection | كشف الآفات |
| `weather_query` | Weather forecasts | توقعات الطقس |
| `yield_prediction` | Yield prediction | تنبؤ الإنتاجية |
| `field_analysis` | Field analysis | تحليل الحقول |
| `terrain_analysis` | Terrain analysis | تحليل التضاريس |
| `hydrology_query` | Hydrology analysis | تحليل الهيدرولوجيا |
| `leveling_query` | Leveling optimization | تحسين التسوية |
| `image_analysis` | Image analysis | تحليل الصور |

## Example Usage | مثال الاستخدام

```python
import httpx

# Orchestrate a crop disease query
response = httpx.post(
    "http://localhost:8220/api/v1/orchestrate",
    json={
        "text": "What disease is affecting my wheat crop?",
        "language": "en",
        "field_id": "field_001"
    }
)

print(response.json())
```

Arabic example:
```python
response = httpx.post(
    "http://localhost:8220/api/v1/orchestrate",
    json={
        "text": "ما هو المرض الذي يصيب محصول القمح؟",
        "language": "ar",
        "field_id": "field_001"
    }
)
```

## Environment Variables | متغيرات البيئة

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8220 | Service port |
| `ENVIRONMENT` | development | Environment (development/staging/production) |
| `LOG_LEVEL` | INFO | Logging level |
| `DATABASE_URL` | - | PostgreSQL connection URL |
| `REDIS_URL` | redis://localhost:6379 | Redis URL for caching |
| `NATS_URL` | nats://localhost:4222 | NATS URL for events |
| `OLLAMA_URL` | http://localhost:11434 | Ollama server URL |
| `LLM_MODEL_NAME` | codellama:7b | LLM model for intent classification |
| `AGENT_TIMEOUT` | 30 | Agent call timeout in seconds |
| `AGENT_MAX_RETRIES` | 3 | Maximum retries for agent calls |

## Development | التطوير

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn src.main:app --host 0.0.0.0 --port 8220 --reload

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

## Docker | دوكر

```bash
# Build
docker build -t sahool/llm-orchestrator-service:16.0.0 -f Dockerfile ../..

# Run
docker run -p 8220:8220 sahool/llm-orchestrator-service:16.0.0
```

## Architecture | الهيكلة

```
llm-orchestrator-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   └── config.py        # Settings configuration
│   ├── api/
│   │   ├── schemas.py       # Pydantic models
│   │   └── endpoints/
│   │       └── orchestrator.py  # API endpoints
│   ├── agents/
│   │   ├── registry.py      # Agent registry
│   │   └── executor.py      # Agent executor
│   └── utils/
│       ├── intent_classifier.py  # Intent classification
│       └── synthesizer.py   # Response synthesis
├── tests/
│   ├── conftest.py          # Test fixtures
│   └── test_orchestrator.py # Unit tests
├── requirements.txt
├── Dockerfile
└── README.md
```

## License | الترخيص

Proprietary - KAFAAT
