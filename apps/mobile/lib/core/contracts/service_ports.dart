/// SAHOOL Unified Service Ports (auto-generated)
/// DO NOT EDIT - Generated from packages/shared-types/src/contracts/service-ports.ts
/// Run: npx tsx scripts/sync-contracts-to-dart.ts
///
/// Contract version: 4.20.0
library;

/// Single source of truth for all microservice ports.
abstract final class ServicePorts {
  static const int fieldManagement = 3000;
  static const int userService = 3025;
  static const int partnerAuth = 3030;
  static const int marketplace = 3010;
  static const int researchCore = 3015;
  static const int disasterAssessment = 3020;
  static const int vegetationAnalysis = 8090;
  static const int indicators = 8091;
  static const int weather = 8092;
  static const int advisory = 8093;
  static const int irrigationSmart = 8094;
  static const int cropIntelligence = 8095;
  static const int ndviProcessor = 8118;
  static const int virtualSensors = 8119;
  static const int fieldIntelligence = 8120;
  static const int skillsService = 8121;
  static const int laiEstimation = 3022;
  static const int cropGrowthModel = 3023;
  static const int yieldPrediction = 8152;
  static const int yieldEngine = 8098;
  static const int yieldPredictionLegacy = 3021;
  static const int taskService = 8103;
  static const int equipment = 8101;
  static const int notifications = 8110;
  static const int alertService = 8113;
  static const int auditService = 8114;
  static const int billingCore = 8089;
  static const int providerConfig = 8104;
  static const int inventory = 8116;
  static const int wsGateway = 8081;
  static const int chatService = 8115;
  static const int fieldChat = 8099;
  static const int communityChat = 8097;
  static const int iotService = 8117;
  static const int iotGateway = 8106;
  static const int iotSensorHub = 8251;
  static const int copilotApi = 8088;
  static const int aiAdvisor = 8112;
  static const int aiAgentsCore = 8161;
  static const int aiAgentsService = 8130;
  static const int aiChatAssistant = 8260;
  static const int agentRegistry = 8160;
  static const int llmOrchestrator = 8164;
  static const int knowledgeGraph = 8140;
  static const int codeFixAgent = 8162;
  static const int codeReviewService = 8102;
  static const int yoloVision = 8150;
  static const int groundVision = 8182;
  static const int terrainCore = 8185;
  static const int hydrology = 8165;
  static const int levelingOptimizer = 8170;
  static const int edgeOrchestrator = 8180;
  static const int vllmDeepseek = 8270;
  static const int soilAnalysis = 8134;
  static const int pestDetection = 8125;
  static const int droneService = 8126;
  static const int cooperative = 8127;
  static const int globalgap = 8128;
  static const int traceability = 8123;
  static const int crmService = 8131;
  static const int astronomicalCalendar = 8111;
  static const int logistics = 8167;
  static const int supplyChain = 8230;
  static const int lowcodeEngine = 8132;
  static const int community = 8133;
  static const int wechat = 8135;
  static const int whatsappBot = 8240;
  static const int ussdGateway = 8183;
  static const int fertigationEngine = 8252;
  static const int irrigationCycleEngine = 8250;
  static const int digitalTwin = 8253;
  static const int mcpServer = 8201;
  static const int carbonService = 8195;
  static const int admin = 3001;
  static const int web = 3002;
  static const int kongGateway = 8000;
  static const int kongAdmin = 8001;
  static const int nats = 4222;
  static const int natsMonitor = 8222;
  static const int postgres = 5432;
  static const int pgbouncer = 6432;
  static const int redis = 6379;
}

/// Get service URL from port and host.
String getServiceUrl(int port, {String host = 'http://localhost'}) =>
    '$host:$port';
