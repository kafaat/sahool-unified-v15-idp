# AI Advisor Service | خدمة المستشار الذكي

Multi-agent AI system for comprehensive agricultural advisory using Claude and LangChain.

نظام ذكاء اصطناعي متعدد الوكلاء للاستشارات الزراعية الشاملة باستخدام Claude و LangChain.

## Features | المميزات

- **Multi-Agent Architecture**: Specialized agents for different agricultural tasks
- **Field Analysis**: NDVI analysis, satellite imagery interpretation
- **Disease Diagnosis**: AI-powered crop disease identification and treatment
- **Irrigation Management**: Smart irrigation scheduling and water optimization
- **Yield Prediction**: Data-driven crop yield forecasting
- **RAG Integration**: Knowledge retrieval from agricultural databases
- **Workflow Orchestration**: Complex multi-step agricultural workflows

## Architecture | البنية

### Agents | الوكلاء

1. **Field Analyst** - Satellite data and NDVI analysis
2. **Disease Expert** - Crop disease diagnosis and treatment
3. **Irrigation Advisor** - Water management and irrigation scheduling
4. **Yield Predictor** - Production forecasting and harvest planning

### Components | المكونات

- **Supervisor**: Coordinates multiple agents
- **Workflow Manager**: Handles multi-step processes
- **RAG System**: Knowledge retrieval with Qdrant
- **External Tools**: Integration with other microservices

## Prerequisites | المتطلبات

- Python 3.11+
- Docker and Docker Compose
- Anthropic API Key
- Qdrant vector database
- Access to external services (crop-health-ai, weather-core, satellite-service, agro-advisor)

## Installation | التثبيت

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Docker Build

```bash
docker build -t ai-advisor:latest .
```

### 3. Run Service

```bash
docker run -p 8112:8112 --env-file .env ai-advisor:latest
```

## API Endpoints | نقاط النهاية

### Health Check

```http
GET /healthz
```

### Ask Question

```http
POST /v1/advisor/ask
Content-Type: application/json

{
  "question": "What is the best irrigation schedule for wheat?",
  "language": "en",
  "context": {
    "crop_type": "wheat",
    "location": "Yemen"
  }
}
```

### Diagnose Disease

```http
POST /v1/advisor/diagnose
Content-Type: application/json

{
  "crop_type": "tomato",
  "symptoms": {
    "leaf_color": "yellow",
    "spots": true,
    "wilting": false
  },
  "image_path": "/path/to/image.jpg",
  "location": "field_123"
}
```

### Get Recommendations

```http
POST /v1/advisor/recommend
Content-Type: application/json

{
  "crop_type": "corn",
  "growth_stage": "vegetative",
  "recommendation_type": "irrigation",
  "field_data": {
    "soil": {"moisture": 30},
    "weather": {"temperature": 28}
  }
}
```

### Analyze Field

```http
POST /v1/advisor/analyze-field
Content-Type: application/json

{
  "field_id": "field_123",
  "crop_type": "wheat",
  "include_disease_check": true,
  "include_irrigation": true,
  "include_yield_prediction": true
}
```

### List Agents

```http
GET /v1/advisor/agents
```

## Configuration | الإعدادات

Key environment variables:

- `ANTHROPIC_API_KEY`: Your Claude API key (required)
- `SERVICE_PORT`: Service port (default: 8112)
- `QDRANT_HOST`: Qdrant database host
- `EMBEDDINGS_MODEL`: Sentence transformer model for embeddings
- `RAG_TOP_K`: Number of documents to retrieve (default: 5)

See `.env.example` for all configuration options.

## Development | التطوير

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run service
python -m uvicorn src.main:app --reload --port 8112
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

## Integration | التكامل

This service integrates with:

- **crop-health-ai** (8109): Image-based disease detection
- **weather-core** (8002): Weather data and forecasts
- **satellite-service** (8108): Satellite imagery and NDVI
- **agro-advisor** (8003): Agricultural knowledge base

## RAG Knowledge Base | قاعدة المعرفة RAG

The service uses Qdrant for knowledge retrieval. To populate the knowledge base:

1. Prepare agricultural documents
2. Use the embeddings manager to generate vectors
3. Store in Qdrant collection

Example:

```python
from src.rag import EmbeddingsManager, KnowledgeRetriever

embeddings = EmbeddingsManager()
retriever = KnowledgeRetriever(embeddings)

documents = [
    "Wheat requires 450-650mm of water during growing season...",
    "Tomato early blight is caused by Alternaria solani..."
]

retriever.add_documents(documents)
```

## Monitoring | المراقبة

The service provides structured JSON logs. Key metrics:

- Agent response times
- Tool call success rates
- RAG retrieval scores
- Workflow execution status

## License | الترخيص

Part of Sahool Unified Platform v15.

## Support | الدعم

For issues and questions, contact the development team.
