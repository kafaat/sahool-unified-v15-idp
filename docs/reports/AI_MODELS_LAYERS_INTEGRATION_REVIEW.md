# تقرير مراجعة شاملة: موديلات الذكاء الاصطناعي والطبقات والتكامل
# Comprehensive Review: AI Models, Layers & Integration

**التاريخ**: 2026-03-06
**الإصدار**: 16.0.0
**المراجع**: Claude AI Review Agent

---

## 1. ملخص تنفيذي | Executive Summary

منصة سهول تحتوي على منظومة ذكاء اصطناعي شاملة تتضمن:
- **50+ موديل ذكاء اصطناعي** مسجل في سجل الموديلات الزراعية
- **6 مزودي LLM** (Ollama, Anthropic, OpenAI, Google, DeepSeek, vLLM)
- **13+ خدمة ذكاء اصطناعي** متخصصة
- **11 فئة وكلاء** (A2A Protocol)
- **11 سير عمل RAG** زراعي متقدم
- **13 مجموعة معرفية** زراعية
- **17 ملف في وحدة المعرفة** مع خط أنابيب استيعاب من 6 مراحل

---

## 2. سجل الموديلات الزراعية | Agricultural AI Models Registry

**الموقع**: `shared/ai/models_registry/` (الإصدار 1.0.0)

### 2.1 الفئات الخمس الرئيسية

| الفئة | عدد الموديلات | الوصف |
|-------|-------------|-------|
| **General Agriculture Decision** | 20+ | دعم القرار الزراعي العام |
| **Breeding & Bioscience** | 10+ | التربية والعلوم الحيوية |
| **Livestock & Veterinary** | 10+ | الثروة الحيوانية والبيطرية |
| **Remote Sensing & Geo** | 10+ | الاستشعار عن بعد والجغرافيا المكانية |
| **Specialty** | 10+ | الزراعة المتخصصة/العمودية |

### 2.2 الموديلات الرئيسية المميزة

| الموديل | النوع | المطور | الدعم العربي | الحالة |
|---------|------|--------|------------|--------|
| **ShengNong 3.0** | VLM متعدد الوسائط | China Agricultural University | لا | نشط |
| **CropWizard** | Expert System | NCSA/UIUC | لا | نشط |
| **PlantGPT** | LLM | Plant Genomics | لا | نشط |
| **AgroGPT** | VLM | MBZUAI | **نعم** | نشط |
| **Prithvi** | Foundation Model | NASA/IBM | لا | نشط |
| **AgroNT** | Transformer | Genomics | لا | نشط |
| **FarmVibes.AI** | Multi-modal | Microsoft | لا | نشط |

### 2.3 القدرات المعرفة (ModelCapability)

```
QA, DECISION_SUPPORT, EXPERT_CONSULTATION, PEST_DETECTION,
DISEASE_DETECTION, YIELD_PREDICTION, CROP_MONITORING,
KNOWLEDGE_GRAPH, GENOMICS, REMOTE_SENSING, SOIL_ANALYSIS,
IRRIGATION_OPTIMIZATION, WEATHER_FORECASTING
```

### 2.4 أنواع البنية المعمارية

- **LLM**: نماذج لغوية كبيرة
- **VLM**: نماذج رؤية-لغة
- **Foundation Model**: نماذج أساسية
- **Transformer**: نماذج محولات متخصصة

---

## 3. مزودو LLM | LLM Providers

**الموقع**: `shared/ai/llm_provider.py`

### 3.1 المزودون المدعومون (بترتيب الأولوية)

| المزود | الأولوية | النموذج الافتراضي | النوع | الحالة |
|--------|---------|------------------|------|--------|
| **Ollama** | 0 (الأعلى) | `codellama:13b` | محلي | Offline-first |
| **vLLM** | 0 | `deepseek-coder-6.7b-instruct` | محلي GPU | اختياري |
| **Anthropic** | 1 | `claude-3-haiku-20240307` | سحابي | يحتاج API key |
| **OpenAI** | 2 | `gpt-4o-mini` | سحابي | يحتاج API key |
| **Google** | 3 | `gemini-1.5-flash` | سحابي | يحتاج API key |
| **DeepSeek** | 4 | `deepseek-coder` | سحابي | يحتاج API key |

### 3.2 ميزات المزود الموحد

- **Failover تلقائي** بين المزودين
- **Circuit Breaker** لكل مزود (3 إخفاقات → فتح الدائرة)
- **تتبع التكلفة** وتسجيل المراجعة (Audit)
- **مقاييس Prometheus** لكل استدعاء
- **Offline-first**: أولوية Ollama المحلي

---

## 4. طبقات الذكاء الاصطناعي | AI Layers Architecture

### 4.1 خريطة الطبقات الكاملة

```
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 7: Applications                         │
│  copilot-api │ ai-chat-assistant │ advisory-service              │
├─────────────────────────────────────────────────────────────────┤
│                    Layer 6: Orchestration                        │
│  llm-orchestrator │ agent-registry │ ai-agents-core              │
│  SwarmCoordinator │ ConsensusManager │ AgentRouter               │
├─────────────────────────────────────────────────────────────────┤
│                    Layer 5: Knowledge & RAG                      │
│  UltraRAG (11 workflows) │ Knowledge Base (13 collections)      │
│  CRAG │ KnowledgeGraph │ AGROVOC │ VectorStore                  │
├─────────────────────────────────────────────────────────────────┤
│                    Layer 4: Intelligence                         │
│  crop-intelligence │ pest-detection │ yolo26-vision              │
│  CropVision │ NLP (AraBERT) │ Embeddings │ ExplainabilityEngine │
├─────────────────────────────────────────────────────────────────┤
│                    Layer 3: Memory & Context                     │
│  FarmMemory │ GraphMemory │ CollectiveMemory │ ExperienceLearner │
│  ContextCompressor │ FeedbackCollector                           │
├─────────────────────────────────────────────────────────────────┤
│                    Layer 2: Core AI Infrastructure               │
│  LLMProviderManager │ EmbeddingsAdapter │ OllamaClient          │
│  CircuitBreaker │ AIValidator │ AIAuditLogger │ Metrics          │
├─────────────────────────────────────────────────────────────────┤
│                    Layer 1: Safety & Guardrails                  │
│  ToolGuard │ GuardPolicy │ Validation │ Allowlists              │
│  InputFilter │ OutputFilter │ DomainAllowlist                    │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 تفصيل كل طبقة

#### الطبقة 1: الحماية والأمان (Guardrails)
**الموقع**: `shared/ai/guardrails/`, `shared/ai/validation.py`

| المكون | الوظيفة |
|--------|---------|
| `ToolGuard` | حارس أدوات الوكلاء |
| `GuardPolicy` | سياسات الحماية |
| `AIValidator` | التحقق من المدخلات/المخرجات |
| `DOMAIN_ALLOWLIST` | القائمة البيضاء للنطاقات |
| `BLOCKED_PATTERNS` | أنماط محظورة |

#### الطبقة 2: البنية التحتية الأساسية للذكاء الاصطناعي
**الموقع**: `shared/ai/`

| المكون | الوظيفة | الحالة |
|--------|---------|--------|
| `LLMProviderManager` | إدارة 6 مزودي LLM | مكتمل ✅ |
| `EmbeddingsAdapter` | 4 مزودي تضمين (Sentence Transformers, Ollama, OpenAI, Google) | مكتمل ✅ |
| `HuggingfaceProvider` | تضمينات عربية ومتعددة اللغات | مكتمل ✅ |
| `OllamaClient` | عميل Ollama المحلي | مكتمل ✅ |
| `CircuitBreaker` | نمط قاطع الدائرة | مكتمل ✅ |
| `AIAuditLogger` | تسجيل المراجعة مع تتبع التكلفة | مكتمل ✅ |
| `AIMetricsCollector` | مقاييس Prometheus | مكتمل ✅ |

#### الطبقة 3: الذاكرة والسياق
**الموقع**: `shared/ai/context_engineering/`, `shared/ai/graph_memory.py`, `shared/ai/experience_learning.py`

| المكون | الوصف | مستوحى من |
|--------|-------|-----------|
| `FarmMemory` | ذاكرة دائمة للعمليات الزراعية | Context Engineering |
| `ContextCompressor` | ضغط الرموز (3 مستويات: 80%/50%/25%) | Token Optimization |
| `GraphMemory` | ذاكرة بيانية مع خط أنابيب ECL | Cognee |
| `ExperienceLearner` | تعلم ذاتي مع توليد SOP | Acontext |
| `CollectiveMemory` | ذاكرة جماعية للوكلاء | Claude-Flow |
| `RecommendationEvaluator` | تقييم LLM-as-Judge | Quality Assessment |
| `FeedbackCollector` | جمع ملاحظات المستخدمين | Continuous Learning |

#### الطبقة 4: الذكاء والتحليل
**الموقع**: `shared/ai/crop_vision.py`, `shared/nlp/`, `shared/ai/embeddings.py`

| المكون | الوظيفة |
|--------|---------|
| `CropVisionAnalyzer` | رؤية حاسوبية (أمراض، آفات، مراحل نمو، NDVI) |
| `ArabicNLPProcessor` | معالجة لغة عربية (AraBERT) |
| `SentinelNDVIAnalyzer` | تحليل NDVI من صور القمر الصناعي |
| `ExplainabilityEngine` | تفسير التوصيات (ثنائي اللغة) |
| `AgMLDatasetManager` | مجموعات بيانات ML زراعية |

#### الطبقة 5: المعرفة و RAG
**الموقع**: `shared/ai/knowledge/`, `shared/ai/ultrarag/`

##### قاعدة المعرفة (13 مجموعة):
| المجموعة | الوصف |
|----------|-------|
| `CROP_KNOWLEDGE` | معرفة المحاصيل |
| `PEST_KNOWLEDGE` | معرفة الآفات |
| `SOIL_KNOWLEDGE` | معرفة التربة |
| `IRRIGATION_PRACTICES` | ممارسات الري |
| `FERTILIZER_KNOWLEDGE` | معرفة الأسمدة |
| `WEATHER_KNOWLEDGE` | معرفة الطقس |
| `REMOTE_SENSING_KNOWLEDGE` | الاستشعار عن بعد |
| `SMART_AGRICULTURE_KNOWLEDGE` | الزراعة الذكية |
| `PRECISION_FARMING_KNOWLEDGE` | الزراعة الدقيقة |
| `DIGITAL_TWIN_KNOWLEDGE` | التوأم الرقمي |
| `CROP_WATER_REQUIREMENTS` | متطلبات المياه |
| `RESEARCH_REFERENCES` | مراجع بحثية |
| `GENERAL_AGRICULTURE` | زراعة عامة |

##### خط أنابيب الاستيعاب (6 مراحل):
```
Extract → Clean → Chunk → Embed → Validate → Store
استخراج ← تنظيف ← تقطيع ← تضمين ← تحقق ← تخزين
```

##### مكونات المعرفة المتقدمة:
| المكون | الوظيفة |
|--------|---------|
| `CorrectiveRetrievalEngine` | استرجاع تصحيحي (CRAG) |
| `AgriculturalKnowledgeGraph` | رسم بياني للمعرفة الزراعية |
| `AgrovocLookup` | مصطلحات FAO AGROVOC |
| `KnowledgeFreshnessMonitor` | مراقبة حداثة المعرفة |
| `KnowledgeQualityGate` | بوابة جودة المعرفة |
| `DocumentVersionManager` | إدارة إصدارات الوثائق |
| `KnowledgeVectorStore` | تكامل مع مخزن المتجهات |

##### سير عمل UltraRAG (11 سير عمل):
1. `crop_advisory.yaml` - استشارات المحاصيل
2. `irrigation_advisory.yaml` - استشارات الري
3. `fertilizer_advisory.yaml` - استشارات الأسمدة
4. `pest_diagnosis.yaml` - تشخيص الآفات
5. `soil_analysis_advisory.yaml` - تحليل التربة
6. `weather_advisory.yaml` - استشارات الطقس
7. `remote_sensing_analysis.yaml` - تحليل الاستشعار عن بعد
8. `precision_farming_advisory.yaml` - الزراعة الدقيقة
9. `digital_twin_simulation.yaml` - محاكاة التوأم الرقمي
10. `knowledge_search.yaml` - البحث في المعرفة
11. `comprehensive_field_advisory.yaml` - استشارة شاملة للحقل

#### الطبقة 6: التنسيق والتوجيه
**الموقع**: `shared/ai/orchestration/`, `apps/services/llm-orchestrator-service/`

| المكون | الوظيفة |
|--------|---------|
| `AgentRouter` | توجيه المهام للوكلاء المناسبين |
| `SwarmCoordinator` | تنسيق السرب (Swarm Intelligence) |
| `ConsensusManager` | بروتوكولات الإجماع (Majority, Weighted, Raft, Quorum) |
| `AggregationStrategy` | استراتيجيات تجميع النتائج |
| `AgentExecutor` | منفذ الوكلاء في LLM Orchestrator |

#### الطبقة 7: التطبيقات
**الموقع**: `apps/services/`

| الخدمة | المنفذ | الوظيفة |
|--------|-------|---------|
| `copilot-api` | 8088 | مساعد ذكاء اصطناعي متعدد LLM مع RAG |
| `ai-chat-assistant` | 8260 | مساعد محادثة ذكي |
| `ai-advisor` | 8112 | خدمة استشارية |
| `advisory-service` | 8093 | توصيات واستشارات |
| `crop-intelligence-service` | 8095 | ذكاء المحاصيل |
| `pest-detection-service` | 8125 | كشف الآفات |
| `yolo26-vision-service` | 8150 | رؤية حاسوبية YOLO26 |
| `knowledge-graph` | 8140 | خدمة الرسم البياني المعرفي |

---

## 5. تكامل الخدمات | Service Integration

### 5.1 خريطة التكامل

```
┌──────────────────┐     NATS Events      ┌──────────────────┐
│  copilot-api     │◄────────────────────►│ advisory-service  │
│  (Port 8088)     │                       │ (Port 8093)       │
│  ┌─────────────┐ │                       │ ┌──────────────┐  │
│  │ RAG Service │ │                       │ │ Crop Advisor │  │
│  │ Tool Guards │ │                       │ │ Irrigation   │  │
│  │ Agent Route │ │                       │ │ Fertilizer   │  │
│  └─────────────┘ │                       │ └──────────────┘  │
└────────┬─────────┘                       └──────────────────┘
         │
    ┌────▼──────────┐     HTTP/NATS     ┌──────────────────┐
    │ llm-          │◄────────────────►│ ai-agents-core   │
    │ orchestrator  │                   │ (Port 8161)      │
    │ (Port 8220)   │                   │ CrewAI agents    │
    │ ┌───────────┐ │                   └──────────────────┘
    │ │ NLP Svc   │ │
    │ │ ML Svc    │ │     HTTP/NATS     ┌──────────────────┐
    │ │ Satellite │ │◄────────────────►│ yolo26-vision    │
    │ │ Crew Svc  │ │                   │ (Port 8150)      │
    │ └───────────┘ │                   │ YOLO26 Detection │
    └───────────────┘                   └──────────────────┘
         │
    ┌────▼──────────┐                   ┌──────────────────┐
    │ knowledge-    │◄─── Vector DB ──►│ Vector Store     │
    │ graph         │                   │ (Qdrant/SQLite)  │
    │ (Port 8140)   │                   └──────────────────┘
    └───────────────┘
```

### 5.2 نقاط التكامل عبر NATS

| الموضوع (Subject) | المنشئ | المستهلك |
|-------------------|--------|---------|
| `sahool.vision.pest_detected` | yolo26-vision | advisory-service, notification |
| `sahool.vision.disease_detected` | yolo26-vision | crop-intelligence, advisory |
| `sahool.vision.critical_alert` | yolo26-vision | notification, alert-service |
| `sahool.vision.plant_count_completed` | yolo26-vision | field-intelligence |
| `sahool.field.created` | field-management | vegetation-analysis, indicators |
| `sahool.weather.alert` | weather-service | advisory, irrigation-smart |

### 5.3 تكامل LLM Orchestrator

خدمة `llm-orchestrator-service` تعمل كنقطة مركزية تدمج:
- **NLPService**: معالجة اللغة العربية (AraBERT)
- **SatelliteService**: تحليل NDVI
- **MLService**: مجموعات بيانات AgML
- **CrewService**: تنسيق وكلاء CrewAI
- **AGLTrainer**: تدريب النماذج
- **FeedbackCollector**: جمع الملاحظات

---

## 6. الفجوات المحددة | Identified Gaps

### 6.1 فجوات حرجة (Critical Gaps) 🔴

| # | الفجوة | الوصف | التأثير |
|---|-------|-------|---------|
| G-01 | **نموذج Anthropic قديم** | `llm_provider.py` يستخدم `claude-3-haiku-20240307` - نموذج قديم، يجب تحديثه إلى `claude-haiku-4-5-20251001` أو أحدث | أداء أقل من المتوقع |
| G-02 | **ضعف الدعم العربي في سجل الموديلات** | من 50+ موديل، **موديل واحد فقط** (AgroGPT) يدعم العربية - وهو نقطة ضعف كبيرة لمنصة تستهدف الشرق الأوسط | فجوة وظيفية رئيسية |
| G-03 | **عدم وجود تكامل فعلي للموديلات الخارجية** | سجل الموديلات يحتوي على Connectors (ShengNong, CropWizard, PlantGPT, AgroGPT) لكن التكامل الفعلي غير مؤكد - لا توجد API keys أو اختبارات تكامل | موديلات مسجلة لكن غير متصلة |
| G-04 | **عدم ربط Knowledge Base بالخدمات** | قاعدة المعرفة (`shared/ai/knowledge/`) شاملة جداً لكن لا يوجد استيراد مباشر لها في خدمات مثل `advisory-service` أو `copilot-api` | معرفة معزولة |

### 6.2 فجوات متوسطة (Medium Gaps) 🟠

| # | الفجوة | الوصف | التأثير |
|---|-------|-------|---------|
| G-05 | **عدم وجود اختبارات تكامل AI-to-AI** | لا توجد اختبارات تتحقق من تدفق البيانات بين طبقات الذكاء الاصطناعي | صعوبة اكتشاف الأخطاء |
| G-06 | **تكرار في مزودي التضمين** | `embeddings.py` و `huggingface_provider.py` و `ot_embeddings.py` كلها توفر تضمينات - يوجد تداخل | تعقيد غير ضروري |
| G-07 | **UltraRAG غير متصل بالخدمات** | 11 سير عمل RAG معرفة لكن لا يوجد دليل على استخدامها في خدمات الإنتاج | سير عمل معطلة |
| G-08 | **غياب تكامل vLLM في Orchestrator** | `LLMProvider` يعرف vLLM لكن `llm-orchestrator-service` لا يستخدمه | قدرة GPU المحلية غير مستغلة |
| G-09 | **Orchestration اختيارية** | `ORCHESTRATION_AVAILABLE` معرف كـ optional import مما يعني أن الـ SwarmCoordinator و ConsensusManager قد لا يعملان | قدرات تنسيق محدودة |
| G-10 | **عدم وجود Health Checks للموديلات** | لا توجد آلية للتحقق من صحة الموديلات المحلية (Ollama) قبل استخدامها | فشل صامت |

### 6.3 فجوات تحسينية (Enhancement Gaps) 🟡

| # | الفجوة | الوصف | التأثير |
|---|-------|-------|---------|
| G-11 | **غياب A/B Testing للموديلات** | لا توجد آلية لاختبار أداء موديلات مختلفة على نفس المهمة | عدم القدرة على التحسين المستمر |
| G-12 | **غياب Model Versioning في الإنتاج** | سجل الموديلات لا يتتبع إصدارات الموديلات المنشورة فعلياً | صعوبة التراجع |
| G-13 | **عدم استخدام GRPO Trainer** | `grpo_trainer.py` موجود لكن لا يوجد دليل على استخدامه | تدريب غير مستغل |
| G-14 | **Diffusion Module فارغ/هيكلي** | `shared/ai/diffusion/` موجود لكن قد يكون هيكلي فقط | قدرة توليد صور غير مفعلة |
| G-15 | **عدم تكامل MCP مع RAG** | `shared/ai/ultrarag/mcp_tools.py` يعرف أدوات MCP لكن `mcp-server` (Port 8201) وصفه "skeleton" | MCP غير مكتمل |
| G-16 | **Google Gemini API قديم** | يستخدم `v1beta` endpoint بدلاً من `v1` المستقر | عدم استقرار |
| G-17 | **عدم وجود Caching لاستدعاءات LLM** | `LLMProviderManager` لا يستخدم Redis لتخزين مؤقت للردود المتكررة | تكلفة وأداء |
| G-18 | **غياب Streaming في جميع المزودين** | جميع استدعاءات LLM تستخدم `"stream": False` | تجربة مستخدم بطيئة |

### 6.4 فجوات في التوثيق 📝

| # | الفجوة | الوصف |
|---|-------|-------|
| G-19 | **غياب Architecture Decision Record للذكاء الاصطناعي** | لا يوجد ADR يوثق قرارات اختيار الموديلات والبنية المعمارية |
| G-20 | **عدم توثيق تدفق البيانات بين الطبقات** | لا يوجد رسم بياني يوضح كيف تتدفق البيانات من الاستيعاب إلى التوصية |

---

## 7. مصفوفة التكامل | Integration Matrix

### 7.1 حالة التكامل بين المكونات

| المكون المصدر | → | المكون الهدف | الحالة | الملاحظات |
|--------------|---|-------------|--------|----------|
| `LLMProviderManager` | → | `copilot-api` | ✅ متصل | عبر shared imports |
| `LLMProviderManager` | → | `llm-orchestrator` | ✅ متصل | عبر agent executor |
| `models_registry` | → | `LLMProviderManager` | ❌ غير متصل | الموديلات مسجلة لكن غير مستخدمة في التوليد |
| `Knowledge Base` | → | `UltraRAG` | ⚠️ جزئي | VectorStore integration موجود لكن التفعيل غير واضح |
| `Knowledge Base` | → | `copilot-api` | ❌ غير متصل | RAG service خاص بـ copilot |
| `UltraRAG workflows` | → | `advisory-service` | ❌ غير متصل | لا يوجد استيراد |
| `CropVisionAnalyzer` | → | `yolo26-vision` | ⚠️ مكرر | كلاهما يوفر رؤية حاسوبية |
| `NLP (AraBERT)` | → | `llm-orchestrator` | ✅ متصل | عبر NLPService |
| `Embeddings` | → | `VectorStore` | ✅ متصل | عبر EmbeddingsAdapter |
| `Guardrails` | → | `copilot-api` | ✅ متصل | Tool guards مفعلة |
| `Feedback` | → | `model_training` | ⚠️ جزئي | التصدير متاح لكن لا يوجد خط أنابيب تلقائي |
| `ExperienceLearner` | → | أي خدمة | ❌ غير متصل | موجود لكن غير مستخدم في الإنتاج |
| `GraphMemory` | → | `knowledge-graph` | ❌ غير متصل | مكونان منفصلان |
| `Orchestration` | → | `llm-orchestrator` | ⚠️ اختياري | import اختياري قد يفشل |
| `AGROVOC` | → | `Knowledge Base` | ✅ متصل | تكامل مصطلحات |
| `CRAG` | → | `UltraRAG` | ⚠️ جزئي | موجود في knowledge لكن غير مربوط بالـ pipeline |
| `CircuitBreaker` | → | جميع المزودين | ✅ متصل | مفعل لكل مزود LLM |

---

## 8. التوصيات | Recommendations

### 8.1 أولوية عاجلة (Sprint 1)

1. **تحديث نموذج Anthropic** → `claude-haiku-4-5-20251001` (G-01)
2. **ربط Knowledge Base بخدمات الإنتاج** → إنشاء adapter في `copilot-api` و `advisory-service` (G-04)
3. **تفعيل UltraRAG workflows** → ربط سير العمل بخدمات الاستشارة (G-07)

### 8.2 أولوية متوسطة (Sprint 2-3)

4. **إضافة موديلات عربية** → دمج AraBERT variants و Jais model في السجل (G-02)
5. **توحيد مزودي التضمين** → دمج `embeddings.py` و `huggingface_provider.py` في واجهة واحدة (G-06)
6. **إضافة LLM Response Caching** → Redis-based caching في `LLMProviderManager` (G-17)
7. **تفعيل Streaming** → SSE streaming لتحسين تجربة المستخدم (G-18)

### 8.3 أولوية طويلة المدى (Sprint 4+)

8. **A/B Testing Framework** → لمقارنة أداء الموديلات (G-11)
9. **كتابة ADR** → توثيق قرارات البنية المعمارية للذكاء الاصطناعي (G-19)
10. **تفعيل MCP Server** → ربط أدوات RAG بخادم MCP (G-15)

---

## 9. إحصائيات سريعة | Quick Stats

| المقياس | القيمة |
|---------|--------|
| إجمالي موديلات AI المسجلة | 50+ |
| مزودو LLM | 6 |
| خدمات AI | 13+ |
| فئات الوكلاء | 11 |
| مجموعات المعرفة | 13 |
| سير عمل RAG | 11 |
| ملفات في `shared/ai/` | 100+ |
| طبقات البنية المعمارية | 7 |
| الفجوات المحددة | 20 |
| الفجوات الحرجة | 4 |

---

*آخر تحديث: 2026-03-06*
*المراجع: Claude AI Review Agent*
