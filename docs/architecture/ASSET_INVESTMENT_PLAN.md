# خطة استثمار الأصول غير المستغلة

# Under-Utilized Assets Investment Plan

**الإصدار:** 1.0.0
**التاريخ:** ديسمبر 2025
**المنهج:** Field-First Asset Monetization

---

## الملخص التنفيذي

> **SAHOOL لا يعاني من نقص موارد، بل من موارد قوية لم تُفعّل بعد**

بناءً على المراجعة الاستراتيجية للكود، تم تأكيد وجود **5 فئات من الأصول غير المستغلة** يمكن تحويلها إلى قيمة ميدانية مباشرة دون إعادة كتابة.

---

## 📊 نتائج التحليل الفعلي

### 1. Event Infrastructure (NATS)

| المؤشر            | الحالة                   |
| ----------------- | ------------------------ |
| ملفات تستخدم NATS | 35 ملف                   |
| في الخدمات النشطة | ❌ معظمها في `archive/`  |
| في shared/libs    | ✅ بنية جاهزة غير مفعّلة |

**الفجوة:** البنية التحتية للأحداث موجودة في `shared/libs/events/` لكن الخدمات النشطة تستخدم REST مباشرة.

### 2. Analysis Services Output

| الخدمة             | نوع المخرج                 | Action Template |
| ------------------ | -------------------------- | --------------- |
| fertilizer-advisor | `FertilizerRecommendation` | ❌ غير موجود    |
| irrigation-smart   | `IrrigationSchedule`       | ❌ غير موجود    |
| crop-health-ai     | Disease detection          | ❌ غير موجود    |
| yield-engine       | Yield prediction           | ❌ غير موجود    |

**الفجوة:** التحليلات تُنتج Insights لكن لا تُترجم إلى Tasks قابلة للتنفيذ.

### 3. Shared Packages Adoption

| Package              | apps/web | apps/admin | apps/mobile |
| -------------------- | -------- | ---------- | ----------- |
| @sahool/shared-ui    | ✅       | ✅         | ❌          |
| @sahool/shared-hooks | ✅       | ✅         | ❌          |
| Offline Components   | ❌       | ❌         | ❌          |

**الفجوة:** لا توجد مكونات Offline موحدة في المكتبات المشتركة.

### 4. Historical Data Usage

| الخدمة             | بيانات تاريخية | Trend Analysis                | Seasonal Comparison |
| ------------------ | -------------- | ----------------------------- | ------------------- |
| satellite-service  | ✅ timeseries  | ⚠️ بسيط (improving/declining) | ❌                  |
| weather-advanced   | ✅             | ❌                            | ❌                  |
| indicators-service | ✅             | ❌                            | ❌                  |

**الفجوة:** البيانات التاريخية مخزنة لكن لا تُستخدم للمقارنات الموسمية أو اكتشاف الأنماط.

---

## 🎯 خطة التنفيذ

### Phase 1: Quick Wins (0-30 يوم)

#### 1.1 Action Template Standard

**الهدف:** كل تحليل يُنتج قالب إجراء قابل للتنفيذ

```python
# shared/contracts/action_template.py

class ActionTemplate(BaseModel):
    """قالب الإجراء الموحد"""

    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType  # IRRIGATION, FERTILIZATION, SPRAY, INSPECTION

    # What
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str

    # Why (Analysis Source)
    source_service: str
    source_analysis_id: str
    confidence: float = Field(ge=0, le=1)

    # When
    urgency: UrgencyLevel
    deadline: Optional[datetime]
    optimal_window: Optional[TimeWindow]

    # How
    steps: List[ActionStep]
    resources_needed: List[Resource]
    estimated_duration_minutes: int

    # Fallback (Field-First)
    offline_executable: bool = True
    fallback_instructions: str

    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ActionStatus = ActionStatus.PENDING
```

**الملفات المتأثرة:**

- `shared/contracts/action_template.py` (جديد)
- `apps/services/fertilizer-advisor/src/main.py` (تحديث المخرجات)
- `apps/services/irrigation-smart/src/main.py` (تحديث المخرجات)
- `apps/services/crop-health-ai/src/main.py` (تحديث المخرجات)

---

#### 1.2 NATS as Notification Spine

**الهدف:** تفعيل NATS للتنبيهات بدلاً من REST المباشر

```
قبل:
  analysis-service → REST → notification-service → mobile

بعد:
  analysis-service → NATS (analysis.completed) → notification-service → mobile
```

**التنفيذ:**

```python
# apps/services/satellite-service/src/events.py

from shared.libs.events.producer import EventProducer
from shared.libs.events.envelope import EventEnvelope

class SatelliteEventPublisher:
    def __init__(self, nats_client):
        self.producer = EventProducer(nats_client)

    async def publish_ndvi_computed(self, field_id: str, ndvi_value: float, action: ActionTemplate):
        envelope = EventEnvelope(
            event_type="ndvi.computed.v1",
            data={
                "field_id": field_id,
                "ndvi_value": ndvi_value,
                "action": action.dict() if action else None,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.producer.publish(envelope)
```

**الملفات المتأثرة:**

- `apps/services/satellite-service/src/events.py` (جديد)
- `apps/services/notification-service/src/subscribers.py` (جديد)
- `docker-compose.yml` (تفعيل NATS)

---

#### 1.3 Unified Offline UX Components

**الهدف:** مكونات موحدة للتعامل مع حالة عدم الاتصال

```typescript
// packages/shared-ui/src/components/offline/index.ts

export { OfflineBanner } from "./OfflineBanner";
export { StaleDataBadge } from "./StaleDataBadge";
export { SyncStatusIndicator } from "./SyncStatusIndicator";
export { OfflineAwareWrapper } from "./OfflineAwareWrapper";
```

```typescript
// packages/shared-ui/src/components/offline/OfflineAwareWrapper.tsx

interface OfflineAwareWrapperProps {
  children: React.ReactNode;
  lastUpdated?: Date;
  staleThresholdMinutes?: number;
  offlineFallback?: React.ReactNode;
}

export function OfflineAwareWrapper({
  children,
  lastUpdated,
  staleThresholdMinutes = 30,
  offlineFallback
}: OfflineAwareWrapperProps) {
  const isOnline = useOnlineStatus();
  const isStale = lastUpdated &&
    (Date.now() - lastUpdated.getTime()) > staleThresholdMinutes * 60 * 1000;

  return (
    <div className="relative">
      {!isOnline && <OfflineBanner />}
      {isStale && <StaleDataBadge lastUpdated={lastUpdated} />}
      {!isOnline && offlineFallback ? offlineFallback : children}
    </div>
  );
}
```

**الملفات الجديدة:**

- `packages/shared-ui/src/components/offline/OfflineBanner.tsx`
- `packages/shared-ui/src/components/offline/StaleDataBadge.tsx`
- `packages/shared-ui/src/components/offline/SyncStatusIndicator.tsx`
- `packages/shared-ui/src/components/offline/OfflineAwareWrapper.tsx`
- `packages/shared-ui/src/components/offline/index.ts`

---

### Phase 2: Medium Investment (31-60 يوم)

#### 2.1 Historical Geospatial Intelligence

**الهدف:** تفعيل المقارنات التاريخية والموسمية

```python
# apps/services/satellite-service/src/historical.py

class HistoricalAnalyzer:
    """محلل البيانات التاريخية"""

    async def compare_seasons(
        self,
        field_id: str,
        current_date: date,
        lookback_years: int = 2
    ) -> SeasonalComparison:
        """مقارنة الموسم الحالي بالمواسم السابقة"""

        current_season = await self.get_season_data(field_id, current_date)
        historical_seasons = []

        for year in range(1, lookback_years + 1):
            past_date = current_date.replace(year=current_date.year - year)
            season = await self.get_season_data(field_id, past_date)
            historical_seasons.append(season)

        return SeasonalComparison(
            current=current_season,
            historical=historical_seasons,
            deviation_percent=self._calculate_deviation(current_season, historical_seasons),
            risk_areas=self._identify_risk_areas(current_season, historical_seasons),
            insights=self._generate_insights(current_season, historical_seasons)
        )

    async def detect_chronic_issues(self, field_id: str) -> List[ChronicIssue]:
        """اكتشاف المشاكل المزمنة في الحقل"""

        # Analyze 3 years of data
        issues = []
        ndvi_history = await self.get_ndvi_history(field_id, years=3)

        # Find zones that consistently underperform
        for zone in self._identify_zones(ndvi_history):
            if zone.avg_ndvi < 0.4 and zone.consistency > 0.7:
                issues.append(ChronicIssue(
                    zone_geometry=zone.geometry,
                    issue_type="chronic_low_vigor",
                    severity=self._calculate_severity(zone),
                    recommended_actions=self._suggest_remediation(zone)
                ))

        return issues
```

**Endpoint جديد:**

```
GET /api/v1/fields/{field_id}/historical-analysis
GET /api/v1/fields/{field_id}/seasonal-comparison
GET /api/v1/fields/{field_id}/chronic-issues
```

---

#### 2.2 Docs as Guardrails

**الهدف:** تحويل الوثائق إلى فحوصات تلقائية

```yaml
# .github/PULL_REQUEST_TEMPLATE.md

## Field-First Checklist

### Required (Block Merge if Not Checked)
- [ ] Does this change work offline? (أو يوجد fallback)
- [ ] If analysis service: Does it output ActionTemplate?
- [ ] If frontend: Does it use OfflineAwareWrapper?

### Recommended
- [ ] Uses NATS for async communication
- [ ] Has Field-First tests
- [ ] Updates relevant documentation
```

```yaml
# .github/workflows/field-first-check.yml

name: Field-First Architecture Check

on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for offline support
        run: |
          if grep -r "fetch\|axios" apps/mobile/; then
            if ! grep -r "OfflineAware\|offline\|cache" apps/mobile/; then
              echo "::warning::Mobile code uses network calls without offline handling"
            fi
          fi

      - name: Check analysis services
        run: |
          for service in apps/services/*-advisor apps/services/*-engine; do
            if [ -d "$service" ]; then
              if ! grep -q "ActionTemplate" "$service/src/main.py"; then
                echo "::warning::$service does not output ActionTemplate"
              fi
            fi
          done
```

---

### Phase 3: Strategic Investment (61-90 يوم)

#### 3.1 Event-Driven Playbooks

**الهدف:** سلاسل إجراءات تلقائية بناءً على الأحداث

```python
# shared/playbooks/engine.py

class PlaybookEngine:
    """محرك Playbooks للإجراءات التلقائية"""

    playbooks = {
        "drought_response": DroughtResponsePlaybook(),
        "disease_outbreak": DiseaseOutbreakPlaybook(),
        "yield_optimization": YieldOptimizationPlaybook()
    }

    async def trigger(self, event: EventEnvelope):
        """تفعيل Playbook بناءً على الحدث"""

        for name, playbook in self.playbooks.items():
            if playbook.matches(event):
                await playbook.execute(event)


class DroughtResponsePlaybook:
    """Playbook الاستجابة للجفاف"""

    def matches(self, event: EventEnvelope) -> bool:
        return (
            event.event_type == "ndvi.computed.v1" and
            event.data.get("ndvi_value", 1) < 0.3
        ) or (
            event.event_type == "weather.alert.v1" and
            event.data.get("alert_type") == "drought"
        )

    async def execute(self, event: EventEnvelope):
        field_id = event.data["field_id"]

        # Step 1: Get irrigation recommendation
        irrigation = await self.irrigation_service.get_emergency_schedule(field_id)

        # Step 2: Create tasks
        tasks = [
            ActionTemplate(
                action_type=ActionType.IRRIGATION,
                title_ar="ري طوارئ - جفاف",
                urgency=UrgencyLevel.CRITICAL,
                steps=irrigation.steps
            )
        ]

        # Step 3: Notify
        await self.notification_service.send_critical_alert(
            field_id=field_id,
            alert_type="drought_response",
            tasks=tasks
        )

        # Step 4: Log playbook execution
        await self.audit_service.log(
            action="playbook.executed",
            playbook="drought_response",
            field_id=field_id
        )
```

---

#### 3.2 Operations Analytics

**الهدف:** قياس فعالية التوصيات

```python
# apps/services/analytics-service/src/operations.py

class OperationsAnalytics:
    """تحليلات العمليات"""

    async def get_recommendation_effectiveness(
        self,
        tenant_id: str,
        date_range: DateRange
    ) -> EffectivenessReport:
        """قياس فعالية التوصيات"""

        # Get all recommendations issued
        recommendations = await self.db.get_recommendations(
            tenant_id=tenant_id,
            date_range=date_range
        )

        # Track execution
        executed = [r for r in recommendations if r.status == "executed"]
        ignored = [r for r in recommendations if r.status == "ignored"]

        # Calculate outcomes
        return EffectivenessReport(
            total_recommendations=len(recommendations),
            executed_count=len(executed),
            execution_rate=len(executed) / len(recommendations) * 100,

            # By type
            by_type={
                ActionType.IRRIGATION: self._analyze_type(recommendations, ActionType.IRRIGATION),
                ActionType.FERTILIZATION: self._analyze_type(recommendations, ActionType.FERTILIZATION),
                ActionType.SPRAY: self._analyze_type(recommendations, ActionType.SPRAY)
            },

            # Time to action
            avg_time_to_action_hours=self._calculate_avg_time(executed),

            # Impact correlation
            ndvi_improvement_after_action=self._correlate_ndvi_improvement(executed),

            # Recommendations
            improvement_suggestions=self._suggest_improvements(recommendations)
        )
```

---

## 📈 ROI Matrix

| المورد                   | الجهد    | الأثر        | ROI Score | الأولوية |
| ------------------------ | -------- | ------------ | --------- | -------- |
| Action Template Standard | 🟢 منخفض | 🔴 عالي جدًا | 9/10      | 🥇 1     |
| NATS Notification Spine  | 🟡 متوسط | 🔴 عالي      | 8/10      | 🥈 2     |
| Unified Offline UX       | 🟢 منخفض | 🟡 متوسط     | 7/10      | 🥉 3     |
| Historical Intelligence  | 🟡 متوسط | 🟡 متوسط     | 6/10      | 4        |
| Docs as Guardrails       | 🟢 منخفض | 🟡 متوسط     | 7/10      | 5        |
| Event-Driven Playbooks   | 🔴 عالي  | 🔴 عالي جدًا | 7/10      | 6        |
| Operations Analytics     | 🟡 متوسط | 🟡 متوسط     | 5/10      | 7        |

---

## 📁 الملفات الجديدة المطلوبة

### Phase 1

```
shared/contracts/action_template.py          # Action Template Standard
shared/contracts/action_types.py             # Action Types Enum
packages/shared-ui/src/components/offline/   # Offline Components
apps/services/*/src/events.py                # Event Publishers
```

### Phase 2

```
apps/services/satellite-service/src/historical.py
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/field-first-check.yml
```

### Phase 3

```
shared/playbooks/                            # Playbook Engine
apps/services/analytics-service/             # Operations Analytics
```

---

## ✅ معايير النجاح

### Phase 1 KPIs

- [ ] 100% من خدمات التحليل تُنتج ActionTemplate
- [ ] NATS يحمل 80% من التنبيهات
- [ ] مكونات Offline مستخدمة في Web و Mobile

### Phase 2 KPIs

- [ ] مقارنات موسمية متاحة لكل حقل
- [ ] 100% من PRs تمر بـ Field-First check

### Phase 3 KPIs

- [ ] 3+ Playbooks نشطة
- [ ] تقارير فعالية أسبوعية

---

## الخطوة التالية

ابدأ بـ **Phase 1.1: Action Template Standard** لأنه:

1. أقل جهد
2. أعلى عائد
3. أساس لكل المراحل اللاحقة

---

<p align="center">
  <sub>SAHOOL Asset Investment Plan v1.0.0</sub>
  <br>
  <sub>ديسمبر 2025</sub>
</p>
