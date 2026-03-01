/// Unit Tests for Crop Health Feature Models
/// اختبارات وحدات نماذج صحة المحاصيل
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/crop_health/data/models/diagnosis_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // DiseaseSeverity Enum Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('DiseaseSeverity', () {
    test('has correct values', () {
      expect(DiseaseSeverity.values, hasLength(5));
      expect(DiseaseSeverity.healthy.index, 0);
      expect(DiseaseSeverity.low.index, 1);
      expect(DiseaseSeverity.medium.index, 2);
      expect(DiseaseSeverity.high.index, 3);
      expect(DiseaseSeverity.critical.index, 4);
    });

    test('toString returns correct name', () {
      expect(DiseaseSeverity.healthy.name, 'healthy');
      expect(DiseaseSeverity.critical.name, 'critical');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // TreatmentType Enum Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('TreatmentType', () {
    test('has all expected values', () {
      expect(TreatmentType.values, contains(TreatmentType.fungicide));
      expect(TreatmentType.values, contains(TreatmentType.insecticide));
      expect(TreatmentType.values, contains(TreatmentType.herbicide));
      expect(TreatmentType.values, contains(TreatmentType.fertilizer));
      expect(TreatmentType.values, contains(TreatmentType.irrigation));
      expect(TreatmentType.values, contains(TreatmentType.pruning));
      expect(TreatmentType.values, contains(TreatmentType.none));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Treatment Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('Treatment', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'treatmentType': 'fungicide',
        'productName': 'Propiconazole',
        'productNameAr': 'بروبيكونازول',
        'dosage': '250 ml/ha',
        'dosageAr': '250 مل/هكتار',
        'applicationMethod': 'Foliar spray',
        'applicationMethodAr': 'رش ورقي',
        'frequency': 'Every 14 days',
        'frequencyAr': 'كل 14 يوم',
        'precautions': ['Wear PPE', 'Do not apply in wind'],
        'precautionsAr': ['ارتداء معدات الحماية', 'عدم الرش في الرياح'],
      };

      // Act
      final treatment = Treatment.fromJson(json);

      // Assert
      expect(treatment.treatmentType, 'fungicide');
      expect(treatment.productName, 'Propiconazole');
      expect(treatment.productNameAr, 'بروبيكونازول');
      expect(treatment.dosage, '250 ml/ha');
      expect(treatment.dosageAr, '250 مل/هكتار');
      expect(treatment.applicationMethod, 'Foliar spray');
      expect(treatment.applicationMethodAr, 'رش ورقي');
      expect(treatment.frequency, 'Every 14 days');
      expect(treatment.frequencyAr, 'كل 14 يوم');
      expect(treatment.precautions, hasLength(2));
      expect(treatment.precautionsAr, hasLength(2));
    });

    test('defaults precautions to empty list', () {
      // Arrange
      final json = {
        'treatmentType': 'irrigation',
        'productName': 'Water',
        'productNameAr': 'ماء',
        'dosage': '25mm',
        'dosageAr': '25 مم',
        'applicationMethod': 'Drip',
        'applicationMethodAr': 'تنقيط',
        'frequency': 'Daily',
        'frequencyAr': 'يومي',
      };

      // Act
      final treatment = Treatment.fromJson(json);

      // Assert
      expect(treatment.precautions, isEmpty);
      expect(treatment.precautionsAr, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DiagnosisResult Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('DiagnosisResult', () {
    test('fromJson parses comprehensive diagnosis', () {
      // Arrange
      final json = {
        'diagnosisId': 'DIAG-001',
        'timestamp': '2025-06-15T10:30:00Z',
        'diseaseName': 'Wheat Leaf Rust',
        'diseaseNameAr': 'صدأ أوراق القمح',
        'diseaseDescription': 'Fungal disease affecting wheat leaves',
        'diseaseDescriptionAr': 'مرض فطري يصيب أوراق القمح',
        'confidence': 0.92,
        'severity': 'high',
        'affectedAreaPercent': 35.0,
        'detectedCrop': 'wheat',
        'growthStage': 'heading',
        'treatments': [
          {
            'treatmentType': 'fungicide',
            'productName': 'Tilt',
            'productNameAr': 'تيلت',
            'dosage': '500 ml/ha',
            'dosageAr': '500 مل/هكتار',
            'applicationMethod': 'Spray',
            'applicationMethodAr': 'رش',
            'frequency': 'Once',
            'frequencyAr': 'مرة واحدة',
          },
        ],
        'urgentActionRequired': true,
        'needsExpertReview': false,
        'weatherConsideration': 'Humid conditions favor disease spread',
        'preventionTips': ['Use resistant varieties', 'Crop rotation'],
        'preventionTipsAr': ['استخدام أصناف مقاومة', 'تناوب المحاصيل'],
      };

      // Act
      final result = DiagnosisResult.fromJson(json);

      // Assert
      expect(result.diagnosisId, 'DIAG-001');
      expect(result.timestamp, DateTime.utc(2025, 6, 15, 10, 30, 0));
      expect(result.diseaseName, 'Wheat Leaf Rust');
      expect(result.diseaseNameAr, 'صدأ أوراق القمح');
      expect(result.confidence, 0.92);
      expect(result.severity, 'high');
      expect(result.affectedAreaPercent, 35.0);
      expect(result.detectedCrop, 'wheat');
      expect(result.growthStage, 'heading');
      expect(result.treatments, hasLength(1));
      expect(result.urgentActionRequired, true);
      expect(result.needsExpertReview, false);
      expect(result.weatherConsideration, 'Humid conditions favor disease spread');
      expect(result.preventionTips, hasLength(2));
      expect(result.preventionTipsAr, hasLength(2));
    });

    test('fromJson handles null optional fields', () {
      // Arrange
      final json = {
        'diagnosisId': 'DIAG-002',
        'timestamp': '2025-06-15T10:00:00Z',
        'diseaseName': 'Healthy',
        'diseaseNameAr': 'سليم',
        'diseaseDescription': 'No issues detected',
        'diseaseDescriptionAr': 'لم يتم اكتشاف مشاكل',
        'confidence': 0.95,
        'severity': 'healthy',
        'affectedAreaPercent': 0.0,
        'detectedCrop': 'wheat',
        'treatments': <Map<String, dynamic>>[],
        'urgentActionRequired': false,
        'needsExpertReview': false,
      };

      // Act
      final result = DiagnosisResult.fromJson(json);

      // Assert
      expect(result.growthStage, isNull);
      expect(result.expertReviewReason, isNull);
      expect(result.weatherConsideration, isNull);
      expect(result.preventionTips, isEmpty);
    });

    test('copyWith preserves unchanged fields', () {
      // Arrange
      final result = DiagnosisResult(
        diagnosisId: 'DIAG-003',
        timestamp: DateTime.now(),
        diseaseName: 'Test',
        diseaseNameAr: 'اختبار',
        diseaseDescription: 'Desc',
        diseaseDescriptionAr: 'وصف',
        confidence: 0.5,
        severity: 'medium',
        affectedAreaPercent: 10.0,
        detectedCrop: 'wheat',
        treatments: const [],
        urgentActionRequired: false,
        needsExpertReview: true,
        expertReviewReason: 'Low confidence',
      );

      // Act
      final modified = result.copyWith(urgentActionRequired: true);

      // Assert
      expect(modified.urgentActionRequired, true);
      expect(modified.diagnosisId, 'DIAG-003');
      expect(modified.needsExpertReview, true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropOption Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropOption', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'cropId': 'wheat',
        'name': 'Wheat',
        'nameAr': 'قمح',
        'icon': 'grain',
        'diseasesCount': 12,
      };

      // Act
      final option = CropOption.fromJson(json);

      // Assert
      expect(option.cropId, 'wheat');
      expect(option.name, 'Wheat');
      expect(option.nameAr, 'قمح');
      expect(option.icon, 'grain');
      expect(option.diseasesCount, 12);
    });

    test('defaults diseasesCount to 0', () {
      // Arrange
      final json = {
        'cropId': 'barley',
        'name': 'Barley',
        'nameAr': 'شعير',
        'icon': 'grain',
      };

      // Act
      final option = CropOption.fromJson(json);

      // Assert
      expect(option.diseasesCount, 0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DiseaseInfo Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('DiseaseInfo', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'diseaseId': 'rust-001',
        'name': 'Leaf Rust',
        'nameAr': 'صدأ الأوراق',
        'crop': 'wheat',
        'severity': 'high',
      };

      // Act
      final info = DiseaseInfo.fromJson(json);

      // Assert
      expect(info.diseaseId, 'rust-001');
      expect(info.name, 'Leaf Rust');
      expect(info.nameAr, 'صدأ الأوراق');
      expect(info.crop, 'wheat');
      expect(info.severity, 'high');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ExpertReviewRequest Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('ExpertReviewRequest', () {
    test('fromJson parses with defaults', () {
      // Arrange
      final json = {
        'diagnosisId': 'DIAG-001',
      };

      // Act
      final request = ExpertReviewRequest.fromJson(json);

      // Assert
      expect(request.diagnosisId, 'DIAG-001');
      expect(request.farmerNotes, isNull);
      expect(request.urgency, 'normal');
    });

    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'diagnosisId': 'DIAG-001',
        'farmerNotes': 'Spreading rapidly',
        'urgency': 'high',
      };

      // Act
      final request = ExpertReviewRequest.fromJson(json);

      // Assert
      expect(request.farmerNotes, 'Spreading rapidly');
      expect(request.urgency, 'high');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ExpertReviewResponse Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('ExpertReviewResponse', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'reviewId': 'REV-001',
        'diagnosisId': 'DIAG-001',
        'status': 'pending',
        'estimatedResponseTime': '24 hours',
        'message': 'تم تسجيل طلبك للمراجعة',
        'messageEn': 'Your review request has been registered',
      };

      // Act
      final response = ExpertReviewResponse.fromJson(json);

      // Assert
      expect(response.reviewId, 'REV-001');
      expect(response.diagnosisId, 'DIAG-001');
      expect(response.status, 'pending');
      expect(response.estimatedResponseTime, '24 hours');
      expect(response.message, 'تم تسجيل طلبك للمراجعة');
      expect(response.messageEn, 'Your review request has been registered');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // BatchDiagnosisResult Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('BatchDiagnosisResult', () {
    test('fromJson parses batch result with summary', () {
      // Arrange
      final json = {
        'batchId': 'BATCH-001',
        'fieldId': 'FIELD-001',
        'totalImages': 10,
        'processed': 10,
        'results': [
          {
            'filename': 'image1.jpg',
            'disease': 'Leaf Rust',
            'confidence': 0.89,
            'diseaseNameAr': 'صدأ الأوراق',
          },
          {
            'filename': 'image2.jpg',
            'disease': 'Healthy',
            'confidence': 0.95,
            'diseaseNameAr': 'سليم',
          },
        ],
        'summary': {
          'healthyCount': 7,
          'infectedCount': 3,
          'averageConfidence': 0.88,
        },
      };

      // Act
      final batch = BatchDiagnosisResult.fromJson(json);

      // Assert
      expect(batch.batchId, 'BATCH-001');
      expect(batch.fieldId, 'FIELD-001');
      expect(batch.totalImages, 10);
      expect(batch.processed, 10);
      expect(batch.results, hasLength(2));
      expect(batch.results.first.filename, 'image1.jpg');
      expect(batch.results.first.disease, 'Leaf Rust');
      expect(batch.results.first.confidence, 0.89);
      expect(batch.results.first.diseaseNameAr, 'صدأ الأوراق');
      expect(batch.summary.healthyCount, 7);
      expect(batch.summary.infectedCount, 3);
      expect(batch.summary.averageConfidence, 0.88);
    });

    test('fromJson handles null fieldId', () {
      // Arrange
      final json = {
        'batchId': 'BATCH-002',
        'totalImages': 5,
        'processed': 3,
        'results': <Map<String, dynamic>>[],
        'summary': {
          'healthyCount': 3,
          'infectedCount': 0,
          'averageConfidence': 0.92,
        },
      };

      // Act
      final batch = BatchDiagnosisResult.fromJson(json);

      // Assert
      expect(batch.fieldId, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DiagnosisHistoryItem Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('DiagnosisHistoryItem', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'diagnosisId': 'DIAG-001',
        'diseaseName': 'Leaf Rust',
        'diseaseNameAr': 'صدأ الأوراق',
        'confidence': 0.89,
        'severity': 'high',
        'timestamp': '2025-06-15T10:00:00Z',
        'fieldId': 'FIELD-001',
        'imagePath': '/images/DIAG-001.jpg',
        'isResolved': true,
      };

      // Act
      final item = DiagnosisHistoryItem.fromJson(json);

      // Assert
      expect(item.diagnosisId, 'DIAG-001');
      expect(item.diseaseName, 'Leaf Rust');
      expect(item.diseaseNameAr, 'صدأ الأوراق');
      expect(item.confidence, 0.89);
      expect(item.severity, 'high');
      expect(item.fieldId, 'FIELD-001');
      expect(item.imagePath, '/images/DIAG-001.jpg');
      expect(item.isResolved, true);
    });

    test('defaults isResolved to false', () {
      // Arrange
      final json = {
        'diagnosisId': 'DIAG-002',
        'diseaseName': 'Blight',
        'diseaseNameAr': 'لفحة',
        'confidence': 0.75,
        'severity': 'medium',
        'timestamp': '2025-06-15T10:00:00Z',
      };

      // Act
      final item = DiagnosisHistoryItem.fromJson(json);

      // Assert
      expect(item.isResolved, false);
      expect(item.fieldId, isNull);
      expect(item.imagePath, isNull);
    });
  });
}
