// ═══════════════════════════════════════════════════════════════════════════════
// Web Data Collector Controller - مراقب جمع البيانات من الويب
// REST API for agricultural web data aggregation (Browserbase MCP inspired)
// ═══════════════════════════════════════════════════════════════════════════════

import { Controller, Get, Post, Body, Param, Query } from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiQuery,
  ApiBody,
  ApiParam,
} from "@nestjs/swagger";
import { WebDataCollectorService } from "./web-data-collector.service";

class CollectionJobInput {
  sources: string[];
  region?: string;
  commodities?: string[];
  dateRange?: { from: string; to: string };
}

@ApiTags("web-data-collector")
@Controller("api/v1/data-collector")
export class WebDataCollectorController {
  constructor(private readonly collectorService: WebDataCollectorService) {}

  // ─────────────────────────────────────────────────────────────────────────────
  // Data Sources - مصادر البيانات
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("sources")
  @ApiOperation({
    summary: "List all available data sources",
    description: "قائمة جميع مصادر البيانات الزراعية المتاحة",
  })
  @ApiQuery({
    name: "type",
    required: false,
    enum: [
      "weather",
      "market",
      "research",
      "satellite",
      "commodity",
      "news",
      "government",
    ],
  })
  @ApiQuery({ name: "region", required: false, example: "saudi_arabia" })
  @ApiQuery({ name: "free", required: false, type: "boolean" })
  @ApiResponse({ status: 200, description: "List of data sources" })
  listSources(
    @Query("type") type?: string,
    @Query("region") region?: string,
    @Query("free") free?: string,
  ) {
    let sources = this.collectorService.getAllDataSources();

    if (type) {
      // Type guard to ensure type is valid
      const validTypes = [
        "weather",
        "market",
        "research",
        "satellite",
        "commodity",
        "news",
        "government",
      ];
      const isValidType = (
        t: string,
      ): t is
        | "weather"
        | "market"
        | "research"
        | "satellite"
        | "commodity"
        | "news"
        | "government" => {
        return validTypes.includes(t);
      };

      if (isValidType(type)) {
        sources = this.collectorService.getDataSourcesByType(type);
      }
    }

    if (region) {
      sources = sources.filter(
        (s) => s.region.includes(region) || s.region.includes("global"),
      );
    }

    if (free === "true") {
      sources = sources.filter((s) => s.isFree);
    }

    return {
      sources,
      total: sources.length,
      filters: { type, region, free },
      stats: this.collectorService.getSourceStatistics(),
    };
  }

  @Get("sources/:id")
  @ApiOperation({
    summary: "Get data source details",
    description: "الحصول على تفاصيل مصدر بيانات معين",
  })
  @ApiParam({ name: "id", example: "copernicus" })
  @ApiResponse({ status: 200, description: "Data source details" })
  getSource(@Param("id") id: string) {
    const source = this.collectorService.getDataSourceById(id);

    if (!source) {
      return {
        error: `Data source ${id} not found`,
        availableSources: this.collectorService
          .getAllDataSources()
          .map((s) => s.id),
      };
    }

    return { source };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Collection Jobs - مهام الجمع
  // ─────────────────────────────────────────────────────────────────────────────

  @Post("collect")
  @ApiOperation({
    summary: "Create a data collection job",
    description: "إنشاء مهمة جمع بيانات جديدة - مستوحى من Browserbase",
  })
  @ApiBody({
    description: "Collection configuration",
    schema: {
      type: "object",
      properties: {
        sources: {
          type: "array",
          items: { type: "string" },
          example: ["copernicus", "openmeteo"],
        },
        region: { type: "string", example: "saudi_arabia" },
        commodities: {
          type: "array",
          items: { type: "string" },
          example: ["wheat", "dates"],
        },
        dateRange: {
          type: "object",
          properties: {
            from: { type: "string", example: "2024-01-01" },
            to: { type: "string", example: "2024-12-31" },
          },
        },
      },
      required: ["sources"],
    },
  })
  @ApiResponse({ status: 200, description: "Collection job created" })
  createCollectionJob(@Body() input: CollectionJobInput) {
    const job = this.collectorService.createCollectionJob(input);

    return {
      ...job,
      apiNote:
        "In production, this would trigger actual web scraping/API calls",
      apiNoteAr:
        "في بيئة الإنتاج، سيؤدي هذا إلى تشغيل عمليات استخراج فعلية من الويب",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Market Data - بيانات السوق
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("market/prices")
  @ApiOperation({
    summary: "Get current market prices for agricultural commodities",
    description: "الحصول على أسعار السوق الحالية للسلع الزراعية",
  })
  @ApiQuery({
    name: "commodities",
    required: false,
    description: "Comma-separated list of commodities",
    example: "wheat,dates,barley",
  })
  @ApiResponse({ status: 200, description: "Market prices" })
  getMarketPrices(@Query("commodities") commodities?: string) {
    const commodityList = commodities?.split(",").map((c) => c.trim());
    const prices = this.collectorService.getMarketPrices(commodityList);

    return {
      prices,
      total: prices.length,
      lastUpdated: new Date().toISOString(),
      dataSource: "Aggregated from multiple sources",
      dataSourceAr: "مجمعة من مصادر متعددة",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Weather Alerts - تنبيهات الطقس
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("weather/alerts")
  @ApiOperation({
    summary: "Get active weather alerts affecting agriculture",
    description: "الحصول على تنبيهات الطقس النشطة المؤثرة على الزراعة",
  })
  @ApiQuery({ name: "region", required: false, example: "Riyadh" })
  @ApiResponse({ status: 200, description: "Weather alerts" })
  getWeatherAlerts(@Query("region") region?: string) {
    const alerts = this.collectorService.getWeatherAlerts(region);

    return {
      alerts,
      total: alerts.length,
      highSeverityCount: alerts.filter(
        (a) => a.severity === "high" || a.severity === "extreme",
      ).length,
      lastChecked: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Agricultural News - أخبار زراعية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("news")
  @ApiOperation({
    summary: "Get latest agricultural news",
    description: "الحصول على آخر الأخبار الزراعية",
  })
  @ApiQuery({
    name: "category",
    required: false,
    enum: ["policy", "market", "technology", "weather", "research", "pest"],
  })
  @ApiQuery({ name: "limit", required: false, type: "number", example: 10 })
  @ApiResponse({ status: 200, description: "Agricultural news" })
  getNews(
    @Query("category") category?: string,
    @Query("limit") limit?: string,
  ) {
    // Type guard for news category
    type NewsCategory =
      | "policy"
      | "market"
      | "technology"
      | "weather"
      | "research"
      | "pest";
    const validCategories: NewsCategory[] = [
      "policy",
      "market",
      "technology",
      "weather",
      "research",
      "pest",
    ];
    const isValidCategory = (
      c: string | undefined,
    ): c is NewsCategory | undefined => {
      return c === undefined || validCategories.includes(c as NewsCategory);
    };

    const news = this.collectorService.getAgriculturalNews(
      isValidCategory(category) ? category : undefined,
      limit ? parseInt(limit, 10) : undefined,
    );

    return {
      news,
      total: news.length,
      categories: [
        "policy",
        "market",
        "technology",
        "weather",
        "research",
        "pest",
      ],
      lastFetched: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Research Papers - أوراق بحثية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("research")
  @ApiOperation({
    summary: "Get relevant agricultural research papers",
    description: "الحصول على أوراق بحثية زراعية ذات صلة",
  })
  @ApiQuery({
    name: "keywords",
    required: false,
    description: "Comma-separated keywords",
    example: "irrigation,yield,machine learning",
  })
  @ApiResponse({ status: 200, description: "Research papers" })
  getResearch(@Query("keywords") keywords?: string) {
    const keywordList = keywords?.split(",").map((k) => k.trim());
    const papers = this.collectorService.getResearchPapers(keywordList);

    return {
      papers,
      total: papers.length,
      source: "Aggregated from AGRIS, KACST, and other repositories",
      sourceAr: "مجمعة من AGRIS و KACST ومستودعات أخرى",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Intelligence Report - تقرير الاستخبارات
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("intelligence")
  @ApiOperation({
    summary: "Get aggregated agricultural intelligence report",
    description: "الحصول على تقرير استخبارات زراعية مجمع",
  })
  @ApiQuery({ name: "region", required: false, example: "saudi_arabia" })
  @ApiResponse({ status: 200, description: "Intelligence report" })
  getIntelligenceReport(@Query("region") region?: string) {
    const report = this.collectorService.getAgriculturalIntelligence(
      region || "saudi_arabia",
    );

    return {
      ...report,
      apiNote:
        "Comprehensive agricultural intelligence from multiple data sources",
      apiNoteAr: "استخبارات زراعية شاملة من مصادر بيانات متعددة",
      inspiration: "Browserbase MCP - Automated web data collection",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Statistics - الإحصائيات
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("statistics")
  @ApiOperation({
    summary: "Get data collection statistics",
    description: "الحصول على إحصائيات جمع البيانات",
  })
  @ApiResponse({ status: 200, description: "Collection statistics" })
  getStatistics() {
    const stats = this.collectorService.getSourceStatistics();

    return {
      ...stats,
      timestamp: new Date().toISOString(),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Demo Endpoints - نقاط النهاية التجريبية
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("demo")
  @ApiOperation({
    summary: "Run demo data collection",
    description: "تشغيل جمع بيانات تجريبي",
  })
  @ApiResponse({ status: 200, description: "Demo collection result" })
  runDemo() {
    const job = this.collectorService.createCollectionJob({
      sources: ["copernicus", "openmeteo", "fao_giews"],
      region: "saudi_arabia",
    });

    const intelligence =
      this.collectorService.getAgriculturalIntelligence("saudi_arabia");

    return {
      job,
      intelligence,
      demo: true,
      note: "This is simulated data for demonstration",
      noteAr: "هذه بيانات محاكاة للعرض التوضيحي",
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check
  // ─────────────────────────────────────────────────────────────────────────────

  @Get("health")
  @ApiOperation({
    summary: "Web data collector service health check",
    description: "فحص صحة خدمة جمع البيانات من الويب",
  })
  @ApiResponse({ status: 200, description: "Service is healthy" })
  healthCheck() {
    const stats = this.collectorService.getSourceStatistics();

    return {
      status: "healthy",
      service: "web-data-collector",
      timestamp: new Date().toISOString(),
      version: "1.0.0",
      inspiration: "Browserbase MCP - Automated Web Data Collection",
      stats,
      features: [
        "Multi-source data aggregation",
        "Market price tracking",
        "Weather alert monitoring",
        "Agricultural news aggregation",
        "Research paper discovery",
        "Intelligence report generation",
      ],
      featuresAr: [
        "تجميع بيانات من مصادر متعددة",
        "تتبع أسعار السوق",
        "مراقبة تنبيهات الطقس",
        "تجميع الأخبار الزراعية",
        "اكتشاف الأوراق البحثية",
        "توليد تقارير الاستخبارات",
      ],
      sourceTypes: Object.keys(stats.byType),
      regions: Object.keys(stats.byRegion),
    };
  }
}
