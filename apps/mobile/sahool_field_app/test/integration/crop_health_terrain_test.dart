/// SAHOOL Field App - Crop Health & Terrain Integration Tests
/// اختبارات تكامل صحة المحاصيل والتضاريس
///
/// Tests MockServer with crop health and terrain endpoints:
/// - Crop health zones and diagnosis
/// - NDVI analysis and satellite imagery
/// - Disease detection and severity
/// - Treatment recommendations
/// - Terrain/DEM analysis
/// - Hydrology and drainage
/// - Advisory integration
/// - Outbox integration for offline observations
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';

import '../../../integration_test/helpers/mock_server.dart';
import '../mocks/mock_app_database.dart';

void main() {
  // ===========================================================================
  // Crop Health API Integration
  // تكامل واجهة صحة المحاصيل
  // ===========================================================================

  group('Crop Health API Integration - تكامل واجهة صحة المحاصيل', () {
    late MockHttpClient client;

    setUp(() {
      setupMockServer();
      client = MockHttpClient();

      // Stub crop health zones
      MockServer.instance.stub('/api/v1/crop-health/zones', (request) {
        if (request.method == 'GET') {
          return MockResponse.success({
            'data': [
              {
                'id': 'zone-001',
                'fieldId': 'field-test-001',
                'name': 'المنطقة الشمالية',
                'nameEn': 'North Zone',
                'ndvi': 0.72,
                'healthStatus': 'healthy',
                'healthStatusAr': 'صحي',
                'area': 2.5,
                'cropType': 'wheat',
                'growthStage': 'tillering',
                'lastObservation': '2026-03-13T10:00:00Z',
              },
              {
                'id': 'zone-002',
                'fieldId': 'field-test-001',
                'name': 'المنطقة الجنوبية',
                'nameEn': 'South Zone',
                'ndvi': 0.38,
                'healthStatus': 'stressed',
                'healthStatusAr': 'مجهد',
                'area': 3.0,
                'cropType': 'wheat',
                'growthStage': 'tillering',
                'lastObservation': '2026-03-13T10:00:00Z',
                'alerts': [
                  {
                    'type': 'nitrogen_deficiency',
                    'severity': 'warning',
                    'message': 'نقص النيتروجين المحتمل',
                  },
                ],
              },
            ],
            'total': 2,
            'fieldId': 'field-test-001',
          });
        }
        if (request.method == 'POST') {
          return MockResponse.created({
            'data': {
              'id': 'zone-new-${DateTime.now().millisecondsSinceEpoch}',
              ...?request.body,
              'healthStatus': 'unknown',
              'ndvi': null,
            },
            'message': 'تم إنشاء المنطقة بنجاح',
          });
        }
        return MockResponse.notFound;
      });

      // Diagnosis endpoint
      MockServer.instance.stub('/api/v1/crop-health/diagnose', (request) {
        if (request.method == 'POST') {
          return MockResponse.success({
            'data': {
              'diagnosisId':
                  'diag-${DateTime.now().millisecondsSinceEpoch}',
              'fieldId': request.body?['fieldId'] ?? 'field-test-001',
              'disease': {
                'name': 'صدأ الأوراق',
                'nameEn': 'Leaf Rust',
                'scientificName': 'Puccinia triticina',
                'confidence': 0.87,
                'severity': 'moderate',
                'severityAr': 'متوسطة',
                'affectedArea': 15.0,
              },
              'recommendations': [
                {
                  'type': 'fungicide',
                  'product': 'Propiconazole 25%',
                  'productAr': 'بروبيكونازول 25%',
                  'rate': '0.5 L/ha',
                  'timing': 'Apply within 48 hours',
                  'timingAr': 'الرش خلال 48 ساعة',
                  'priority': 'high',
                },
                {
                  'type': 'monitoring',
                  'description': 'Re-assess in 7 days',
                  'descriptionAr': 'إعادة التقييم بعد 7 أيام',
                  'priority': 'medium',
                },
              ],
              'similarCases': 3,
            },
          });
        }
        return MockResponse.notFound;
      });

      // Observations endpoint
      MockServer.instance.stub('/api/v1/crop-health/observations', (request) {
        if (request.method == 'GET') {
          return MockResponse.success({
            'data': [
              {
                'id': 'obs-001',
                'zoneId': 'zone-001',
                'type': 'visual_inspection',
                'notes': 'اصفرار خفيف في الأوراق السفلية',
                'severity': 'low',
                'images': ['img-001.jpg'],
                'observedAt': '2026-03-12T08:30:00Z',
                'observer': 'أحمد',
              },
              {
                'id': 'obs-002',
                'zoneId': 'zone-002',
                'type': 'sensor_reading',
                'notes': 'رطوبة التربة منخفضة',
                'severity': 'medium',
                'observedAt': '2026-03-13T07:00:00Z',
              },
            ],
            'total': 2,
          });
        }
        if (request.method == 'POST') {
          return MockResponse.created({
            'data': {
              'id': 'obs-new-${DateTime.now().millisecondsSinceEpoch}',
              ...?request.body,
              'createdAt': DateTime.now().toIso8601String(),
            },
            'message': 'تم تسجيل الملاحظة بنجاح',
          });
        }
        return MockResponse.notFound;
      });

      // Timeline endpoint
      MockServer.instance.stub('/api/v1/crop-health/zones/zone-001/timeline',
          (request) {
        return MockResponse.success({
          'data': {
            'zoneId': 'zone-001',
            'entries': List.generate(30, (i) {
              final date = DateTime.now().subtract(Duration(days: 29 - i));
              return {
                'date': date.toIso8601String(),
                'ndvi': 0.55 + (i * 0.006), // Gradual improvement
                'healthStatus':
                    i > 20 ? 'healthy' : (i > 10 ? 'moderate' : 'stressed'),
                'events': i == 15
                    ? [
                        {
                          'type': 'treatment',
                          'description': 'تطبيق سماد يوريا',
                        }
                      ]
                    : [],
              };
            }),
          },
        });
      });

      // NDVI endpoint
      MockServer.instance.stub('/api/v1/ndvi/field-test-001', (request) {
        return MockResponse.success({
          'data': {
            'fieldId': 'field-test-001',
            'meanNdvi': 0.65,
            'minNdvi': 0.32,
            'maxNdvi': 0.82,
            'healthStatus': 'moderate',
            'healthStatusAr': 'معتدل',
            'imageDate': '2026-03-12',
            'source': 'Sentinel-2',
            'cloudCoverage': 5.2,
            'zones': [
              {'name': 'North', 'ndvi': 0.72, 'status': 'healthy'},
              {'name': 'South', 'ndvi': 0.38, 'status': 'stressed'},
            ],
          },
        });
      });

      // Terrain analysis endpoint
      MockServer.instance.stub('/api/v1/terrain/analyze', (request) {
        if (request.method == 'POST') {
          return MockResponse.success({
            'data': {
              'fieldId': request.body?['fieldId'] ?? 'field-test-001',
              'elevation': {
                'min': 1250.0,
                'max': 1285.0,
                'mean': 1267.5,
                'range': 35.0,
                'unit': 'meters',
              },
              'slope': {
                'mean': 3.2,
                'max': 8.7,
                'classification': 'gentle',
                'classificationAr': 'منحدر خفيف',
              },
              'aspect': {
                'dominant': 'SE',
                'dominantAr': 'جنوب شرقي',
                'degrees': 135,
              },
              'drainage': {
                'classification': 'well_drained',
                'classificationAr': 'جيد الصرف',
                'flowDirection': 'SE',
                'accumulation': 'low',
              },
              'suitability': {
                'irrigation': 'suitable',
                'irrigationAr': 'مناسب للري',
                'mechanization': 'suitable',
                'score': 85,
              },
              'processedAt': DateTime.now().toIso8601String(),
            },
          });
        }
        return MockResponse.notFound;
      });

      // Hydrology endpoint
      MockServer.instance.stub('/api/v1/hydrology/drainage', (request) {
        if (request.method == 'POST') {
          return MockResponse.success({
            'data': {
              'fieldId': request.body?['fieldId'] ?? 'field-test-001',
              'watershedArea': 12.5,
              'drainageChannels': [
                {
                  'id': 'ch-001',
                  'length': 120.0,
                  'depth': 0.8,
                  'type': 'natural',
                },
                {
                  'id': 'ch-002',
                  'length': 85.0,
                  'depth': 0.5,
                  'type': 'constructed',
                },
              ],
              'floodRisk': 'low',
              'floodRiskAr': 'منخفض',
              'recommendations': [
                {
                  'type': 'drainage_improvement',
                  'description': 'تحسين قناة الصرف الشرقية',
                  'priority': 'medium',
                },
              ],
            },
          });
        }
        return MockResponse.notFound;
      });

      // Advisory endpoint
      MockServer.instance.stub('/api/v1/advisory', (request) {
        if (request.method == 'POST') {
          return MockResponse.success({
            'data': {
              'advisoryId':
                  'adv-${DateTime.now().millisecondsSinceEpoch}',
              'type': request.body?['type'] ?? 'general',
              'recommendation': 'Based on current soil moisture (38%) and '
                  'weather forecast, irrigate within 24 hours.',
              'recommendationAr': 'بناءً على رطوبة التربة الحالية (38%) وتوقعات '
                  'الطقس، يُنصح بالري خلال 24 ساعة.',
              'confidence': 0.85,
              'priority': 'high',
              'factors': [
                {'name': 'Soil Moisture', 'nameAr': 'رطوبة التربة', 'value': 38},
                {'name': 'Temperature', 'nameAr': 'درجة الحرارة', 'value': 28.5},
                {'name': 'Crop Stage', 'nameAr': 'مرحلة النمو', 'value': 'tillering'},
              ],
              'actions': [
                {
                  'step': 1,
                  'description': 'Apply 25mm irrigation early morning',
                  'descriptionAr': 'تطبيق 25 ملم ري في الصباح الباكر',
                },
                {
                  'step': 2,
                  'description': 'Monitor soil moisture after 24 hours',
                  'descriptionAr': 'مراقبة رطوبة التربة بعد 24 ساعة',
                },
              ],
            },
          });
        }
        return MockResponse.notFound;
      });
    });

    tearDown(() {
      resetMockServer();
    });

    // -------------------------------------------------------------------------
    // Crop Health Zones
    // -------------------------------------------------------------------------

    test('GET /crop-health/zones returns zones with health status', () async {
      final response = await client.get('/api/v1/crop-health/zones');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['data'].length, equals(2));

      final healthyZone = response.body['data'][0];
      expect(healthyZone['ndvi'], equals(0.72));
      expect(healthyZone['healthStatus'], equals('healthy'));
      expect(healthyZone['healthStatusAr'], equals('صحي'));

      final stressedZone = response.body['data'][1];
      expect(stressedZone['ndvi'], equals(0.38));
      expect(stressedZone['healthStatus'], equals('stressed'));
      expect(stressedZone['alerts'], isList);
      expect(stressedZone['alerts'].length, equals(1));
      expect(stressedZone['alerts'][0]['type'], equals('nitrogen_deficiency'));
    });

    test('POST /crop-health/zones creates new zone', () async {
      final response = await client.post(
        '/api/v1/crop-health/zones',
        body: {
          'fieldId': 'field-test-001',
          'name': 'المنطقة الغربية',
          'area': 1.5,
        },
      );

      expect(response.statusCode, equals(201));
      expect(response.body['data']['name'], equals('المنطقة الغربية'));
      expect(response.body['data']['healthStatus'], equals('unknown'));
    });

    // -------------------------------------------------------------------------
    // Disease Diagnosis
    // -------------------------------------------------------------------------

    test('POST /crop-health/diagnose returns diagnosis with recommendations',
        () async {
      final response = await client.post(
        '/api/v1/crop-health/diagnose',
        body: {
          'fieldId': 'field-test-001',
          'zoneId': 'zone-002',
          'symptoms': ['leaf_yellowing', 'rust_spots'],
          'cropType': 'wheat',
        },
      );

      expect(response.statusCode, equals(200));
      final diagnosis = response.body['data'];

      // Disease identification
      expect(diagnosis['disease']['name'], equals('صدأ الأوراق'));
      expect(diagnosis['disease']['nameEn'], equals('Leaf Rust'));
      expect(diagnosis['disease']['confidence'], greaterThan(0.8));
      expect(diagnosis['disease']['severity'], equals('moderate'));
      expect(diagnosis['disease']['affectedArea'], equals(15.0));

      // Recommendations
      expect(diagnosis['recommendations'], isList);
      expect(diagnosis['recommendations'].length, greaterThan(0));

      final firstRec = diagnosis['recommendations'][0];
      expect(firstRec['type'], equals('fungicide'));
      expect(firstRec['product'], isNotNull);
      expect(firstRec['priority'], equals('high'));
    });

    // -------------------------------------------------------------------------
    // Observations
    // -------------------------------------------------------------------------

    test('GET /crop-health/observations returns observation history', () async {
      final response = await client.get('/api/v1/crop-health/observations');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['data'].length, equals(2));

      final obs = response.body['data'][0];
      expect(obs['type'], equals('visual_inspection'));
      expect(obs['severity'], isNotNull);
    });

    test('POST /crop-health/observations records new observation', () async {
      final response = await client.post(
        '/api/v1/crop-health/observations',
        body: {
          'zoneId': 'zone-002',
          'type': 'visual_inspection',
          'notes': 'بقع صدأ على الأوراق العلوية',
          'severity': 'high',
        },
      );

      expect(response.statusCode, equals(201));
      expect(response.body['message'], contains('بنجاح'));
    });

    // -------------------------------------------------------------------------
    // Zone Timeline
    // -------------------------------------------------------------------------

    test('GET /crop-health/zones/:id/timeline returns historical data',
        () async {
      final response =
          await client.get('/api/v1/crop-health/zones/zone-001/timeline');

      expect(response.statusCode, equals(200));
      final entries = response.body['data']['entries'] as List;
      expect(entries.length, equals(30));

      // NDVI should show improvement trend
      final firstNdvi = entries.first['ndvi'] as double;
      final lastNdvi = entries.last['ndvi'] as double;
      expect(lastNdvi, greaterThan(firstNdvi));

      // Check treatment event exists
      final treatmentEntries = entries.where(
        (e) => (e['events'] as List).isNotEmpty,
      );
      expect(treatmentEntries.length, equals(1));
    });

    // -------------------------------------------------------------------------
    // NDVI Analysis
    // -------------------------------------------------------------------------

    test('GET /ndvi/:fieldId returns NDVI analysis', () async {
      final response = await client.get('/api/v1/ndvi/field-test-001');

      expect(response.statusCode, equals(200));
      final data = response.body['data'];
      expect(data['meanNdvi'], equals(0.65));
      expect(data['minNdvi'], equals(0.32));
      expect(data['maxNdvi'], equals(0.82));
      expect(data['source'], equals('Sentinel-2'));
      expect(data['cloudCoverage'], lessThan(10));

      // Zone breakdown
      expect(data['zones'], isList);
      expect(data['zones'].length, equals(2));
    });

    // -------------------------------------------------------------------------
    // Terrain Analysis
    // -------------------------------------------------------------------------

    test('POST /terrain/analyze returns terrain analysis', () async {
      final response = await client.post(
        '/api/v1/terrain/analyze',
        body: {'fieldId': 'field-test-001'},
      );

      expect(response.statusCode, equals(200));
      final data = response.body['data'];

      // Elevation
      expect(data['elevation']['min'], isA<num>());
      expect(data['elevation']['max'], isA<num>());
      expect(data['elevation']['range'], equals(35.0));

      // Slope
      expect(data['slope']['mean'], equals(3.2));
      expect(data['slope']['classification'], equals('gentle'));
      expect(data['slope']['classificationAr'], equals('منحدر خفيف'));

      // Aspect
      expect(data['aspect']['dominant'], equals('SE'));
      expect(data['aspect']['degrees'], equals(135));

      // Drainage
      expect(data['drainage']['classification'], equals('well_drained'));

      // Suitability
      expect(data['suitability']['score'], equals(85));
      expect(data['suitability']['irrigation'], equals('suitable'));
    });

    // -------------------------------------------------------------------------
    // Hydrology
    // -------------------------------------------------------------------------

    test('POST /hydrology/drainage returns drainage analysis', () async {
      final response = await client.post(
        '/api/v1/hydrology/drainage',
        body: {'fieldId': 'field-test-001'},
      );

      expect(response.statusCode, equals(200));
      final data = response.body['data'];
      expect(data['watershedArea'], equals(12.5));
      expect(data['drainageChannels'], isList);
      expect(data['drainageChannels'].length, equals(2));
      expect(data['floodRisk'], equals('low'));
      expect(data['floodRiskAr'], equals('منخفض'));
      expect(data['recommendations'], isList);
    });

    // -------------------------------------------------------------------------
    // Advisory
    // -------------------------------------------------------------------------

    test('POST /advisory returns bilingual recommendation', () async {
      final response = await client.post(
        '/api/v1/advisory',
        body: {
          'fieldId': 'field-test-001',
          'type': 'irrigation',
          'context': {
            'soilMoisture': 38,
            'temperature': 28.5,
            'cropStage': 'tillering',
          },
        },
      );

      expect(response.statusCode, equals(200));
      final data = response.body['data'];

      expect(data['recommendation'], isNotNull);
      expect(data['recommendationAr'], isNotNull);
      expect(data['confidence'], greaterThan(0.8));
      expect(data['priority'], equals('high'));

      // Contributing factors
      expect(data['factors'], isList);
      expect(data['factors'].length, greaterThan(0));

      // Action steps
      expect(data['actions'], isList);
      expect(data['actions'].length, equals(2));
      expect(data['actions'][0]['step'], equals(1));
      expect(data['actions'][0]['descriptionAr'], isNotNull);
    });
  });

  // ===========================================================================
  // Crop Health Offline Outbox Integration
  // تكامل صندوق صادر صحة المحاصيل بدون اتصال
  // ===========================================================================

  group('Crop Health Offline Outbox - صندوق صادر صحة المحاصيل', () {
    late MockAppDatabase db;

    setUp(() {
      db = MockAppDatabase();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
    });

    test('observation recorded offline is queued', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'observation',
        entityId: 'obs-offline-001',
        apiEndpoint: '/api/v1/crop-health/observations',
        method: 'POST',
        payload: jsonEncode({
          'zoneId': 'zone-002',
          'type': 'visual_inspection',
          'notes': 'بقع صفراء على أوراق القمح',
          'severity': 'medium',
          'images': ['captured-photo-001.jpg'],
          'location': {'lat': 15.3694, 'lng': 44.1910},
        }),
      );

      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(1));
      expect(pending.first.entityType, equals('observation'));

      final payload = jsonDecode(pending.first.payload) as Map<String, dynamic>;
      expect(payload['notes'], contains('بقع صفراء'));
      expect(payload['images'], isList);
    });

    test('multiple observations queued across zones', () async {
      final zones = ['zone-001', 'zone-002'];

      for (final zoneId in zones) {
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'observation',
          entityId: 'obs-$zoneId',
          apiEndpoint: '/api/v1/crop-health/observations',
          method: 'POST',
          payload: jsonEncode({
            'zoneId': zoneId,
            'type': 'sensor_reading',
            'notes': 'قراءة المستشعر في $zoneId',
          }),
        );
      }

      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(2));
      expect(
        pending.every((o) => o.entityType == 'observation'),
        isTrue,
      );
    });

    test('diagnosis request queued offline with image data', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'diagnosis',
        entityId: 'diag-offline-001',
        apiEndpoint: '/api/v1/crop-health/diagnose',
        method: 'POST',
        payload: jsonEncode({
          'fieldId': 'field-test-001',
          'zoneId': 'zone-002',
          'symptoms': ['leaf_yellowing', 'wilting'],
          'cropType': 'wheat',
          'imageRef': 'local-img-001.jpg',
        }),
      );

      final pending = await db.getPendingOutbox();
      expect(pending.first.entityType, equals('diagnosis'));

      final payload = jsonDecode(pending.first.payload) as Map<String, dynamic>;
      expect(payload['symptoms'], isList);
      expect(payload['symptoms'], contains('leaf_yellowing'));
    });

    test('sync event generated for conflict on observation update', () async {
      // Simulate: observation was modified locally and on server
      await db.addSyncEvent(
        tenantId: 'tenant-001',
        type: 'conflict',
        entityType: 'observation',
        entityId: 'obs-001',
        message: 'تعارض في تحديث الملاحظة - استخدام نسخة الخادم',
      );

      final events = await db.getUnreadSyncEvents('tenant-001');
      expect(events.length, equals(1));
      expect(events.first.type, equals('conflict'));
      expect(events.first.entityType, equals('observation'));
      expect(events.first.message, contains('تعارض'));
    });

    test('treatment action queued offline', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'treatment_action',
        entityId: 'action-offline-001',
        apiEndpoint: '/api/v1/crop-health/actions/complete',
        method: 'POST',
        payload: jsonEncode({
          'diagnosisId': 'diag-001',
          'actionType': 'fungicide_application',
          'product': 'Propiconazole 25%',
          'rate': '0.5 L/ha',
          'appliedAt': DateTime.now().toIso8601String(),
          'appliedBy': 'أحمد',
          'notes': 'تم الرش في الصباح الباكر',
        }),
      );

      final pending = await db.getPendingOutbox();
      expect(pending.first.entityType, equals('treatment_action'));

      final payload = jsonDecode(pending.first.payload) as Map<String, dynamic>;
      expect(payload['product'], equals('Propiconazole 25%'));
      expect(payload['appliedBy'], equals('أحمد'));
    });
  });

  // ===========================================================================
  // Full Diagnostic Flow Integration
  // تكامل سير العمل التشخيصي الكامل
  // ===========================================================================

  group('Full Diagnostic Flow - سير العمل التشخيصي', () {
    late MockHttpClient client;

    setUp(() {
      setupMockServer();
      client = MockHttpClient();

      // Reuse stubs from above
      MockServer.instance.stub('/api/v1/crop-health/zones', (request) {
        return MockResponse.success({
          'data': [
            {
              'id': 'zone-002',
              'healthStatus': 'stressed',
              'ndvi': 0.38,
            },
          ],
          'total': 1,
        });
      });

      MockServer.instance.stub('/api/v1/crop-health/diagnose', (request) {
        return MockResponse.success({
          'data': {
            'diagnosisId': 'diag-flow-001',
            'disease': {
              'nameEn': 'Leaf Rust',
              'confidence': 0.87,
              'severity': 'moderate',
            },
            'recommendations': [
              {
                'type': 'fungicide',
                'product': 'Propiconazole',
                'priority': 'high',
              },
            ],
          },
        });
      });

      MockServer.instance.stub('/api/v1/crop-health/observations', (request) {
        return MockResponse.created({
          'data': {
            'id': 'obs-flow-001',
            ...?request.body,
          },
        });
      });

      MockServer.instance.stub('/api/v1/advisory', (request) {
        return MockResponse.success({
          'data': {
            'recommendation': 'Apply fungicide treatment',
            'recommendationAr': 'تطبيق مبيد فطري',
            'priority': 'high',
          },
        });
      });
    });

    tearDown(() {
      resetMockServer();
    });

    test('complete diagnostic workflow: observe → diagnose → advise',
        () async {
      // Step 1: Check zones for stressed areas
      final zonesResp = await client.get('/api/v1/crop-health/zones');
      expect(zonesResp.statusCode, equals(200));
      final stressedZones = (zonesResp.body['data'] as List)
          .where((z) => z['healthStatus'] == 'stressed')
          .toList();
      expect(stressedZones.length, greaterThan(0));

      // Step 2: Record observation
      final obsResp = await client.post(
        '/api/v1/crop-health/observations',
        body: {
          'zoneId': stressedZones.first['id'],
          'type': 'visual_inspection',
          'notes': 'بقع صدأ على الأوراق',
          'severity': 'medium',
        },
      );
      expect(obsResp.statusCode, equals(201));

      // Step 3: Request diagnosis
      final diagResp = await client.post(
        '/api/v1/crop-health/diagnose',
        body: {
          'fieldId': 'field-test-001',
          'zoneId': stressedZones.first['id'],
          'symptoms': ['rust_spots', 'leaf_yellowing'],
          'cropType': 'wheat',
        },
      );
      expect(diagResp.statusCode, equals(200));
      expect(diagResp.body['data']['disease']['confidence'], greaterThan(0.8));

      // Step 4: Get advisory based on diagnosis
      final advResp = await client.post(
        '/api/v1/advisory',
        body: {
          'type': 'treatment',
          'diagnosisId': diagResp.body['data']['diagnosisId'],
        },
      );
      expect(advResp.statusCode, equals(200));
      expect(advResp.body['data']['priority'], equals('high'));

      // Verify request sequence
      final log = getMockRequestLog();
      expect(log.length, equals(4));
      expect(log[0].path, contains('/crop-health/zones'));
      expect(log[1].path, contains('/crop-health/observations'));
      expect(log[2].path, contains('/crop-health/diagnose'));
      expect(log[3].path, contains('/advisory'));
    });
  });
}
