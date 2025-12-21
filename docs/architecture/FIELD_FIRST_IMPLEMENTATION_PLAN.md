# 🚀 خطة تنفيذ ميثاق Field-First
## SAHOOL Platform v15.5

---

## 📋 نظرة عامة

هذه الخطة تحول ميثاق "Field-First, Analysis-Serves-Field" إلى إجراءات تنفيذية محددة.

**المبدأ الأساسي:**
> المنصة ميدانية، والتحليل يخدم الميدان.

---

## 🎯 الأهداف

| الهدف | المقياس | الهدف |
|-------|---------|-------|
| Offline Reliability | نسبة نجاح العمليات offline | > 95% |
| Field Response Time | وقت تنفيذ المهمة | < 2 ثانية |
| Sync Success Rate | نسبة نجاح المزامنة | > 99% |
| Analysis to Task Conversion | تحويل التحليل لمهام | 100% |

---

## 📅 المراحل التنفيذية

### المرحلة 1: التأسيس المعماري
**المدة:** أسبوع واحد

#### 1.1 إنشاء ملف المبادئ المعمارية

```markdown
# إنشاء: docs/architecture/PRINCIPLES.md
```

**المحتوى:**
- القواعد الذهبية الثلاث
- تصنيف الخدمات
- معايير قبول الميزات

#### 1.2 تحديث docker-compose.yml

```yaml
# إضافة labels للتصنيف
services:
  field-service:
    labels:
      - "sahool.layer=field-critical"
      - "sahool.priority=1"
      - "sahool.offline=required"

  indicators-service:
    labels:
      - "sahool.layer=bridge"
      - "sahool.priority=2"
      - "sahool.offline=optional"

  crop-health-ai:
    labels:
      - "sahool.layer=analysis"
      - "sahool.priority=3"
      - "sahool.offline=not-required"
```

#### 1.3 إنشاء Service Registry

```yaml
# إنشاء: config/service-registry.yaml
services:
  field-critical:
    - name: field-service
      port: 8080
      offline: required
      fallback: local-cache

    - name: billing-core
      port: 8089
      offline: capability-based
      fallback: last-known-state

    - name: astronomical-calendar
      port: 8111
      offline: required
      fallback: local-calculation

  bridge:
    - name: indicators-service
      port: 8091
      transforms: [ndvi → risk-score, weather → irrigation-advice]

    - name: notification-service
      port: 8110
      channels: [push, sms, in-app]

  analysis:
    - name: satellite-service
      port: 8090
      async: true
      cache-ttl: 24h
```

---

### المرحلة 2: Bridge Layer
**المدة:** أسبوعان

#### 2.1 تحديث indicators-service كـ Bridge رئيسي

```python
# apps/services/indicators-service/src/bridge.py

class AnalysisBridge:
    """
    تحويل مخرجات التحليل إلى إجراءات قابلة للتنفيذ
    """

    async def transform_ndvi_to_action(
        self,
        ndvi_result: NDVIResult,
        field_id: str
    ) -> FieldAction:
        """
        NDVI → Risk Assessment → Recommended Action → Task
        """
        risk = self._calculate_risk(ndvi_result)

        if risk.level == "high":
            return FieldAction(
                type="urgent_inspection",
                title="فحص عاجل مطلوب",
                description=f"انخفاض NDVI بنسبة {risk.drop_percent}%",
                deadline=datetime.now() + timedelta(hours=48),
                offline_executable=True
            )

        return FieldAction(
            type="routine_check",
            title="فحص روتيني",
            offline_executable=True
        )

    async def transform_weather_to_irrigation(
        self,
        forecast: WeatherForecast,
        field_id: str
    ) -> IrrigationAdvice:
        """
        Weather Forecast → ET0 Calculation → Irrigation Schedule
        """
        et0 = self._calculate_et0(forecast)

        return IrrigationAdvice(
            action="irrigate" if et0 > threshold else "skip",
            amount_mm=et0 * crop_coefficient,
            timing="صباحاً" if forecast.temp_max > 35 else "أي وقت",
            offline_executable=True
        )
```

#### 2.2 Action Templates

```python
# apps/services/shared/action_templates.py

class ActionTemplate:
    """
    قوالب الإجراءات الميدانية
    """

    TEMPLATES = {
        "water_stress": {
            "title_ar": "إجهاد مائي محتمل",
            "title_en": "Potential Water Stress",
            "action": "ري خلال 48 ساعة",
            "priority": "high",
            "offline_data": ["last_irrigation", "soil_moisture"],
            "proof_required": ["photo", "meter_reading"]
        },

        "pest_detection": {
            "title_ar": "اشتباه آفة",
            "title_en": "Suspected Pest",
            "action": "فحص ومعالجة",
            "priority": "urgent",
            "offline_data": ["pest_history", "treatment_options"],
            "proof_required": ["photo", "notes"]
        },

        "harvest_ready": {
            "title_ar": "جاهز للحصاد",
            "title_en": "Ready for Harvest",
            "action": "بدء الحصاد",
            "priority": "normal",
            "offline_data": ["yield_estimate", "market_prices"],
            "proof_required": ["weight", "photo"]
        }
    }
```

#### 2.3 Event Pipeline

```python
# apps/services/indicators-service/src/pipeline.py

class AnalysisPipeline:
    """
    Analysis → Bridge → Field Pipeline
    """

    async def process(self, event: AnalysisEvent):
        """
        معالجة حدث تحليلي وتحويله لمهمة ميدانية
        """
        # 1. Normalize
        normalized = self.normalize(event)

        # 2. Enrich with context
        enriched = await self.enrich(normalized)

        # 3. Apply business rules
        action = self.apply_rules(enriched)

        # 4. Create field task
        task = self.create_task(action)

        # 5. Publish for mobile sync
        await self.publish_task(task)

        # 6. Send notification
        await self.notify(task)
```

---

### المرحلة 3: Mobile Enhancements
**المدة:** أسبوع واحد

#### 3.1 Analysis Cache Layer

```dart
// apps/mobile/lib/core/cache/analysis_cache.dart

class AnalysisCache {
  final AppDatabase _db;

  /// Cache analysis result with TTL
  Future<void> cacheAnalysis({
    required String fieldId,
    required String analysisType,
    required Map<String, dynamic> result,
    Duration ttl = const Duration(hours: 24),
  }) async {
    await _db.analysisCache.insert(
      AnalysisCacheEntry(
        fieldId: fieldId,
        type: analysisType,
        data: jsonEncode(result),
        cachedAt: DateTime.now(),
        expiresAt: DateTime.now().add(ttl),
      ),
    );
  }

  /// Get cached analysis (returns null if expired)
  Future<CachedAnalysis?> getAnalysis({
    required String fieldId,
    required String analysisType,
  }) async {
    final entry = await _db.analysisCache.getLatest(fieldId, analysisType);

    if (entry == null) return null;

    final isExpired = DateTime.now().isAfter(entry.expiresAt);

    return CachedAnalysis(
      data: jsonDecode(entry.data),
      cachedAt: entry.cachedAt,
      isStale: isExpired,
    );
  }
}
```

#### 3.2 Fallback UI Components

```dart
// apps/mobile/lib/shared/widgets/offline_aware.dart

class OfflineAwareWidget extends StatelessWidget {
  final Widget child;
  final Widget offlineChild;
  final DateTime? lastUpdated;

  @override
  Widget build(BuildContext context) {
    return Consumer(
      builder: (context, ref, _) {
        final isOnline = ref.watch(networkStatusProvider);
        final hasData = lastUpdated != null;

        if (!isOnline && !hasData) {
          return offlineChild;
        }

        return Column(
          children: [
            if (!isOnline && hasData)
              StaleDataBanner(
                lastUpdated: lastUpdated!,
                message: 'البيانات قديمة - ستُحدّث عند الاتصال',
              ),
            child,
          ],
        );
      },
    );
  }
}

class StaleDataBanner extends StatelessWidget {
  final DateTime lastUpdated;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.orange.shade100,
      padding: EdgeInsets.all(8),
      child: Row(
        children: [
          Icon(Icons.cloud_off, size: 16),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              '$message (${_formatAge(lastUpdated)})',
              style: TextStyle(fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }

  String _formatAge(DateTime dt) {
    final diff = DateTime.now().difference(dt);
    if (diff.inHours < 1) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inDays < 1) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }
}
```

#### 3.3 تحديث الشاشات الرئيسية

```dart
// apps/mobile/lib/features/field/ui/field_detail_screen.dart

class FieldDetailScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final field = ref.watch(fieldProvider(fieldId));
    final analysis = ref.watch(cachedAnalysisProvider(fieldId));

    return Scaffold(
      body: OfflineAwareWidget(
        lastUpdated: analysis?.cachedAt,
        offlineChild: FieldOfflinePlaceholder(),
        child: Column(
          children: [
            // Field info (always available offline)
            FieldInfoCard(field: field),

            // Analysis with stale indicator
            AnalysisCard(
              analysis: analysis,
              isStale: analysis?.isStale ?? false,
            ),

            // Actions (always executable offline)
            ActionButtons(fieldId: fieldId),
          ],
        ),
      ),
    );
  }
}
```

---

### المرحلة 4: Testing & Validation
**المدة:** أسبوع واحد

#### 4.1 Offline Scenarios Test

```dart
// test/integration/offline_scenarios_test.dart

void main() {
  group('Offline Scenarios', () {
    test('Task creation works offline', () async {
      // Simulate offline
      await networkController.goOffline();

      // Create task
      final task = await taskService.create(testTask);

      // Verify in outbox
      expect(task.syncStatus, SyncStatus.pending);
      expect(await outbox.count(), 1);
    });

    test('Analysis shows stale data offline', () async {
      // Cache analysis
      await analysisCache.cache(testAnalysis);

      // Go offline
      await networkController.goOffline();

      // Verify stale indicator
      final cached = await analysisCache.get(fieldId);
      expect(cached.isStale, false); // Not stale yet

      // Advance time
      await clock.advance(Duration(hours: 25));

      final stale = await analysisCache.get(fieldId);
      expect(stale.isStale, true);
    });

    test('Sync resumes on reconnect', () async {
      // Create offline tasks
      await networkController.goOffline();
      await taskService.create(task1);
      await taskService.create(task2);

      // Reconnect
      await networkController.goOnline();

      // Wait for sync
      await syncEngine.waitForComplete();

      // Verify synced
      expect(await outbox.count(), 0);
    });
  });
}
```

#### 4.2 Field Testing Checklist

```markdown
## قائمة اختبار ميداني

### سيناريو 1: لا يوجد اتصال
- [ ] فتح التطبيق
- [ ] عرض الحقول المحفوظة
- [ ] إنشاء مهمة جديدة
- [ ] التقاط صورة
- [ ] حفظ ملاحظات
- [ ] التحقق من Outbox

### سيناريو 2: اتصال متقطع
- [ ] بدء sync
- [ ] قطع الاتصال منتصف العملية
- [ ] التحقق من عدم فقدان البيانات
- [ ] إعادة الاتصال
- [ ] التحقق من استكمال sync

### سيناريو 3: بيانات تحليلية قديمة
- [ ] عرض NDVI محفوظ
- [ ] التحقق من مؤشر "قديم"
- [ ] تنفيذ مهمة بناءً على بيانات قديمة
- [ ] تحديث عند الاتصال
```

---

## 📊 مؤشرات النجاح

| المؤشر | الهدف | طريقة القياس |
|--------|-------|--------------|
| Offline Task Success | > 95% | `tasks_created_offline / total_offline_tasks` |
| Sync Failure Rate | < 1% | `failed_syncs / total_syncs` |
| Stale Data Usage | < 5% | `decisions_on_stale / total_decisions` |
| Field Response Time | < 2s | `avg(task_creation_time)` |
| User Satisfaction | > 4.5/5 | Field surveys |

---

## 🔧 متطلبات تقنية

### Backend
- [ ] Bridge endpoints في indicators-service
- [ ] Action Templates في shared
- [ ] Event pipeline للتحويل

### Mobile
- [ ] Analysis Cache
- [ ] Offline-aware widgets
- [ ] Stale data indicators

### Infrastructure
- [ ] Service labels في docker-compose
- [ ] Priority-based restart policies
- [ ] Monitoring للـ offline metrics

---

## ⚠️ المخاطر والتخفيف

| المخاطر | الاحتمال | التأثير | التخفيف |
|---------|----------|---------|---------|
| تعقيد Bridge Layer | متوسط | متوسط | بدء بسيط وتوسيع تدريجي |
| زيادة حجم التخزين المحلي | منخفض | منخفض | TTL + cleanup |
| تعارض البيانات | منخفض | متوسط | Conflict resolution موجود |

---

## ✅ الخطوات التالية

1. **الآن:** اعتماد الميثاق رسمياً
2. **هذا الأسبوع:** إنشاء ملفات التوثيق
3. **الأسبوع القادم:** بدء Bridge Layer
4. **خلال شهر:** اكتمال التنفيذ

---

<p align="center">
  <strong>خطة تنفيذ Field-First</strong>
  <br>
  <sub>SAHOOL Platform - December 2025</sub>
</p>
