/// Unit Tests for AI Service Models and StateNotifier
/// اختبارات وحدات خدمة الذكاء الاصطناعي
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_field_app/core/ai/ai_service.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // AiAdvisory Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('AiAdvisory', () {
    test('fromJson parses all fields correctly', () {
      // Arrange
      final json = {
        'id': 'adv-001',
        'question': 'When to irrigate wheat?',
        'answer': 'Irrigate every 10 days during tillering.',
        'answer_ar': 'اسقِ كل 10 أيام خلال مرحلة التفريع.',
        'confidence': 0.92,
        'sources': ['SAHOOL KB', 'FAO Guide'],
        'type': 'irrigation',
        'created_at': '2025-06-15T10:00:00Z',
      };

      // Act
      final advisory = AiAdvisory.fromJson(json);

      // Assert
      expect(advisory.id, 'adv-001');
      expect(advisory.question, 'When to irrigate wheat?');
      expect(advisory.answer, 'Irrigate every 10 days during tillering.');
      expect(advisory.answerAr, 'اسقِ كل 10 أيام خلال مرحلة التفريع.');
      expect(advisory.confidence, 0.92);
      expect(advisory.sources, ['SAHOOL KB', 'FAO Guide']);
      expect(advisory.type, AdvisoryType.irrigation);
      expect(advisory.createdAt, DateTime.utc(2025, 6, 15, 10, 0, 0));
    });

    test('fromJson uses defaults for missing/null fields', () {
      // Arrange
      final json = <String, dynamic>{};

      // Act
      final advisory = AiAdvisory.fromJson(json);

      // Assert
      expect(advisory.id, '');
      expect(advisory.question, '');
      expect(advisory.answer, '');
      expect(advisory.answerAr, '');
      expect(advisory.confidence, 0.0);
      expect(advisory.sources, isEmpty);
      expect(advisory.type, AdvisoryType.general);
    });

    test('fromJson handles null sources gracefully', () {
      // Arrange
      final json = {
        'id': 'adv-002',
        'question': 'test',
        'answer': 'test',
        'answer_ar': 'test',
        'confidence': 0.5,
        'sources': null,
        'type': 'general',
        'created_at': '2025-01-01T00:00:00Z',
      };

      // Act
      final advisory = AiAdvisory.fromJson(json);

      // Assert
      expect(advisory.sources, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AdvisoryType Enum Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('AdvisoryType', () {
    test('fromString returns correct type for valid values', () {
      expect(AdvisoryType.fromString('irrigation'), AdvisoryType.irrigation);
      expect(AdvisoryType.fromString('fertilizer'), AdvisoryType.fertilizer);
      expect(AdvisoryType.fromString('pest_control'), AdvisoryType.pestControl);
      expect(
          AdvisoryType.fromString('disease_management'),
          AdvisoryType.diseaseManagement);
      expect(
          AdvisoryType.fromString('crop_planning'),
          AdvisoryType.cropPlanning);
      expect(
          AdvisoryType.fromString('weather_advisory'),
          AdvisoryType.weatherAdvisory);
      expect(AdvisoryType.fromString('general'), AdvisoryType.general);
    });

    test('fromString returns general for unknown values', () {
      expect(AdvisoryType.fromString('unknown'), AdvisoryType.general);
      expect(AdvisoryType.fromString(''), AdvisoryType.general);
    });

    test('has correct Arabic labels', () {
      expect(AdvisoryType.irrigation.labelAr, 'الري');
      expect(AdvisoryType.fertilizer.labelAr, 'التسميد');
      expect(AdvisoryType.pestControl.labelAr, 'مكافحة الآفات');
      expect(AdvisoryType.diseaseManagement.labelAr, 'إدارة الأمراض');
      expect(AdvisoryType.cropPlanning.labelAr, 'تخطيط المحاصيل');
      expect(AdvisoryType.weatherAdvisory.labelAr, 'استشارات الطقس');
      expect(AdvisoryType.general.labelAr, 'عام');
    });

    test('has correct value strings', () {
      expect(AdvisoryType.irrigation.value, 'irrigation');
      expect(AdvisoryType.fertilizer.value, 'fertilizer');
      expect(AdvisoryType.pestControl.value, 'pest_control');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ImageAnalysisResult Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('ImageAnalysisResult', () {
    test('fromJson parses correctly with recommendations', () {
      // Arrange
      final json = {
        'detected_class': 'Leaf Rust',
        'detected_class_ar': 'صدأ الأوراق',
        'confidence': 0.87,
        'severity': 'moderate',
        'severity_ar': 'متوسط',
        'recommendations': [
          {
            'title': 'Apply Fungicide',
            'title_ar': 'تطبيق مبيد فطري',
            'description': 'Apply propiconazole within 48 hours',
            'description_ar': 'تطبيق بروبيكونازول خلال 48 ساعة',
            'priority': 'high',
            'action_route': '/treatments/fungicide',
          },
        ],
        'bounding_box': {'x': 10, 'y': 20, 'width': 100, 'height': 80},
      };

      // Act
      final result = ImageAnalysisResult.fromJson(json);

      // Assert
      expect(result.detectedClass, 'Leaf Rust');
      expect(result.detectedClassAr, 'صدأ الأوراق');
      expect(result.confidence, 0.87);
      expect(result.severity, 'moderate');
      expect(result.severityAr, 'متوسط');
      expect(result.recommendations, hasLength(1));
      expect(result.recommendations.first.title, 'Apply Fungicide');
      expect(result.recommendations.first.priority, 'high');
      expect(result.recommendations.first.actionRoute, '/treatments/fungicide');
      expect(result.boundingBox['x'], 10);
    });

    test('fromJson uses defaults for missing fields', () {
      // Arrange
      final json = <String, dynamic>{};

      // Act
      final result = ImageAnalysisResult.fromJson(json);

      // Assert
      expect(result.detectedClass, 'Unknown');
      expect(result.detectedClassAr, 'غير معروف');
      expect(result.confidence, 0.0);
      expect(result.severity, 'unknown');
      expect(result.recommendations, isEmpty);
      expect(result.boundingBox, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AiRecommendation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('AiRecommendation', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'title': 'Apply Fertilizer',
        'title_ar': 'تطبيق السماد',
        'description': 'Apply nitrogen-based fertilizer',
        'description_ar': 'تطبيق سماد نيتروجيني',
        'priority': 'medium',
        'action_route': '/fertilizer/apply',
      };

      // Act
      final rec = AiRecommendation.fromJson(json);

      // Assert
      expect(rec.title, 'Apply Fertilizer');
      expect(rec.titleAr, 'تطبيق السماد');
      expect(rec.description, 'Apply nitrogen-based fertilizer');
      expect(rec.descriptionAr, 'تطبيق سماد نيتروجيني');
      expect(rec.priority, 'medium');
      expect(rec.actionRoute, '/fertilizer/apply');
    });

    test('fromJson handles null action_route', () {
      // Arrange
      final json = {
        'title': 'Test',
        'title_ar': 'اختبار',
        'description': 'Test description',
        'description_ar': 'وصف الاختبار',
        'priority': 'low',
      };

      // Act
      final rec = AiRecommendation.fromJson(json);

      // Assert
      expect(rec.actionRoute, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AiServiceState Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('AiServiceState', () {
    test('default state has correct initial values', () {
      // Arrange & Act
      const state = AiServiceState();

      // Assert
      expect(state.isLoading, false);
      expect(state.isAnalyzing, false);
      expect(state.error, isNull);
      expect(state.chatHistory, isEmpty);
      expect(state.lastAnalysis, isNull);
      expect(state.recentAdvisories, isEmpty);
    });

    test('copyWith preserves unchanged fields', () {
      // Arrange
      const state = AiServiceState();

      // Act
      final newState = state.copyWith(isLoading: true);

      // Assert
      expect(newState.isLoading, true);
      expect(newState.isAnalyzing, false);
      expect(newState.error, isNull);
      expect(newState.chatHistory, isEmpty);
    });

    test('copyWith sets error and clears on next copy', () {
      // Arrange
      const state = AiServiceState();

      // Act
      final errorState = state.copyWith(error: 'Network error');
      final clearedState = errorState.copyWith(error: null);

      // Assert
      expect(errorState.error, 'Network error');
      expect(clearedState.error, isNull);
    });

    test('copyWith updates chat history', () {
      // Arrange
      const state = AiServiceState();
      final messages = [
        AiChatMessage(
          id: '1',
          content: 'Hello',
          isUser: true,
          timestamp: DateTime.now(),
        ),
      ];

      // Act
      final newState = state.copyWith(chatHistory: messages);

      // Assert
      expect(newState.chatHistory, hasLength(1));
      expect(newState.chatHistory.first.content, 'Hello');
      expect(newState.chatHistory.first.isUser, true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AiServiceNotifier Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('AiServiceNotifier', () {
    late AiServiceNotifier notifier;

    setUp(() {
      notifier = AiServiceNotifier();
    });

    test('initial state is default AiServiceState', () {
      expect(notifier.state.isLoading, false);
      expect(notifier.state.isAnalyzing, false);
      expect(notifier.state.chatHistory, isEmpty);
    });

    test('clearChat resets chat history', () {
      // Act
      notifier.clearChat();

      // Assert
      expect(notifier.state.chatHistory, isEmpty);
    });

    test('clearAnalysis sets lastAnalysis to null', () {
      // Act
      notifier.clearAnalysis();

      // Assert
      expect(notifier.state.lastAnalysis, isNull);
    });

    test('askAdvisor adds user message to chat history', () async {
      // Act
      await notifier.askAdvisor(question: 'متى أسقي القمح؟');

      // Assert - after the mock delay, should have 2 messages (user + AI)
      expect(notifier.state.chatHistory.length, 2);
      expect(notifier.state.chatHistory.first.isUser, true);
      expect(notifier.state.chatHistory.first.content, 'متى أسقي القمح؟');
      expect(notifier.state.chatHistory.last.isUser, false);
    });

    test('askAdvisor returns AiAdvisory with correct classification', () async {
      // Act - question with irrigation keywords
      final advisory = await notifier.askAdvisor(question: 'irrigation schedule for wheat');

      // Assert
      expect(advisory, isNotNull);
      expect(advisory!.type, AdvisoryType.irrigation);
      expect(advisory.confidence, 0.85);
      expect(advisory.sources, isNotEmpty);
    });

    test('askAdvisor classifies fertilizer questions correctly', () async {
      // Act
      final advisory = await notifier.askAdvisor(question: 'When to apply سماد?');

      // Assert
      expect(advisory, isNotNull);
      expect(advisory!.type, AdvisoryType.fertilizer);
    });

    test('askAdvisor classifies pest questions correctly', () async {
      // Act
      final advisory = await notifier.askAdvisor(question: 'pest control for locust');

      // Assert
      expect(advisory, isNotNull);
      expect(advisory!.type, AdvisoryType.pestControl);
    });

    test('askAdvisor classifies disease questions correctly', () async {
      // Act
      final advisory = await notifier.askAdvisor(question: 'disease symptoms on wheat صدأ');

      // Assert
      expect(advisory, isNotNull);
      expect(advisory!.type, AdvisoryType.diseaseManagement);
    });

    test('askAdvisor classifies weather questions correctly', () async {
      // Act
      final advisory = await notifier.askAdvisor(question: 'weather forecast this week');

      // Assert
      expect(advisory, isNotNull);
      expect(advisory!.type, AdvisoryType.weatherAdvisory);
    });

    test('askAdvisor defaults to general for unclassified questions', () async {
      // Act
      final advisory = await notifier.askAdvisor(question: 'hello');

      // Assert
      expect(advisory, isNotNull);
      expect(advisory!.type, AdvisoryType.general);
    });

    test('askAdvisor stores recent advisories (max 20)', () async {
      // Act
      await notifier.askAdvisor(question: 'Question 1');
      await notifier.askAdvisor(question: 'Question 2');

      // Assert
      expect(notifier.state.recentAdvisories.length, 2);
      // Most recent should be first
      expect(notifier.state.recentAdvisories.first.question, 'Question 2');
    });

    test('askAdvisor sets isLoading false after completion', () async {
      // Act
      await notifier.askAdvisor(question: 'test');

      // Assert
      expect(notifier.state.isLoading, false);
      expect(notifier.state.error, isNull);
    });

    test('analyzeImage sets isAnalyzing and returns result', () async {
      // Arrange
      final imageBytes = List.filled(100, 0).toList();
      final bytes = Uint8List.fromList(imageBytes);

      // Act
      final result = await notifier.analyzeImage(imageBytes: bytes);

      // Assert
      expect(result, isNotNull);
      expect(result!.detectedClass, 'Leaf Rust');
      expect(result.detectedClassAr, 'صدأ الأوراق');
      expect(result.confidence, 0.87);
      expect(result.severity, 'moderate');
      expect(result.recommendations, hasLength(2));
      expect(notifier.state.isAnalyzing, false);
      expect(notifier.state.lastAnalysis, isNotNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AiChatMessage Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('AiChatMessage', () {
    test('stores properties correctly', () {
      // Arrange & Act
      final now = DateTime.now();
      final message = AiChatMessage(
        id: 'msg-1',
        content: 'Test message',
        isUser: true,
        timestamp: now,
        recommendations: const [],
      );

      // Assert
      expect(message.id, 'msg-1');
      expect(message.content, 'Test message');
      expect(message.isUser, true);
      expect(message.timestamp, now);
      expect(message.recommendations, isEmpty);
    });

    test('defaults recommendations to empty list', () {
      // Arrange & Act
      final message = AiChatMessage(
        id: 'msg-2',
        content: 'Content',
        isUser: false,
        timestamp: DateTime.now(),
      );

      // Assert
      expect(message.recommendations, isEmpty);
    });
  });
}
