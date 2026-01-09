# SAHOOL Code Fix Agent
# وكيل إصلاح الكود

AI-powered code analysis, bug fixing, and implementation agent for the SAHOOL platform.

وكيل ذكاء اصطناعي لتحليل وإصلاح وتنفيذ الكود لمنصة سهول.

## Features / الميزات

- **Code Analysis / تحليل الكود**: Comprehensive analysis for bugs, security issues, performance, and style
- **Bug Fixing / إصلاح الأخطاء**: Automated bug detection and fixing
- **PR Review / مراجعة طلبات السحب**: Intelligent pull request review
- **Test Generation / توليد الاختبارات**: Automatic unit test generation
- **Feature Implementation / تنفيذ الميزات**: Implement features from specifications

## Architecture / الهيكل

```
code-fix-agent/
├── src/
│   ├── agent/
│   │   ├── code_fix_agent.py    # Main agent class
│   │   ├── analyzers/           # Language-specific analyzers
│   │   ├── fixers/              # Bug fixers
│   │   └── generators/          # Code generators
│   ├── tools/                   # Utility tools
│   ├── knowledge/               # Knowledge base
│   ├── api/v1/                  # API endpoints
│   └── main.py                  # FastAPI entry point
└── tests/                       # Test suite
```

## Agent Type / نوع الوكيل

- **Type**: LEARNING (with Utility-Based decision making)
- **Layer**: SPECIALIST
- **Protocol**: A2A compliant
- **Integration**: MCP tools support

## API Endpoints / نقاط النهاية

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analyze` | POST | تحليل الكود |
| `/api/v1/fix` | POST | إصلاح الكود |
| `/api/v1/review` | POST | مراجعة PR |
| `/api/v1/generate-tests` | POST | توليد الاختبارات |
| `/api/v1/implement` | POST | تنفيذ ميزة |
| `/api/v1/feedback` | POST | تغذية راجعة للتعلم |
| `/healthz` | GET | فحص الحياة |
| `/readyz` | GET | فحص الجاهزية |
| `/metrics` | GET | مقاييس بروميثيوس |

## Quick Start / البداية السريعة

### Local Development / التطوير المحلي

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m uvicorn src.main:app --reload --port 8090
```

### Docker

```bash
# Build image
docker build -t sahool/code-fix-agent .

# Run container
docker run -p 8090:8090 sahool/code-fix-agent
```

## Usage Examples / أمثلة الاستخدام

### Analyze Code / تحليل الكود

```bash
curl -X POST http://localhost:8090/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def foo():\n    eval(input())",
    "language": "python"
  }'
```

### Fix Code / إصلاح الكود

```bash
curl -X POST http://localhost:8090/api/v1/fix \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b)\n    return a + b",
    "errors": [{"type": "SyntaxError", "line": 1, "message": "expected :"}],
    "language": "python"
  }'
```

## Configuration / التكوين

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8090 | Service port |
| `HOST` | 0.0.0.0 | Bind address |
| `LOG_LEVEL` | INFO | Logging level |
| `NATS_URL` | - | NATS server URL |

## Supported Languages / اللغات المدعومة

- Python (3.10+)
- TypeScript
- Dart

## Learning / التعلم

The agent learns from feedback to improve fix accuracy over time.
Submit feedback via `/api/v1/feedback`:

```json
{
  "fix_successful": true,
  "pattern_key": "bug_minimal",
  "reward": 1.0
}
```

## Testing / الاختبار

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## License / الترخيص

Proprietary - KAFAAT

---

**Version**: 1.0.0
**Last Updated**: January 2026
