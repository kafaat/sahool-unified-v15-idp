/// Service Ports Unit Tests - اختبارات منافذ الخدمات
///
/// Tests that service port definitions are correct, within valid range,
/// and have no duplicate values.
///
/// Run with: flutter test test/core/contracts/service_ports_test.dart
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/core/contracts/service_ports.dart';

void main() {
  // ===========================================================================
  // Port value correctness
  // ===========================================================================

  group('ServicePorts - defined values', () {
    test('core application ports are correct', () {
      expect(ServicePorts.fieldManagement, 3000);
      expect(ServicePorts.admin, 3001);
      expect(ServicePorts.web, 3002);
      expect(ServicePorts.userService, 3025);
      expect(ServicePorts.marketplace, 3010);
    });

    test('analytics and intelligence ports are correct', () {
      expect(ServicePorts.vegetationAnalysis, 8090);
      expect(ServicePorts.indicators, 8091);
      expect(ServicePorts.weather, 8092);
      expect(ServicePorts.advisory, 8093);
      expect(ServicePorts.irrigationSmart, 8094);
      expect(ServicePorts.cropIntelligence, 8095);
    });

    test('infrastructure ports are correct', () {
      expect(ServicePorts.kongGateway, 8000);
      expect(ServicePorts.kongAdmin, 8001);
      expect(ServicePorts.nats, 4222);
      expect(ServicePorts.natsMonitor, 8222);
      expect(ServicePorts.postgres, 5432);
      expect(ServicePorts.pgbouncer, 6432);
      expect(ServicePorts.redis, 6379);
    });

    test('vision and terrain ports are correct', () {
      expect(ServicePorts.yoloVision, 8150);
      expect(ServicePorts.groundVision, 8182);
      expect(ServicePorts.terrainCore, 8185);
      expect(ServicePorts.hydrology, 8165);
      expect(ServicePorts.levelingOptimizer, 8170);
      expect(ServicePorts.edgeOrchestrator, 8180);
    });

    test('AI service ports are correct', () {
      expect(ServicePorts.copilotApi, 8088);
      expect(ServicePorts.aiAdvisor, 8112);
      expect(ServicePorts.aiAgentsCore, 8161);
      expect(ServicePorts.llmOrchestrator, 8164);
      expect(ServicePorts.knowledgeGraph, 8140);
      expect(ServicePorts.vllmDeepseek, 8270);
    });

    test('IoT service ports are correct', () {
      expect(ServicePorts.iotService, 8117);
      expect(ServicePorts.iotGateway, 8106);
      expect(ServicePorts.iotSensorHub, 8251);
    });

    test('communication service ports are correct', () {
      expect(ServicePorts.wsGateway, 8081);
      expect(ServicePorts.chatService, 8115);
      expect(ServicePorts.notifications, 8110);
      expect(ServicePorts.whatsappBot, 8240);
      expect(ServicePorts.ussdGateway, 8183);
    });
  });

  // ===========================================================================
  // Port range validation
  // ===========================================================================

  group('ServicePorts - valid range', () {
    /// All known ports collected for batch validation.
    final allPorts = <String, int>{
      'fieldManagement': ServicePorts.fieldManagement,
      'userService': ServicePorts.userService,
      'marketplace': ServicePorts.marketplace,
      'researchCore': ServicePorts.researchCore,
      'disasterAssessment': ServicePorts.disasterAssessment,
      'vegetationAnalysis': ServicePorts.vegetationAnalysis,
      'indicators': ServicePorts.indicators,
      'weather': ServicePorts.weather,
      'advisory': ServicePorts.advisory,
      'irrigationSmart': ServicePorts.irrigationSmart,
      'cropIntelligence': ServicePorts.cropIntelligence,
      'ndviProcessor': ServicePorts.ndviProcessor,
      'virtualSensors': ServicePorts.virtualSensors,
      'fieldIntelligence': ServicePorts.fieldIntelligence,
      'skillsService': ServicePorts.skillsService,
      'laiEstimation': ServicePorts.laiEstimation,
      'cropGrowthModel': ServicePorts.cropGrowthModel,
      'yieldPrediction': ServicePorts.yieldPrediction,
      'yieldEngine': ServicePorts.yieldEngine,
      'yieldPredictionLegacy': ServicePorts.yieldPredictionLegacy,
      'taskService': ServicePorts.taskService,
      'equipment': ServicePorts.equipment,
      'notifications': ServicePorts.notifications,
      'alertService': ServicePorts.alertService,
      'auditService': ServicePorts.auditService,
      'billingCore': ServicePorts.billingCore,
      'providerConfig': ServicePorts.providerConfig,
      'inventory': ServicePorts.inventory,
      'wsGateway': ServicePorts.wsGateway,
      'chatService': ServicePorts.chatService,
      'fieldChat': ServicePorts.fieldChat,
      'communityChat': ServicePorts.communityChat,
      'iotService': ServicePorts.iotService,
      'iotGateway': ServicePorts.iotGateway,
      'iotSensorHub': ServicePorts.iotSensorHub,
      'copilotApi': ServicePorts.copilotApi,
      'aiAdvisor': ServicePorts.aiAdvisor,
      'aiAgentsCore': ServicePorts.aiAgentsCore,
      'aiAgentsService': ServicePorts.aiAgentsService,
      'aiChatAssistant': ServicePorts.aiChatAssistant,
      'agentRegistry': ServicePorts.agentRegistry,
      'llmOrchestrator': ServicePorts.llmOrchestrator,
      'knowledgeGraph': ServicePorts.knowledgeGraph,
      'codeFixAgent': ServicePorts.codeFixAgent,
      'codeReviewService': ServicePorts.codeReviewService,
      'yoloVision': ServicePorts.yoloVision,
      'groundVision': ServicePorts.groundVision,
      'terrainCore': ServicePorts.terrainCore,
      'hydrology': ServicePorts.hydrology,
      'levelingOptimizer': ServicePorts.levelingOptimizer,
      'edgeOrchestrator': ServicePorts.edgeOrchestrator,
      'vllmDeepseek': ServicePorts.vllmDeepseek,
      'soilAnalysis': ServicePorts.soilAnalysis,
      'pestDetection': ServicePorts.pestDetection,
      'droneService': ServicePorts.droneService,
      'cooperative': ServicePorts.cooperative,
      'globalgap': ServicePorts.globalgap,
      'traceability': ServicePorts.traceability,
      'crmService': ServicePorts.crmService,
      'astronomicalCalendar': ServicePorts.astronomicalCalendar,
      'logistics': ServicePorts.logistics,
      'supplyChain': ServicePorts.supplyChain,
      'lowcodeEngine': ServicePorts.lowcodeEngine,
      'community': ServicePorts.community,
      'wechat': ServicePorts.wechat,
      'whatsappBot': ServicePorts.whatsappBot,
      'ussdGateway': ServicePorts.ussdGateway,
      'fertigationEngine': ServicePorts.fertigationEngine,
      'irrigationCycleEngine': ServicePorts.irrigationCycleEngine,
      'digitalTwin': ServicePorts.digitalTwin,
      'mcpServer': ServicePorts.mcpServer,
      'admin': ServicePorts.admin,
      'web': ServicePorts.web,
      'kongGateway': ServicePorts.kongGateway,
      'kongAdmin': ServicePorts.kongAdmin,
      'nats': ServicePorts.nats,
      'natsMonitor': ServicePorts.natsMonitor,
      'postgres': ServicePorts.postgres,
      'pgbouncer': ServicePorts.pgbouncer,
      'redis': ServicePorts.redis,
    };

    test('all ports are within valid TCP port range (1-65535)', () {
      for (final entry in allPorts.entries) {
        expect(
          entry.value,
          allOf(greaterThan(0), lessThanOrEqualTo(65535)),
          reason: '${entry.key} port ${entry.value} is outside valid range',
        );
      }
    });

    test('all ports are above 1023 (non-privileged)', () {
      for (final entry in allPorts.entries) {
        expect(
          entry.value,
          greaterThan(1023),
          reason: '${entry.key} port ${entry.value} is a privileged port',
        );
      }
    });

    test('no duplicate ports exist', () {
      final seen = <int, String>{};
      for (final entry in allPorts.entries) {
        if (seen.containsKey(entry.value)) {
          fail(
            'Duplicate port ${entry.value}: '
            '${seen[entry.value]} and ${entry.key}',
          );
        }
        seen[entry.value] = entry.key;
      }
    });
  });

  // ===========================================================================
  // getServiceUrl helper
  // ===========================================================================

  group('getServiceUrl', () {
    test('returns correct URL with default host', () {
      expect(
        getServiceUrl(ServicePorts.fieldManagement),
        'http://localhost:3000',
      );
    });

    test('returns correct URL with custom host', () {
      expect(
        getServiceUrl(ServicePorts.userService, host: 'https://api.sahool.app'),
        'https://api.sahool.app:3025',
      );
    });

    test('works with infrastructure ports', () {
      expect(getServiceUrl(ServicePorts.redis), 'http://localhost:6379');
      expect(getServiceUrl(ServicePorts.postgres), 'http://localhost:5432');
    });
  });
}
