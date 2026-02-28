/// Crop Health Diagnosis Models Unit Tests
/// اختبارات وحدات نماذج تشخيص صحة المحاصيل
///
/// Tests Freezed model creation, JSON serialization/deserialization,
/// enum values, and model properties.

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/crop_health/data/models/diagnosis_models.dart';

void main() {
  group('DiseaseSeverity enum', () {
    test('should have all expected values', () {
      expect(DiseaseSeverity.values, hasLength(5));
      expect(DiseaseSeverity.values, containsAll([
        DiseaseSeverity.healthy,
        DiseaseSeverity.low,
        DiseaseSeverity.medium,
        DiseaseSeverity.high,
        DiseaseSeverity.critical,
      ]));
    });

    test('should have correct names', () {
      expect(DiseaseSeverity.healthy.name, 'healthy');
      expect(DiseaseSeverity.low.name, 'low');
      expect(DiseaseSeverity.medium.name, 'medium');
      expect(DiseaseSeverity.high.name, 'high');
      expect(DiseaseSeverity.critical.name, 'critical');
    });
  });

  group('TreatmentType enum', () {
    test('should have all expected values', () {
      expect(TreatmentType.values, hasLength(7));
      expect(TreatmentType.values, containsAll([
        TreatmentType.fungicide,
        TreatmentType.insecticide,
        TreatmentType.herbicide,
        TreatmentType.fertilizer,
        TreatmentType.irrigation,
        TreatmentType.pruning,
        TreatmentType.none,
      ]));
    });

    test('should have correct names', () {
      expect(TreatmentType.fungicide.name, 'fungicide');
      expect(TreatmentType.insecticide.name, 'insecticide');
      expect(TreatmentType.herbicide.name, 'herbicide');
      expect(TreatmentType.fertilizer.name, 'fertilizer');
      expect(TreatmentType.irrigation.name, 'irrigation');
      expect(TreatmentType.pruning.name, 'pruning');
      expect(TreatmentType.none.name, 'none');
    });
  });

  group('Treatment model', () {
    late Treatment treatment;

    setUp(() {
      treatment = const Treatment(
        treatmentType: 'fungicide',
        productName: 'Mancozeb 80% WP',
        productNameAr: 'مانكوزيب 80% مسحوق قابل للبلل',
        dosage: '2.5 g/L water',
        dosageAr: '2.5 جم/لتر ماء',
        applicationMethod: 'Foliar spray',
        applicationMethodAr: 'رش ورقي',
        frequency: 'Every 7 days',
        frequencyAr: 'كل 7 أيام',
        precautions: ['Wear protective equipment', 'Avoid windy conditions'],
        precautionsAr: ['ارتداء معدات الحماية', 'تجنب الرياح'],
      );
    });

    test('should create Treatment with all properties', () {
      expect(treatment.treatmentType, 'fungicide');
      expect(treatment.productName, 'Mancozeb 80% WP');
      expect(treatment.productNameAr, 'مانكوزيب 80% مسحوق قابل للبلل');
      expect(treatment.dosage, '2.5 g/L water');
      expect(treatment.dosageAr, '2.5 جم/لتر ماء');
      expect(treatment.applicationMethod, 'Foliar spray');
      expect(treatment.applicationMethodAr, 'رش ورقي');
      expect(treatment.frequency, 'Every 7 days');
      expect(treatment.frequencyAr, 'كل 7 أيام');
      expect(treatment.precautions, hasLength(2));
      expect(treatment.precautionsAr, hasLength(2));
    });

    test('should create Treatment with default empty precautions', () {
      const treatmentNoPrecautions = Treatment(
        treatmentType: 'irrigation',
        productName: 'Water',
        productNameAr: 'ماء',
        dosage: '25 mm',
        dosageAr: '25 ملم',
        applicationMethod: 'Drip',
        applicationMethodAr: 'تنقيط',
        frequency: 'Daily',
        frequencyAr: 'يومياً',
      );

      expect(treatmentNoPrecautions.precautions, isEmpty);
      expect(treatmentNoPrecautions.precautionsAr, isEmpty);
    });

    test('should serialize to JSON and back', () {
      final json = treatment.toJson();

      expect(json['treatmentType'], 'fungicide');
      expect(json['productName'], 'Mancozeb 80% WP');
      expect(json['productNameAr'], 'مانكوزيب 80% مسحوق قابل للبلل');
      expect(json['dosage'], '2.5 g/L water');
      expect(json['precautions'], hasLength(2));

      final restored = Treatment.fromJson(json);
      expect(restored, equals(treatment));
    });

    test('should support copyWith', () {
      final updated = treatment.copyWith(
        dosage: '5.0 g/L water',
        dosageAr: '5.0 جم/لتر ماء',
      );

      expect(updated.dosage, '5.0 g/L water');
      expect(updated.dosageAr, '5.0 جم/لتر ماء');
      expect(updated.productName, treatment.productName);
    });

    test('should have value equality', () {
      const other = Treatment(
        treatmentType: 'fungicide',
        productName: 'Mancozeb 80% WP',
        productNameAr: 'مانكوزيب 80% مسحوق قابل للبلل',
        dosage: '2.5 g/L water',
        dosageAr: '2.5 جم/لتر ماء',
        applicationMethod: 'Foliar spray',
        applicationMethodAr: 'رش ورقي',
        frequency: 'Every 7 days',
        frequencyAr: 'كل 7 أيام',
        precautions: ['Wear protective equipment', 'Avoid windy conditions'],
        precautionsAr: ['ارتداء معدات الحماية', 'تجنب الرياح'],
      );

      expect(treatment, equals(other));
    });
  });

  group('DiagnosisResult model', () {
    late DiagnosisResult diagnosisResult;
    late DateTime timestamp;

    setUp(() {
      timestamp = DateTime(2026, 2, 27, 10, 30, 0);
      diagnosisResult = DiagnosisResult(
        diagnosisId: 'diag_001',
        timestamp: timestamp,
        diseaseName: 'Wheat Leaf Rust',
        diseaseNameAr: 'صدأ أوراق القمح',
        diseaseDescription: 'Fungal disease causing orange-brown pustules on leaves',
        diseaseDescriptionAr: 'مرض فطري يسبب بثرات برتقالية بنية على الأوراق',
        confidence: 0.92,
        severity: 'high',
        affectedAreaPercent: 35.0,
        detectedCrop: 'wheat',
        growthStage: 'tillering',
        treatments: const [
          Treatment(
            treatmentType: 'fungicide',
            productName: 'Propiconazole',
            productNameAr: 'بروبيكونازول',
            dosage: '0.5 L/ha',
            dosageAr: '0.5 لتر/هكتار',
            applicationMethod: 'Foliar spray',
            applicationMethodAr: 'رش ورقي',
            frequency: 'Once at first appearance',
            frequencyAr: 'مرة عند الظهور الأول',
          ),
        ],
        urgentActionRequired: true,
        needsExpertReview: false,
        weatherConsideration: 'Avoid spraying if rain expected within 6 hours',
        preventionTips: ['Use resistant varieties', 'Rotate crops'],
        preventionTipsAr: ['استخدام أصناف مقاومة', 'تدوير المحاصيل'],
      );
    });

    test('should create DiagnosisResult with all required properties', () {
      expect(diagnosisResult.diagnosisId, 'diag_001');
      expect(diagnosisResult.timestamp, timestamp);
      expect(diagnosisResult.diseaseName, 'Wheat Leaf Rust');
      expect(diagnosisResult.diseaseNameAr, 'صدأ أوراق القمح');
      expect(diagnosisResult.confidence, 0.92);
      expect(diagnosisResult.severity, 'high');
      expect(diagnosisResult.affectedAreaPercent, 35.0);
      expect(diagnosisResult.detectedCrop, 'wheat');
      expect(diagnosisResult.growthStage, 'tillering');
      expect(diagnosisResult.treatments, hasLength(1));
      expect(diagnosisResult.urgentActionRequired, isTrue);
      expect(diagnosisResult.needsExpertReview, isFalse);
    });

    test('should create DiagnosisResult with optional fields null', () {
      final minimal = DiagnosisResult(
        diagnosisId: 'diag_002',
        timestamp: timestamp,
        diseaseName: 'Healthy',
        diseaseNameAr: 'سليم',
        diseaseDescription: 'No disease detected',
        diseaseDescriptionAr: 'لم يتم اكتشاف مرض',
        confidence: 0.95,
        severity: 'healthy',
        affectedAreaPercent: 0.0,
        detectedCrop: 'wheat',
        treatments: const [],
        urgentActionRequired: false,
        needsExpertReview: false,
      );

      expect(minimal.growthStage, isNull);
      expect(minimal.expertReviewReason, isNull);
      expect(minimal.weatherConsideration, isNull);
      expect(minimal.preventionTips, isEmpty);
      expect(minimal.preventionTipsAr, isEmpty);
    });

    test('should serialize to JSON and back', () {
      final json = diagnosisResult.toJson();

      expect(json['diagnosisId'], 'diag_001');
      expect(json['diseaseName'], 'Wheat Leaf Rust');
      expect(json['confidence'], 0.92);
      expect(json['severity'], 'high');
      expect(json['affectedAreaPercent'], 35.0);
      expect(json['detectedCrop'], 'wheat');
      expect(json['treatments'], isList);
      expect(json['urgentActionRequired'], isTrue);

      final restored = DiagnosisResult.fromJson(json);
      expect(restored.diagnosisId, diagnosisResult.diagnosisId);
      expect(restored.diseaseName, diagnosisResult.diseaseName);
      expect(restored.confidence, diagnosisResult.confidence);
      expect(restored.severity, diagnosisResult.severity);
      expect(restored.treatments, hasLength(1));
    });

    test('should deserialize from JSON map', () {
      final json = {
        'diagnosisId': 'diag_from_json',
        'timestamp': '2026-02-27T10:30:00.000',
        'diseaseName': 'Powdery Mildew',
        'diseaseNameAr': 'البياض الدقيقي',
        'diseaseDescription': 'White powdery spots on leaves',
        'diseaseDescriptionAr': 'بقع بيضاء دقيقية على الأوراق',
        'confidence': 0.85,
        'severity': 'medium',
        'affectedAreaPercent': 20.0,
        'detectedCrop': 'barley',
        'treatments': <Map<String, dynamic>>[],
        'urgentActionRequired': false,
        'needsExpertReview': true,
        'expertReviewReason': 'Unusual pattern detected',
        'preventionTips': <String>[],
        'preventionTipsAr': <String>[],
      };

      final result = DiagnosisResult.fromJson(json);

      expect(result.diagnosisId, 'diag_from_json');
      expect(result.diseaseName, 'Powdery Mildew');
      expect(result.diseaseNameAr, 'البياض الدقيقي');
      expect(result.confidence, 0.85);
      expect(result.needsExpertReview, isTrue);
      expect(result.expertReviewReason, 'Unusual pattern detected');
    });

    test('should support copyWith', () {
      final updated = diagnosisResult.copyWith(
        severity: 'critical',
        urgentActionRequired: true,
      );

      expect(updated.severity, 'critical');
      expect(updated.urgentActionRequired, isTrue);
      expect(updated.diagnosisId, diagnosisResult.diagnosisId);
      expect(updated.confidence, diagnosisResult.confidence);
    });
  });

  group('CropOption model', () {
    test('should create CropOption with all properties', () {
      const crop = CropOption(
        cropId: 'wheat',
        name: 'Wheat',
        nameAr: 'قمح',
        icon: 'wheat_icon',
        diseasesCount: 12,
      );

      expect(crop.cropId, 'wheat');
      expect(crop.name, 'Wheat');
      expect(crop.nameAr, 'قمح');
      expect(crop.icon, 'wheat_icon');
      expect(crop.diseasesCount, 12);
    });

    test('should have default diseasesCount of 0', () {
      const crop = CropOption(
        cropId: 'barley',
        name: 'Barley',
        nameAr: 'شعير',
        icon: 'barley_icon',
      );

      expect(crop.diseasesCount, 0);
    });

    test('should serialize to JSON and back', () {
      const crop = CropOption(
        cropId: 'date_palm',
        name: 'Date Palm',
        nameAr: 'نخيل',
        icon: 'palm_icon',
        diseasesCount: 8,
      );

      final json = crop.toJson();
      expect(json['cropId'], 'date_palm');
      expect(json['name'], 'Date Palm');
      expect(json['nameAr'], 'نخيل');
      expect(json['diseasesCount'], 8);

      final restored = CropOption.fromJson(json);
      expect(restored, equals(crop));
    });

    test('should have value equality', () {
      const crop1 = CropOption(
        cropId: 'tomato',
        name: 'Tomato',
        nameAr: 'طماطم',
        icon: 'tomato_icon',
        diseasesCount: 10,
      );

      const crop2 = CropOption(
        cropId: 'tomato',
        name: 'Tomato',
        nameAr: 'طماطم',
        icon: 'tomato_icon',
        diseasesCount: 10,
      );

      expect(crop1, equals(crop2));
    });
  });

  group('DiseaseInfo model', () {
    test('should create DiseaseInfo with all properties', () {
      const disease = DiseaseInfo(
        diseaseId: 'leaf_rust',
        name: 'Leaf Rust',
        nameAr: 'صدأ الأوراق',
        crop: 'wheat',
        severity: 'high',
      );

      expect(disease.diseaseId, 'leaf_rust');
      expect(disease.name, 'Leaf Rust');
      expect(disease.nameAr, 'صدأ الأوراق');
      expect(disease.crop, 'wheat');
      expect(disease.severity, 'high');
    });

    test('should serialize to JSON and back', () {
      const disease = DiseaseInfo(
        diseaseId: 'powdery_mildew',
        name: 'Powdery Mildew',
        nameAr: 'البياض الدقيقي',
        crop: 'barley',
        severity: 'medium',
      );

      final json = disease.toJson();
      expect(json['diseaseId'], 'powdery_mildew');
      expect(json['name'], 'Powdery Mildew');
      expect(json['crop'], 'barley');

      final restored = DiseaseInfo.fromJson(json);
      expect(restored, equals(disease));
    });

    test('should have value equality', () {
      const d1 = DiseaseInfo(
        diseaseId: 'blight',
        name: 'Blight',
        nameAr: 'اللفحة',
        crop: 'tomato',
        severity: 'critical',
      );

      const d2 = DiseaseInfo(
        diseaseId: 'blight',
        name: 'Blight',
        nameAr: 'اللفحة',
        crop: 'tomato',
        severity: 'critical',
      );

      expect(d1, equals(d2));
    });
  });

  group('DiagnosisHistoryItem model', () {
    test('should create DiagnosisHistoryItem with all properties', () {
      final now = DateTime.now();
      final item = DiagnosisHistoryItem(
        diagnosisId: 'diag_hist_001',
        diseaseName: 'Aphid Infestation',
        diseaseNameAr: 'إصابة بالمن',
        confidence: 0.88,
        severity: 'medium',
        timestamp: now,
        fieldId: 'field_001',
        imagePath: '/path/to/image.jpg',
        isResolved: false,
      );

      expect(item.diagnosisId, 'diag_hist_001');
      expect(item.diseaseName, 'Aphid Infestation');
      expect(item.diseaseNameAr, 'إصابة بالمن');
      expect(item.confidence, 0.88);
      expect(item.severity, 'medium');
      expect(item.timestamp, now);
      expect(item.fieldId, 'field_001');
      expect(item.imagePath, '/path/to/image.jpg');
      expect(item.isResolved, isFalse);
    });

    test('should have default isResolved as false', () {
      final item = DiagnosisHistoryItem(
        diagnosisId: 'diag_hist_002',
        diseaseName: 'Rust',
        diseaseNameAr: 'صدأ',
        confidence: 0.75,
        severity: 'low',
        timestamp: DateTime.now(),
      );

      expect(item.isResolved, isFalse);
      expect(item.fieldId, isNull);
      expect(item.imagePath, isNull);
    });

    test('should serialize to JSON and back', () {
      final timestamp = DateTime(2026, 2, 27, 14, 0, 0);
      final item = DiagnosisHistoryItem(
        diagnosisId: 'diag_hist_003',
        diseaseName: 'Fusarium Wilt',
        diseaseNameAr: 'ذبول الفيوزاريوم',
        confidence: 0.91,
        severity: 'high',
        timestamp: timestamp,
        fieldId: 'field_003',
        isResolved: true,
      );

      final json = item.toJson();
      expect(json['diagnosisId'], 'diag_hist_003');
      expect(json['diseaseName'], 'Fusarium Wilt');
      expect(json['confidence'], 0.91);
      expect(json['isResolved'], isTrue);

      final restored = DiagnosisHistoryItem.fromJson(json);
      expect(restored.diagnosisId, item.diagnosisId);
      expect(restored.diseaseName, item.diseaseName);
      expect(restored.confidence, item.confidence);
      expect(restored.isResolved, item.isResolved);
    });
  });

  group('BatchDiagnosisResult model', () {
    test('should create BatchDiagnosisResult with multiple results', () {
      const batch = BatchDiagnosisResult(
        batchId: 'batch_001',
        fieldId: 'field_001',
        totalImages: 5,
        processed: 5,
        results: [
          BatchImageResult(
            filename: 'img_001.jpg',
            disease: 'Leaf Rust',
            confidence: 0.92,
            diseaseNameAr: 'صدأ الأوراق',
          ),
          BatchImageResult(
            filename: 'img_002.jpg',
            disease: 'Healthy',
            confidence: 0.95,
            diseaseNameAr: 'سليم',
          ),
          BatchImageResult(
            filename: 'img_003.jpg',
            disease: 'Powdery Mildew',
            confidence: 0.78,
            diseaseNameAr: 'البياض الدقيقي',
          ),
        ],
        summary: BatchSummary(
          healthyCount: 1,
          infectedCount: 2,
          averageConfidence: 0.883,
        ),
      );

      expect(batch.batchId, 'batch_001');
      expect(batch.fieldId, 'field_001');
      expect(batch.totalImages, 5);
      expect(batch.processed, 5);
      expect(batch.results, hasLength(3));
      expect(batch.summary.healthyCount, 1);
      expect(batch.summary.infectedCount, 2);
      expect(batch.summary.averageConfidence, closeTo(0.883, 0.001));
    });

    test('should create BatchDiagnosisResult without fieldId', () {
      const batch = BatchDiagnosisResult(
        batchId: 'batch_002',
        totalImages: 2,
        processed: 2,
        results: [],
        summary: BatchSummary(
          healthyCount: 2,
          infectedCount: 0,
          averageConfidence: 0.96,
        ),
      );

      expect(batch.fieldId, isNull);
      expect(batch.results, isEmpty);
    });

    test('should serialize to JSON and back', () {
      const batch = BatchDiagnosisResult(
        batchId: 'batch_003',
        totalImages: 1,
        processed: 1,
        results: [
          BatchImageResult(
            filename: 'test.jpg',
            disease: 'Blight',
            confidence: 0.80,
            diseaseNameAr: 'اللفحة',
          ),
        ],
        summary: BatchSummary(
          healthyCount: 0,
          infectedCount: 1,
          averageConfidence: 0.80,
        ),
      );

      final json = batch.toJson();
      expect(json['batchId'], 'batch_003');
      expect(json['totalImages'], 1);
      expect(json['results'], isList);

      final restored = BatchDiagnosisResult.fromJson(json);
      expect(restored.batchId, batch.batchId);
      expect(restored.results, hasLength(1));
      expect(restored.summary.infectedCount, 1);
    });
  });

  group('BatchImageResult model', () {
    test('should create with all properties', () {
      const result = BatchImageResult(
        filename: 'photo_20260227.jpg',
        disease: 'Yellow Rust',
        confidence: 0.87,
        diseaseNameAr: 'الصدأ الأصفر',
      );

      expect(result.filename, 'photo_20260227.jpg');
      expect(result.disease, 'Yellow Rust');
      expect(result.confidence, 0.87);
      expect(result.diseaseNameAr, 'الصدأ الأصفر');
    });

    test('should serialize to JSON and back', () {
      const result = BatchImageResult(
        filename: 'scan.jpg',
        disease: 'Healthy',
        confidence: 0.99,
        diseaseNameAr: 'سليم',
      );

      final json = result.toJson();
      final restored = BatchImageResult.fromJson(json);
      expect(restored, equals(result));
    });
  });

  group('BatchSummary model', () {
    test('should create with all properties', () {
      const summary = BatchSummary(
        healthyCount: 3,
        infectedCount: 7,
        averageConfidence: 0.865,
      );

      expect(summary.healthyCount, 3);
      expect(summary.infectedCount, 7);
      expect(summary.averageConfidence, closeTo(0.865, 0.001));
    });

    test('should serialize to JSON and back', () {
      const summary = BatchSummary(
        healthyCount: 0,
        infectedCount: 0,
        averageConfidence: 0.0,
      );

      final json = summary.toJson();
      final restored = BatchSummary.fromJson(json);
      expect(restored, equals(summary));
    });
  });

  group('ExpertReviewRequest model', () {
    test('should create with all properties', () {
      const request = ExpertReviewRequest(
        diagnosisId: 'diag_001',
        farmerNotes: 'The leaves started turning yellow 3 days ago',
        urgency: 'high',
      );

      expect(request.diagnosisId, 'diag_001');
      expect(request.farmerNotes, 'The leaves started turning yellow 3 days ago');
      expect(request.urgency, 'high');
    });

    test('should have default urgency of normal', () {
      const request = ExpertReviewRequest(
        diagnosisId: 'diag_002',
      );

      expect(request.urgency, 'normal');
      expect(request.farmerNotes, isNull);
    });

    test('should serialize to JSON and back', () {
      const request = ExpertReviewRequest(
        diagnosisId: 'diag_003',
        farmerNotes: 'Urgent issue',
        urgency: 'critical',
      );

      final json = request.toJson();
      expect(json['diagnosisId'], 'diag_003');
      expect(json['urgency'], 'critical');

      final restored = ExpertReviewRequest.fromJson(json);
      expect(restored, equals(request));
    });
  });

  group('ExpertReviewResponse model', () {
    test('should create with all properties', () {
      const response = ExpertReviewResponse(
        reviewId: 'review_001',
        diagnosisId: 'diag_001',
        status: 'pending',
        estimatedResponseTime: '24 hours',
        message: 'تم استلام طلب المراجعة بنجاح',
        messageEn: 'Review request received successfully',
      );

      expect(response.reviewId, 'review_001');
      expect(response.diagnosisId, 'diag_001');
      expect(response.status, 'pending');
      expect(response.estimatedResponseTime, '24 hours');
      expect(response.message, 'تم استلام طلب المراجعة بنجاح');
      expect(response.messageEn, 'Review request received successfully');
    });

    test('should serialize to JSON and back', () {
      const response = ExpertReviewResponse(
        reviewId: 'review_002',
        diagnosisId: 'diag_002',
        status: 'in_progress',
        estimatedResponseTime: '12 hours',
        message: 'قيد المراجعة',
        messageEn: 'Under review',
      );

      final json = response.toJson();
      final restored = ExpertReviewResponse.fromJson(json);
      expect(restored, equals(response));
    });
  });
}
