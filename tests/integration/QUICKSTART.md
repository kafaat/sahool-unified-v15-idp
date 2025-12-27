# Quick Start Guide - Integration Tests
# دليل البداية السريعة - اختبارات التكامل

## 🚀 Getting Started in 5 Minutes / البدء في 5 دقائق

### Step 1: Start Test Environment / الخطوة 1: تشغيل بيئة الاختبار

```bash
# Navigate to project root
cd /home/user/sahool-unified-v15-idp

# Start all test services
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready (30-60 seconds)
echo "Waiting for services to start..."
sleep 30
```

### Step 2: Verify Services are Running / الخطوة 2: التحقق من تشغيل الخدمات

```bash
# Check service health
docker-compose -f docker-compose.test.yml ps

# Test PostgreSQL
docker-compose -f docker-compose.test.yml exec postgres_test pg_isready -U sahool_test

# Test Redis
docker-compose -f docker-compose.test.yml exec redis_test redis-cli -a test_redis_pass ping

# Test NATS
curl http://localhost:8223/healthz
```

### Step 3: Run Tests / الخطوة 3: تشغيل الاختبارات

```bash
# Install test dependencies (if not already installed)
pip install -r tests/integration/requirements-test.txt

# Run all integration tests
pytest tests/integration/ -v

# Or run specific test files
pytest tests/integration/test_alert_workflow.py -v
pytest tests/integration/test_iot_workflow.py -v
pytest tests/integration/test_marketplace_workflow.py -v
pytest tests/integration/test_user_journey.py -v
```

### Step 4: View Results / الخطوة 4: عرض النتائج

```bash
# Tests will show output like:
# ✅ PASSED tests/integration/test_alert_workflow.py::test_weather_alert_creation_workflow
# ✅ PASSED tests/integration/test_iot_workflow.py::test_iot_device_registration_workflow
# ❌ FAILED tests/integration/test_marketplace_workflow.py::test_marketplace_order_placement_workflow

# View detailed HTML report (if generated)
open test-results/report.html
```

### Step 5: Cleanup / الخطوة 5: التنظيف

```bash
# Stop and remove test containers
docker-compose -f docker-compose.test.yml down

# Remove volumes (clean database)
docker-compose -f docker-compose.test.yml down -v
```

---

## 📋 Common Test Commands / أوامر الاختبار الشائعة

### Run Specific Test Categories / تشغيل فئات محددة

```bash
# Run only fast tests (skip slow ones)
pytest tests/integration/ -m "not slow" -v

# Run only API tests
pytest tests/integration/ -m api -v

# Run only workflow tests
pytest tests/integration/test_*_workflow.py -v
```

### Run with Coverage / التشغيل مع التغطية

```bash
# Generate coverage report
pytest tests/integration/ \
  --cov=apps/services \
  --cov-report=html \
  --cov-report=term \
  -v

# View coverage report
open htmlcov/index.html
```

### Debug Mode / وضع التصحيح

```bash
# Run with verbose output and keep containers
pytest tests/integration/ -vv --log-cli-level=DEBUG

# Run single test with debugging
pytest tests/integration/test_alert_workflow.py::test_weather_alert_creation_workflow -vv -s
```

---

## 🎯 Testing Specific Workflows / اختبار سير عمل محدد

### Alert System / نظام التنبيهات

```bash
pytest tests/integration/test_alert_workflow.py -v
```

**Tests**: Weather alerts, pest alerts, IoT alerts, alert management

### IoT Integration / تكامل إنترنت الأشياء

```bash
pytest tests/integration/test_iot_workflow.py -v
```

**Tests**: Device management, sensor data, automation, analytics

### Marketplace / السوق

```bash
pytest tests/integration/test_marketplace_workflow.py -v
```

**Tests**: Products, orders, payments, reviews, seller operations

### User Journeys / رحلات المستخدم

```bash
pytest tests/integration/test_user_journey.py -v
```

**Tests**: Onboarding, daily ops, crisis management, seasonal planning, business growth

---

## 🔧 Troubleshooting / استكشاف الأخطاء

### Problem: Services not starting / المشكلة: الخدمات لا تبدأ

```bash
# Check logs
docker-compose -f docker-compose.test.yml logs

# Restart specific service
docker-compose -f docker-compose.test.yml restart postgres_test
```

### Problem: Port already in use / المشكلة: المنفذ مستخدم بالفعل

```bash
# Check what's using the port
lsof -i :5433
lsof -i :6380

# Kill the process or change port in docker-compose.test.yml
```

### Problem: Database connection errors / المشكلة: أخطاء اتصال قاعدة البيانات

```bash
# Wait longer for PostgreSQL
sleep 60

# Check PostgreSQL logs
docker-compose -f docker-compose.test.yml logs postgres_test

# Restart PostgreSQL
docker-compose -f docker-compose.test.yml restart postgres_test
```

### Problem: Tests timeout / المشكلة: انتهاء مهلة الاختبارات

```bash
# Increase timeout in pytest.ini or run with:
pytest tests/integration/ --timeout=300 -v
```

---

## 📊 Test Results / نتائج الاختبارات

### Expected Results / النتائج المتوقعة

```
tests/integration/test_alert_workflow.py::test_weather_alert_creation_workflow ✅ PASSED
tests/integration/test_alert_workflow.py::test_frost_alert_workflow ✅ PASSED
tests/integration/test_iot_workflow.py::test_iot_device_registration_workflow ✅ PASSED
tests/integration/test_marketplace_workflow.py::test_marketplace_product_listing_workflow ✅ PASSED
tests/integration/test_user_journey.py::test_new_farmer_onboarding_journey ✅ PASSED

========================= X passed in Y seconds =========================
```

### Understanding Results / فهم النتائج

- **✅ PASSED** - Test succeeded / نجح الاختبار
- **❌ FAILED** - Test failed, check error details / فشل الاختبار
- **⚠️ SKIPPED** - Test skipped (e.g., service not available) / تم تخطي الاختبار
- **⏱️ SLOW** - Test took longer than expected / استغرق وقتاً أطول

---

## 🎓 Learning Path / مسار التعلم

### For New Developers / للمطورين الجدد

1. **Read** `README_TESTS.md` - Understand test structure
2. **Run** a simple test - Start with `test_health.py`
3. **Review** test fixtures in `conftest.py`
4. **Study** a workflow test - Read `test_alert_workflow.py`
5. **Write** your first test - Add a new test case

### For Experienced Developers / للمطورين ذوي الخبرة

1. **Review** `TEST_COVERAGE_SUMMARY.md` - See what's covered
2. **Identify** gaps in coverage
3. **Add** new test workflows
4. **Optimize** slow tests
5. **Contribute** to documentation

---

## 📚 Documentation / التوثيق

- **README_TESTS.md** - Complete testing guide
- **TEST_COVERAGE_SUMMARY.md** - Coverage summary
- **QUICKSTART.md** - This file!
- **conftest.py** - Test fixtures and utilities

---

## 🆘 Getting Help / الحصول على المساعدة

### Check Documentation First / تحقق من التوثيق أولاً

```bash
# View README
cat tests/integration/README_TESTS.md

# View coverage summary
cat tests/integration/TEST_COVERAGE_SUMMARY.md
```

### Ask for Help / اطلب المساعدة

1. **Search** existing issues in the repository
2. **Check** test examples in workflow files
3. **Contact** the platform team
4. **Create** a detailed issue with error logs

---

## ✅ Checklist Before Committing / قائمة التحقق قبل الالتزام

- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Test documentation updated
- [ ] No hardcoded credentials
- [ ] Proper test isolation (no shared state)
- [ ] Arabic documentation added
- [ ] Code follows existing patterns

---

## 🚢 CI/CD Integration / تكامل CI/CD

Tests run automatically on:
- Every push to main/development branches
- Every pull request
- Scheduled nightly runs

Check GitHub Actions for results.

---

**Happy Testing! / اختبار سعيد!** 🎉

For questions: Contact SAHOOL Platform Team
