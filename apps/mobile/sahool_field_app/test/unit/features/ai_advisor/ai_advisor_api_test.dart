import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';
import 'package:sahool_field_app/features/ai_advisor/data/remote/ai_advisor_api.dart';

import '../../../mocks/mock_kong_gateway.dart';

void main() {
  late MockKongGatewayClient mockGateway;
  late AiAdvisorApi api;

  setUpAll(() {
    registerFallbackValue(FakeKongService());
  });

  setUp(() {
    mockGateway = MockKongGatewayClient();
    api = AiAdvisorApi(gateway: mockGateway);
  });

  group('AiAdvisorApi', () {
    group('ask', () {
      test('should return advisor response on success', () async {
        // Arrange
        final responseData = {
          'answer': 'You should irrigate every 10-14 days during tillering',
          'answer_ar': 'يُنصح بالري كل 10-14 يوم في مرحلة التفريع',
          'confidence': 0.92,
          'sources': ['wheat_guide_v2', 'irrigation_manual'],
          'session_id': 'session-001',
        };

        when(() => mockGateway.post<Map<String, dynamic>>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson(responseData));
        });

        // Act
        final result = await api.ask(question: 'متى أسقي القمح؟');

        // Assert
        expect(result.answer, contains('irrigate'));
        expect(result.answerAr, contains('الري'));
        expect(result.confidence, 0.92);
        expect(result.sources.length, 2);
        expect(result.sessionId, 'session-001');
      });

      test('should include optional parameters', () async {
        // Arrange
        when(() => mockGateway.post<Map<String, dynamic>>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson({
            'answer': 'Response',
            'confidence': 0.8,
          }));
        });

        // Act
        await api.ask(
          question: 'ما حالة القمح؟',
          fieldId: 'field-001',
          language: 'ar',
          sessionId: 'session-prev',
        );

        // Assert - verify copilot endpoint was called with messages format
        verify(() => mockGateway.post<Map<String, dynamic>>(
              KongServices.copilot,
              '/chat',
              data: {
                'messages': [
                  {'role': 'user', 'content': 'ما حالة القمح؟'}
                ],
                'context': {
                  'field_id': 'field-001',
                  'language': 'ar',
                },
                'session_id': 'session-prev',
              },
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should throw AiAdvisorException on failure with no fallback',
          () async {
        // Arrange - both copilot and advisory fail
        when(() => mockGateway.post<Map<String, dynamic>>(
                  any(),
                  any(),
                  data: any(named: 'data'),
                  queryParams: any(named: 'queryParams'),
                  fromJson: any(named: 'fromJson'),
                  cancelToken: any(named: 'cancelToken'),
                ))
            .thenAnswer((_) async => errorResponse<Map<String, dynamic>>(
                'ERR_503', 'Service unavailable'));

        // Act & Assert
        expect(
          () => api.ask(question: 'test'),
          throwsA(isA<AiAdvisorException>()),
        );
      });
    });

    group('searchKnowledge', () {
      test('should return RAG search results', () async {
        // Arrange
        final searchData = [
          {
            'content': 'Wheat irrigation guide for tillering stage',
            'score': 0.95,
            'source': 'wheat_guide',
            'category': 'irrigation',
          },
          {
            'content': 'Water management best practices',
            'score': 0.82,
            'source': 'water_manual',
          },
        ];

        when(() => mockGateway.get<List<dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as List<dynamic> Function(dynamic);
          return ApiResponse.success(fromJson(searchData));
        });

        // Act
        final results = await api.searchKnowledge(query: 'wheat irrigation');

        // Assert
        expect(results.length, 2);
        expect(results[0].content, contains('Wheat'));
        expect(results[0].score, 0.95);
        expect(results[0].source, 'wheat_guide');
        expect(results[0].category, 'irrigation');
      });

      test('should return empty list on failure', () async {
        // Arrange
        when(() => mockGateway.get<List<dynamic>>(
                  any(),
                  any(),
                  queryParams: any(named: 'queryParams'),
                  fromJson: any(named: 'fromJson'),
                  cancelToken: any(named: 'cancelToken'),
                ))
            .thenAnswer((_) async =>
                errorResponse<List<dynamic>>('ERR_500', 'Server error'));

        // Act
        final results = await api.searchKnowledge(query: 'test');

        // Assert
        expect(results, isEmpty);
      });
    });

    group('getRecommendations', () {
      test('should return recommendations for field', () async {
        // Arrange
        final recData = {
          'recommendations': [
            {
              'type': 'irrigation',
              'title': 'Irrigate Field',
              'title_ar': 'ري الحقل',
              'description': 'Apply 25mm of water',
              'description_ar': 'تطبيق 25 ملم من الماء',
              'priority': 'high',
            },
          ],
          'field_status': {'health_score': 75},
        };

        when(() => mockGateway.post<Map<String, dynamic>>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as Map<String, dynamic> Function(dynamic);
          return ApiResponse.success(fromJson(recData));
        });

        // Act
        final result = await api.getRecommendations(
          fieldId: 'field-001',
          focus: 'irrigation',
        );

        // Assert
        expect(result.recommendations.length, 1);
        expect(result.recommendations[0].type, 'irrigation');
        expect(result.recommendations[0].titleAr, 'ري الحقل');
        expect(result.recommendations[0].priority, 'high');
      });
    });

    group('getChatHistory', () {
      test('should return chat messages', () async {
        // Arrange
        final historyData = [
          {
            'id': 'msg-001',
            'role': 'user',
            'content': 'متى أسقي القمح؟',
            'timestamp': '2026-02-16T10:00:00Z',
          },
          {
            'id': 'msg-002',
            'role': 'assistant',
            'content': 'يُنصح بالري كل 10-14 يوم',
            'timestamp': '2026-02-16T10:00:05Z',
          },
        ];

        when(() => mockGateway.get<List<dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as List<dynamic> Function(dynamic);
          return ApiResponse.success(fromJson(historyData));
        });

        // Act
        final messages = await api.getChatHistory(sessionId: 'session-001');

        // Assert
        expect(messages.length, 2);
        expect(messages[0].role, 'user');
        expect(messages[1].role, 'assistant');
      });

      test('should return empty list on failure', () async {
        // Arrange
        when(() => mockGateway.get<List<dynamic>>(
                  any(),
                  any(),
                  queryParams: any(named: 'queryParams'),
                  fromJson: any(named: 'fromJson'),
                  cancelToken: any(named: 'cancelToken'),
                ))
            .thenAnswer((_) async =>
                errorResponse<List<dynamic>>('ERR_500', 'Server error'));

        // Act
        final messages = await api.getChatHistory();

        // Assert
        expect(messages, isEmpty);
      });
    });

    group('getAvailableTools', () {
      test('should return copilot tools', () async {
        // Arrange
        final toolsData = [
          {
            'name': 'analyze_field',
            'description': 'Analyze field health and status',
            'parameters': {'field_id': 'string'},
          },
          {
            'name': 'get_weather',
            'description': 'Get weather forecast',
          },
        ];

        when(() => mockGateway.get<List<dynamic>>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as List<dynamic> Function(dynamic);
          return ApiResponse.success(fromJson(toolsData));
        });

        // Act
        final tools = await api.getAvailableTools();

        // Assert
        expect(tools.length, 2);
        expect(tools[0].name, 'analyze_field');
        expect(tools[0].parameters, isNotNull);
        expect(tools[1].parameters, isNull);
      });
    });
  });

  group('AdvisorResponse', () {
    test('should parse complete response', () {
      final json = {
        'answer': 'English answer',
        'answer_ar': 'إجابة عربية',
        'confidence': 0.95,
        'sources': ['source1', 'source2'],
        'metadata': {'model': 'claude'},
        'session_id': 'sess-001',
      };

      final response = AdvisorResponse.fromJson(json);

      expect(response.answer, 'English answer');
      expect(response.answerAr, 'إجابة عربية');
      expect(response.confidence, 0.95);
      expect(response.sources.length, 2);
      expect(response.sessionId, 'sess-001');
    });

    test('should handle missing fields with defaults', () {
      final response = AdvisorResponse.fromJson(<String, dynamic>{});

      expect(response.answer, '');
      expect(response.answerAr, isNull);
      expect(response.confidence, 0.8);
      expect(response.sources, isEmpty);
    });
  });

  group('AiAdvisorException', () {
    test('should create exception with code and message', () {
      const exception = AiAdvisorException(
        code: 'LLM_TIMEOUT',
        message: 'LLM response timeout',
      );

      expect(exception.code, 'LLM_TIMEOUT');
      expect(exception.message, 'LLM response timeout');
      expect(exception.toString(), contains('LLM_TIMEOUT'));
    });
  });
}
