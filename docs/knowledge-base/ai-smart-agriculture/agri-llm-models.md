---
title: النماذج اللغوية الزراعية الكبيرة - Agricultural Large Language Models
description: دليل شامل لنماذج الذكاء الاصطناعي اللغوية المتخصصة بالزراعة وتطبيقاتها
tags:
  - llm
  - agri-llm
  - agrigpt
  - arabert
  - rag
  - ai-models
category: ai-smart-agriculture
last_updated: 2026-03-03
version: 1.0.0
---

# النماذج اللغوية الزراعية الكبيرة | Agricultural Large Language Models (AgriLLMs)

دليل شامل لنماذج AI اللغوية المتخصصة بالزراعة، من البحث الأكاديمي إلى التطبيق العملي.

Comprehensive guide to agriculture-specialized AI language models, from academic research to practical application.

---

## نظرة عامة | Overview

النماذج اللغوية العامة (GPT-4, Claude, Gemini) تفتقر للمعرفة الزراعية المتخصصة. النماذج الزراعية المتخصصة (AgriLLMs) تسد هذه الفجوة عبر:

1. **تدريب مسبق على بيانات زراعية** (أوراق بحثية، أدلة محاصيل، بيانات طقس)
2. **ضبط دقيق للمهام الزراعية** (تشخيص أمراض، توصيات ري، تنبؤ إنتاج)
3. **RAG زراعي متخصص** (استرجاع من قواعد معرفة زراعية موثوقة)

---

## تطور النماذج الزراعية | AgriLLM Evolution Timeline

```
2022        2023          2024              2025
 │           │             │                 │
 v           v             v                 v
AgriBERT  ChatAgri     AgriLLM          AgriGPT
(تكييف    (محادثة      (نموذج لغوي     (منظومة متكاملة:
 BERT      زراعية)      زراعي كبير)     Tri-RAG + AgriBench
 للنصوص                                  + رؤية حاسوبية)
 الزراعية)
                        AgroLLM          AgriGPT-VL
                        (ربط المزارعين   (رؤية + لغة
                         بالممارسات)      زراعية)

                        天工开悟 (HIT)     九壤耘星 (Huawei)
                        (22 محصول/95 صنف) (6 نماذج فرعية)
```

---

## النماذج الرئيسية | Key Models

### 1. AgriGPT (2025) — المنظومة الأشمل

| الخاصية | Property | القيمة |
|---------|----------|--------|
| **النموذج الأساسي** | Base Model | Qwen3-8B |
| **طريقة التدريب** | Training Method | LoRA Continual Pretraining |
| **نظام RAG** | RAG System | **Tri-RAG**: 3 قنوات (كثيف + متناثر + رسم معرفي) |
| **مقياس الأداء** | Benchmark | **AgriBench-13K**: 13 مهمة بتعقيدات مختلفة |
| **الترخيص** | License | مفتوح المصدر (النماذج + البيانات + الكود) |

**Tri-RAG Architecture**:
```
استعلام المزارع
    │
    ├──> استرجاع كثيف (Dense Retrieval) ──────────┐
    │    تشابه دلالي عبر embeddings                │
    │                                               │
    ├──> استرجاع متناثر (Sparse Retrieval) ────────┤──> دمج + تصفية ──> LLM ──> إجابة
    │    مطابقة كلمات مفتاحية (BM25)               │
    │                                               │
    └──> استدلال رسم معرفي (KG Reasoning) ─────────┘
         تتبع العلاقات بين المفاهيم الزراعية
```

### 2. AgriGPT-VL (2025) — الرؤية + اللغة

| الخاصية | Property | القيمة |
|---------|----------|--------|
| **القدرات** | Capabilities | تشخيص أمراض من صور + وصف نصي |
| **الأداء** | Performance | يتفوق على النماذج العامة في المهام الزراعية |
| **المقاييس** | Benchmarks | MMLU, ARC, MMBench, MMMU, SEED-Bench |

### 3. 天工开悟 Tiangong Kaiwu (HIT, الصين)

| الخاصية | Property | القيمة |
|---------|----------|--------|
| **التغطية** | Coverage | **22 محصول، 95 صنف** |
| **الدقة** | Accuracy | خطأ التنبؤ **< 10%** |
| **المهام** | Tasks | تنبؤ نمو، تقدير إنتاج، تشخيص أمراض |
| **المطور** | Developer | Harbin Institute of Technology |

### 4. 九壤耘星 Jiurang Yunxing (Huawei + NWAFU, 2025)

| الخاصية | Property | القيمة |
|---------|----------|--------|
| **النماذج الفرعية** | Sub-models | **6**: فاكهة، ماشية، دواجن، مصايد، محاصيل، غابات |
| **التغطية** | Coverage | سلسلة القيمة الكاملة |
| **التكامل** | Integration | Huawei Cloud + IoT |
| **المطور** | Developer | Huawei + Northwest A&F University |

### 5. AgroLLM (2025)

| الخاصية | Property | القيمة |
|---------|----------|--------|
| **الهدف** | Goal | ربط المزارعين بالممارسات الزراعية المثلى |
| **اللغات** | Languages | متعدد اللغات |
| **التركيز** | Focus | سهولة الوصول للمزارعين التقليديين |

---

## مجموعات البيانات الزراعية | Agricultural Datasets

| المجموعة | Dataset | الحجم | النوع | الاستخدام |
|---------|---------|-------|------|----------|
| **Agri-342K** | 342K عينة | تعليمات | ضبط دقيق للنماذج |
| **AgriBench-13K** | 13K عينة، 13 مهمة | تقييم | قياس أداء AgriLLMs |
| **PlantVillage** | 54,306 صورة | صور أمراض | تدريب رؤية حاسوبية |
| **AgML Datasets** | متعدد | صور + بيانات | تعلم آلي زراعي |

---

## التحديات الحالية | Current Challenges

| التحدي | Challenge | الوصف |
|--------|-----------|-------|
| **تعميم النماذج** | Model Generalization | أداء ضعيف عند الانتقال بين مناطق/محاصيل مختلفة |
| **اللغة العربية** | Arabic Support | لا يوجد نموذج زراعي عربي متخصص |
| **الاستدلال المنطقي** | Reasoning | ضعف في الاستدلال المعقد متعدد الخطوات |
| **البيانات المتعددة الوسائط** | Multimodal Data | دمج صور + مستشعرات + نصوص |
| **تحديث المعرفة** | Knowledge Update | المعرفة الزراعية تتغير موسمياً |
| **التعاون بين الوكلاء** | Agent Collaboration | تنسيق عدة نماذج متخصصة |

---

## استراتيجية SAHOOL للنماذج الزراعية | SAHOOL AgriLLM Strategy

### البنية الحالية | Current Architecture

```
SAHOOL AI Stack:
├── LLM Provider (shared/ai/llm_provider.py)
│   ├── Claude (Anthropic)     ← عام، عالي الجودة
│   ├── OpenAI GPT             ← عام
│   ├── Gemini (Google)        ← عام
│   ├── DeepSeek               ← كود
│   └── Ollama (Local)         ← محلي، بدون إنترنت
│       ├── codellama:7b
│       ├── deepseek-coder:6.7b
│       ├── mistral:7b
│       └── qwen2.5-coder:7b
│
├── Embeddings (shared/ai/embeddings.py)
│   ├── Sentence Transformers  ← محلي
│   ├── Ollama embeddings      ← محلي
│   ├── OpenAI embeddings      ← سحابي
│   └── Google embeddings      ← سحابي
│
├── UltraRAG (shared/ai/ultrarag/)
│   ├── AgriRAGProvider        ← 4 استعلامات زراعية + CRAG
│   └── 6 workflows            ← تسميد، تربة، طقس، استشعار، آفات، شامل
│
├── Arabic NLP (shared/nlp/)
│   └── AraBERT                ← تصنيف نوايا + كيانات زراعية
│
└── Knowledge Base (shared/ai/knowledge/)
    ├── 63+ وثيقة ثنائية اللغة
    ├── 17+ مصدر موثوق
    └── فلتر إقليمي (AgriRegion)
```

### خارطة طريق النموذج الزراعي العربي | Arabic AgriLLM Roadmap

| المرحلة | Phase | الهدف | المتطلبات |
|---------|-------|-------|----------|
| **الحالي** | Current | RAG زراعي عبر AraBERT + LLMs عامة | قاعدة معرفة (متوفرة ✓) |
| **المرحلة 1** | Phase 1 | ضبط دقيق لنموذج عربي صغير (7B) على بيانات زراعية | مجموعة بيانات Agri-AR (بناء) |
| **المرحلة 2** | Phase 2 | Tri-RAG عربي (كثيف + متناثر + رسم معرفي) | رسم معرفي زراعي عربي |
| **المرحلة 3** | Phase 3 | نموذج رؤية+لغة زراعي (مثل AgriGPT-VL) | بيانات صور محاصيل MENA |

### الفرق بين SAHOOL والنماذج الأخرى | SAHOOL vs Others

| الميزة | AgriGPT | 天工开悟 | SAHOOL (الهدف) |
|--------|---------|---------|----------------|
| اللغة العربية | لا | لا | **نعم** |
| العمل بدون إنترنت | لا | لا | **نعم (Ollama)** |
| محاصيل MENA | جزئي | لا | **63+ وثيقة** |
| مناخ MENA | لا | لا | **7 مناطق مناخية** |
| تكييف إقليمي | لا | لا | **AgriRegion filter** |
| مصادر موثوقة عربية | لا | لا | **17+ مصدر** |

---

> **ملاحظة**: مجال النماذج الزراعية الكبيرة يتطور بسرعة. AgriGPT (2025) يمثل أحدث المنظومات المتكاملة، لكن لا يوجد حتى الآن نموذج زراعي عربي متخصص - وهذه فرصة استراتيجية لـ SAHOOL.

*آخر تحديث: مارس 2026*
