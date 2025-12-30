# Multi-Agent System API Documentation
# وثائق واجهة برمجة التطبيقات لنظام الوكلاء المتعددين

## Overview | نظرة عامة

This API provides endpoints for the SAHOOL multi-agent agricultural advisory system. The system uses specialized AI agents to provide comprehensive agricultural advice.

توفر واجهة برمجة التطبيقات هذه نقاط نهاية لنظام SAHOOL الاستشاري الزراعي متعدد الوكلاء. يستخدم النظام وكلاء ذكاء اصطناعي متخصصين لتقديم استشارات زراعية شاملة.

## Base URL

```
http://localhost:8000/api/v1/advisor
```

## API Endpoints | نقاط النهاية

### 1. Query Processing | معالجة الاستفسارات

#### POST `/query`
Process a farmer query through the multi-agent system.

**Request Body:**
```json
{
  "query": "نباتات الطماطم لديها بقع صفراء على الأوراق، ما السبب؟",
  "farmer_id": "farmer_001",
  "field_id": "field_123",
  "crop_type": "tomato",
  "language": "ar",
  "priority": "high",
  "location": {
    "lat": 31.9454,
    "lon": 35.9284
  },
  "session_id": "session_abc123"
}
```

**Response:**
```json
{
  "query": "نباتات الطماطم لديها بقع صفراء",
  "answer": "البقع الصفراء على أوراق الطماطم يمكن أن تشير إلى نقص النيتروجين...",
  "query_type": "diagnosis",
  "agents_consulted": ["disease_expert", "field_analyst"],
  "execution_mode": "parallel",
  "confidence": 0.82,
  "recommendations": [
    "إجراء اختبار للتربة",
    "تطبيق سماد عضوي غني بالنيتروجين"
  ],
  "warnings": ["تجنب الإفراط في التسميد"],
  "next_steps": ["مراقبة النباتات لمدة أسبوع"],
  "language": "ar",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### POST `/query/stream`
Process query with streaming response for real-time updates.

**Request Body:** Same as `/query`

**Response:** Server-Sent Events (SSE) stream

```
data: {"status": "analyzing", "message_ar": "تحليل الاستفسار..."}

data: {"status": "routing", "query_type": "diagnosis", "agents": ["disease_expert"]}

data: {"status": "complete", "answer": "...", "confidence": 0.82}
```

---

### 2. Agent Discovery | اكتشاف الوكلاء

#### GET `/agents`
List all available AI agents.

**Response:**
```json
[
  {
    "agent_id": "disease_expert",
    "name": "Disease Expert",
    "role": "Disease Diagnosis & Treatment",
    "description": "Expert in diagnosing plant diseases and recommending treatments",
    "capabilities": ["diagnosis", "treatment", "pest_management"],
    "status": "active"
  },
  {
    "agent_id": "field_analyst",
    "name": "Field Analyst",
    "role": "Field Analysis & Monitoring",
    "description": "Specialized in field health analysis and satellite monitoring",
    "capabilities": ["field_analysis", "general_advisory"],
    "status": "active"
  }
]
```

#### GET `/agents/{agent_id}`
Get detailed information about a specific agent.

**Example:** `GET /agents/disease_expert`

**Response:**
```json
{
  "agent_id": "disease_expert",
  "name": "Disease Expert",
  "role": "Disease Diagnosis & Treatment",
  "description": "Expert in diagnosing plant diseases and recommending treatments",
  "capabilities": ["diagnosis", "treatment", "pest_management"],
  "status": "active"
}
```

#### POST `/agents/{agent_id}/consult`
Directly consult a specific agent.

**Request Body:**
```json
{
  "query": "كيف يمكنني تحسين إنتاجية الطماطم؟",
  "context": {
    "crop_type": "tomato",
    "growth_stage": "flowering"
  },
  "use_rag": true
}
```

**Response:**
```json
{
  "agent_name": "disease_expert",
  "agent_role": "Disease Diagnosis",
  "response": "لتحسين إنتاجية الطماطم في مرحلة الإزهار...",
  "confidence": 0.85,
  "execution_time": 2.3,
  "sources": ["plant_pathology_db", "crop_disease_manual"]
}
```

---

### 3. Council Operations | عمليات المجلس

#### POST `/council/convene`
Convene a council of agents for critical decision-making.

**Request Body:**
```json
{
  "council_type": "treatment_council",
  "query": "المحصول مصاب بمرض فطري، ما هو أفضل علاج إيكولوجي؟",
  "agent_ids": ["disease_expert", "ecological_expert"],
  "min_confidence": 0.7
}
```

**Response:**
```json
{
  "decision": "يُنصح باستخدام العلاج البيولوجي بدلاً من المبيدات الكيميائية",
  "confidence": 0.88,
  "consensus_level": 0.92,
  "participating_agents": ["disease_expert", "ecological_expert", "field_analyst"],
  "supporting_count": 3,
  "dissenting_count": 0,
  "conflicts_count": 0,
  "council_type": "treatment_council",
  "timestamp": "2024-01-15T11:00:00Z"
}
```

#### GET `/council/{council_id}/status`
Get the current status of a council session.

**Response:**
```json
{
  "council_id": "council_abc123",
  "status": "in_progress",
  "progress": 0.65,
  "current_phase": "deliberation",
  "started_at": "2024-01-15T10:00:00Z",
  "estimated_completion": "2024-01-15T10:15:00Z"
}
```

---

### 4. Monitoring | المراقبة

#### GET `/monitoring/{field_id}`
Get current monitoring status for a field.

**Example:** `GET /monitoring/field_123`

**Response:**
```json
{
  "field_id": "field_123",
  "is_active": true,
  "crop_type": "wheat",
  "interval": "daily",
  "last_check": "2024-01-15T08:00:00Z",
  "next_check": "2024-01-16T08:00:00Z",
  "alerts": [
    {
      "type": "disease_risk",
      "severity": "medium",
      "message": "خطر متوسط للإصابة بالصدأ"
    }
  ],
  "health_score": 0.78
}
```

#### POST `/monitoring/{field_id}/start`
Start continuous monitoring for a field.

**Request Body:**
```json
{
  "crop_type": "wheat",
  "monitoring_interval": "daily",
  "alerts_enabled": true,
  "alert_thresholds": {
    "ndvi_drop": 0.15,
    "disease_risk": 0.6
  },
  "agents_to_consult": ["field_analyst", "disease_expert"]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Monitoring started for field field_123",
  "message_ar": "تم بدء المراقبة للحقل field_123",
  "next_check": "2024-01-16T08:00:00Z"
}
```

#### POST `/monitoring/{field_id}/stop`
Stop continuous monitoring for a field.

**Response:**
```json
{
  "status": "success",
  "message": "Monitoring stopped for field field_123",
  "message_ar": "تم إيقاف المراقبة للحقل field_123"
}
```

---

### 5. Feedback & Metrics | الملاحظات والمقاييس

#### POST `/feedback`
Submit feedback on advisory responses.

**Request Body:**
```json
{
  "query_id": "query_xyz789",
  "rating": 5,
  "helpful": true,
  "comment": "شكراً، المعلومات كانت دقيقة وواضحة",
  "farmer_id": "farmer_001"
}
```

**Response:**
```json
{
  "feedback_id": "feedback_xyz456",
  "status": "success",
  "message": "شكراً لملاحظاتك القيمة! سنستخدمها لتحسين خدماتنا.",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

#### GET `/metrics`
Get performance and usage metrics for the multi-agent system.

**Response:**
```json
{
  "total_queries": 1523,
  "avg_response_time": 3.2,
  "avg_confidence": 0.83,
  "agent_usage": {
    "disease_expert": 456,
    "field_analyst": 389,
    "irrigation_advisor": 312
  },
  "query_types": {
    "diagnosis": 456,
    "irrigation": 312,
    "general_advisory": 755
  },
  "execution_modes": {
    "parallel": 823,
    "single_agent": 512,
    "council": 188
  },
  "success_rate": 0.94,
  "avg_rating": 4.3,
  "period": "all_time"
}
```

---

## Enums | التعدادات

### QueryType
- `diagnosis` - Disease diagnosis | تشخيص الأمراض
- `treatment` - Treatment recommendations | توصيات العلاج
- `irrigation` - Irrigation advice | نصائح الري
- `fertilization` - Fertilization recommendations | توصيات التسميد
- `pest_management` - Pest control | مكافحة الآفات
- `harvest_planning` - Harvest planning | تخطيط الحصاد
- `emergency` - Emergency situations | حالات الطوارئ
- `ecological_transition` - Ecological transition | التحول الإيكولوجي
- `market_analysis` - Market analysis | تحليل السوق
- `field_analysis` - Field analysis | تحليل الحقل
- `yield_prediction` - Yield prediction | التنبؤ بالمحصول
- `general_advisory` - General advisory | استشارة عامة

### ExecutionMode
- `parallel` - Parallel execution | تنفيذ متوازي
- `sequential` - Sequential execution | تنفيذ متتابع
- `council` - Council mode | وضع المجلس
- `single_agent` - Single agent | وكيل واحد

### Priority
- `normal` - Normal priority | أولوية عادية
- `high` - High priority | أولوية عالية
- `emergency` - Emergency | طوارئ

### CouncilType
- `diagnosis_council` - Diagnosis council | مجلس التشخيص
- `treatment_council` - Treatment council | مجلس العلاج
- `resource_council` - Resource council | مجلس الموارد
- `emergency_council` - Emergency council | مجلس الطوارئ
- `sustainability_council` - Sustainability council | مجلس الاستدامة
- `harvest_council` - Harvest council | مجلس الحصاد
- `planning_council` - Planning council | مجلس التخطيط

### MonitoringInterval
- `hourly` - Every hour | كل ساعة
- `daily` - Every day | كل يوم
- `weekly` - Every week | كل أسبوع
- `custom` - Custom interval | فترة مخصصة

---

## Error Responses | استجابات الأخطاء

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message in English | رسالة الخطأ بالعربية"
}
```

### Common Status Codes
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource not found)
- `500` - Internal Server Error
- `503` - Service Unavailable (system not initialized)

---

## Usage Examples | أمثلة الاستخدام

### Python Example

```python
import requests

# Process a query
response = requests.post(
    "http://localhost:8000/api/v1/advisor/query",
    json={
        "query": "كيف أعالج الصدأ في القمح؟",
        "farmer_id": "farmer_001",
        "crop_type": "wheat",
        "language": "ar",
        "priority": "high"
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Recommendations: {result['recommendations']}")
```

### cURL Example

```bash
# List all agents
curl -X GET "http://localhost:8000/api/v1/advisor/agents"

# Process a query
curl -X POST "http://localhost:8000/api/v1/advisor/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ما هي أفضل طريقة لري الطماطم؟",
    "language": "ar",
    "crop_type": "tomato"
  }'

# Start monitoring
curl -X POST "http://localhost:8000/api/v1/advisor/monitoring/field_123/start" \
  -H "Content-Type: application/json" \
  -d '{
    "crop_type": "wheat",
    "monitoring_interval": "daily",
    "alerts_enabled": true
  }'
```

### JavaScript/TypeScript Example

```typescript
// Process a query
const response = await fetch('http://localhost:8000/api/v1/advisor/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'نباتات الطماطم لديها بقع صفراء',
    language: 'ar',
    crop_type: 'tomato',
    priority: 'high'
  })
});

const result = await response.json();
console.log('Answer:', result.answer);
console.log('Confidence:', result.confidence);
```

---

## Interactive API Documentation

Once the service is running, you can access the interactive API documentation at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

يمكنك الوصول إلى وثائق واجهة برمجة التطبيقات التفاعلية على:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Notes | ملاحظات

1. **Authentication:** Currently, the API does not require authentication. In production, implement proper authentication and authorization.

   **المصادقة:** حالياً، لا تتطلب واجهة برمجة التطبيقات المصادقة. في الإنتاج، قم بتنفيذ المصادقة والتفويض المناسبين.

2. **Rate Limiting:** Consider implementing rate limiting for production use.

   **تحديد المعدل:** ضع في اعتبارك تنفيذ تحديد المعدل للاستخدام في الإنتاج.

3. **Monitoring Storage:** Currently uses in-memory storage. In production, use Redis or a database.

   **تخزين المراقبة:** يستخدم حالياً التخزين في الذاكرة. في الإنتاج، استخدم Redis أو قاعدة بيانات.

4. **Streaming Support:** Streaming endpoints work best with modern browsers and HTTP/2.

   **دعم البث:** تعمل نقاط نهاية البث بشكل أفضل مع المتصفحات الحديثة وHTTP/2.

---

## Support | الدعم

For issues or questions, please contact the SAHOOL development team.

لأية مشاكل أو أسئلة، يرجى الاتصال بفريق تطوير SAHOOL.
