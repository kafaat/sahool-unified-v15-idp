// ═══════════════════════════════════════════════════════════════════════════════
// Web Data Collector Service - خدمة جمع البيانات من الويب
// Inspired by Browserbase MCP for automated web data collection
// Agricultural data sources aggregation for SAHOOL platform
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";

// ─────────────────────────────────────────────────────────────────────────────
// Interfaces & Types
// ─────────────────────────────────────────────────────────────────────────────

export interface DataSource {
  id: string;
  nameEn: string;
  nameAr: string;
  type:
    | "weather"
    | "market"
    | "research"
    | "satellite"
    | "commodity"
    | "news"
    | "government";
  url: string;
  region: string[];
  dataFormat: "api" | "html" | "json" | "xml" | "rss";
  updateFrequency: "realtime" | "hourly" | "daily" | "weekly";
  isFree: boolean;
  reliability: number; // 0-1 score
  dataTypes: string[];
}

export interface CollectionJob {
  id: string;
  source: DataSource;
  status: "pending" | "running" | "completed" | "failed";
  startedAt?: string;
  completedAt?: string;
  recordsCollected?: number;
  error?: string;
}

export interface MarketPrice {
  commodity: string;
  commodityAr: string;
  price: number;
  unit: string;
  currency: string;
  market: string;
  marketAr: string;
  date: string;
  change: number;
  changePercent: number;
}

export interface WeatherAlert {
  id: string;
  type: "frost" | "heat" | "rain" | "wind" | "dust" | "flood" | "drought";
  severity: "low" | "medium" | "high" | "extreme";
  titleEn: string;
  titleAr: string;
  descriptionEn: string;
  descriptionAr: string;
  affectedRegions: string[];
  validFrom: string;
  validTo: string;
  source: string;
}

export interface AgriculturalNews {
  id: string;
  titleEn: string;
  titleAr: string;
  summary: string;
  summaryAr: string;
  source: string;
  url: string;
  publishedAt: string;
  category:
    | "policy"
    | "market"
    | "technology"
    | "weather"
    | "research"
    | "pest";
  region: string;
  relevanceScore: number;
}

export interface ResearchPaper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  journal: string;
  year: number;
  doi?: string;
  keywords: string[];
  relevanceToSahool: string[];
  impactFactor?: number;
}

export interface CollectorConfig {
  sources: string[];
  region?: string;
  commodities?: string[];
  dateRange?: { from: string; to: string };
}

@Injectable()
export class WebDataCollectorService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Data Sources Database - قاعدة بيانات مصادر البيانات
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly dataSources: Map<string, DataSource> = new Map([
    // Weather Data Sources
    [
      "openmeteo",
      {
        id: "openmeteo",
        nameEn: "Open-Meteo Weather API",
        nameAr: "واجهة Open-Meteo للطقس",
        type: "weather",
        url: "https://api.open-meteo.com",
        region: ["global"],
        dataFormat: "api",
        updateFrequency: "hourly",
        isFree: true,
        reliability: 0.92,
        dataTypes: ["temperature", "precipitation", "wind", "humidity", "et0"],
      },
    ],
    [
      "ncm_sa",
      {
        id: "ncm_sa",
        nameEn: "Saudi National Center for Meteorology",
        nameAr: "المركز الوطني للأرصاد السعودي",
        type: "weather",
        url: "https://ncm.gov.sa",
        region: ["saudi_arabia"],
        dataFormat: "html",
        updateFrequency: "hourly",
        isFree: true,
        reliability: 0.95,
        dataTypes: ["forecast", "alerts", "historical"],
      },
    ],
    // Market Data Sources
    [
      "fao_giews",
      {
        id: "fao_giews",
        nameEn: "FAO Global Information and Early Warning System",
        nameAr: "نظام الإنذار المبكر العالمي للفاو",
        type: "market",
        url: "https://www.fao.org/giews",
        region: ["global"],
        dataFormat: "html",
        updateFrequency: "weekly",
        isFree: true,
        reliability: 0.98,
        dataTypes: ["food_prices", "production", "trade"],
      },
    ],
    [
      "saudi_grains",
      {
        id: "saudi_grains",
        nameEn: "Saudi Grains Organization",
        nameAr: "المؤسسة العامة للحبوب",
        type: "market",
        url: "https://gsfmo.gov.sa",
        region: ["saudi_arabia"],
        dataFormat: "html",
        updateFrequency: "daily",
        isFree: true,
        reliability: 0.95,
        dataTypes: ["wheat_prices", "barley_prices", "import_data"],
      },
    ],
    [
      "emirates_market",
      {
        id: "emirates_market",
        nameEn: "Dubai Multi Commodities Centre",
        nameAr: "مركز دبي للسلع المتعددة",
        type: "commodity",
        url: "https://www.dmcc.ae",
        region: ["uae", "gcc"],
        dataFormat: "html",
        updateFrequency: "daily",
        isFree: false,
        reliability: 0.93,
        dataTypes: ["commodity_prices", "trading_volumes"],
      },
    ],
    // Satellite Data Sources
    [
      "copernicus",
      {
        id: "copernicus",
        nameEn: "Copernicus Open Access Hub",
        nameAr: "منصة كوبرنيكوس المفتوحة",
        type: "satellite",
        url: "https://scihub.copernicus.eu",
        region: ["global"],
        dataFormat: "api",
        updateFrequency: "daily",
        isFree: true,
        reliability: 0.97,
        dataTypes: ["sentinel_2", "sentinel_1", "ndvi", "lai"],
      },
    ],
    [
      "usgs_earthexplorer",
      {
        id: "usgs_earthexplorer",
        nameEn: "USGS Earth Explorer",
        nameAr: "مستكشف الأرض USGS",
        type: "satellite",
        url: "https://earthexplorer.usgs.gov",
        region: ["global"],
        dataFormat: "api",
        updateFrequency: "daily",
        isFree: true,
        reliability: 0.96,
        dataTypes: ["landsat_8", "landsat_9", "modis"],
      },
    ],
    // Research Sources
    [
      "agris_fao",
      {
        id: "agris_fao",
        nameEn: "AGRIS - FAO Agricultural Research",
        nameAr: "AGRIS - بحوث الفاو الزراعية",
        type: "research",
        url: "https://agris.fao.org",
        region: ["global"],
        dataFormat: "api",
        updateFrequency: "daily",
        isFree: true,
        reliability: 0.95,
        dataTypes: ["papers", "reports", "data"],
      },
    ],
    [
      "kacst",
      {
        id: "kacst",
        nameEn: "King Abdulaziz City for Science and Technology",
        nameAr: "مدينة الملك عبدالعزيز للعلوم والتقنية",
        type: "research",
        url: "https://www.kacst.edu.sa",
        region: ["saudi_arabia"],
        dataFormat: "html",
        updateFrequency: "weekly",
        isFree: true,
        reliability: 0.9,
        dataTypes: ["local_research", "innovation", "agriculture"],
      },
    ],
    // Government Sources
    [
      "mewa_sa",
      {
        id: "mewa_sa",
        nameEn: "Saudi Ministry of Environment, Water and Agriculture",
        nameAr: "وزارة البيئة والمياه والزراعة السعودية",
        type: "government",
        url: "https://mewa.gov.sa",
        region: ["saudi_arabia"],
        dataFormat: "html",
        updateFrequency: "daily",
        isFree: true,
        reliability: 0.98,
        dataTypes: ["regulations", "statistics", "alerts", "subsidies"],
      },
    ],
    // News Sources
    [
      "arab_agriculture",
      {
        id: "arab_agriculture",
        nameEn: "Arab Agriculture News Network",
        nameAr: "شبكة أخبار الزراعة العربية",
        type: "news",
        url: "https://arabagrinews.com",
        region: ["mena"],
        dataFormat: "rss",
        updateFrequency: "daily",
        isFree: true,
        reliability: 0.85,
        dataTypes: ["news", "analysis", "events"],
      },
    ],
  ]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Simulated Data Store - مخزن البيانات المحاكاة
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly sampleMarketPrices: MarketPrice[] = [
    {
      commodity: "Wheat",
      commodityAr: "قمح",
      price: 1850,
      unit: "ton",
      currency: "SAR",
      market: "Riyadh Central Market",
      marketAr: "سوق الرياض المركزي",
      date: new Date().toISOString().split("T")[0],
      change: 25,
      changePercent: 1.37,
    },
    {
      commodity: "Barley",
      commodityAr: "شعير",
      price: 1200,
      unit: "ton",
      currency: "SAR",
      market: "Riyadh Central Market",
      marketAr: "سوق الرياض المركزي",
      date: new Date().toISOString().split("T")[0],
      change: -15,
      changePercent: -1.23,
    },
    {
      commodity: "Dates (Sukkari)",
      commodityAr: "تمر سكري",
      price: 45,
      unit: "kg",
      currency: "SAR",
      market: "Buraidah Date Market",
      marketAr: "سوق بريدة للتمور",
      date: new Date().toISOString().split("T")[0],
      change: 5,
      changePercent: 12.5,
    },
    {
      commodity: "Alfalfa",
      commodityAr: "برسيم",
      price: 650,
      unit: "ton",
      currency: "SAR",
      market: "Al-Qassim Agricultural Market",
      marketAr: "سوق القصيم الزراعي",
      date: new Date().toISOString().split("T")[0],
      change: 0,
      changePercent: 0,
    },
    {
      commodity: "Tomatoes",
      commodityAr: "طماطم",
      price: 3.5,
      unit: "kg",
      currency: "SAR",
      market: "Riyadh Wholesale Market",
      marketAr: "سوق الرياض بالجملة",
      date: new Date().toISOString().split("T")[0],
      change: -0.5,
      changePercent: -12.5,
    },
    {
      commodity: "Cucumbers",
      commodityAr: "خيار",
      price: 2.8,
      unit: "kg",
      currency: "SAR",
      market: "Riyadh Wholesale Market",
      marketAr: "سوق الرياض بالجملة",
      date: new Date().toISOString().split("T")[0],
      change: 0.3,
      changePercent: 12.0,
    },
  ];

  private readonly sampleAlerts: WeatherAlert[] = [
    {
      id: "alert_001",
      type: "heat",
      severity: "high",
      titleEn: "Extreme Heat Warning",
      titleAr: "تحذير من موجة حر شديدة",
      descriptionEn:
        "Temperatures expected to exceed 45°C. Increase irrigation frequency and provide shade for sensitive crops.",
      descriptionAr:
        "يتوقع أن تتجاوز درجات الحرارة 45 درجة مئوية. زد معدل الري ووفر الظل للمحاصيل الحساسة.",
      affectedRegions: ["Riyadh", "Al-Qassim", "Eastern Province"],
      validFrom: new Date().toISOString(),
      validTo: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(),
      source: "NCM Saudi Arabia",
    },
    {
      id: "alert_002",
      type: "dust",
      severity: "medium",
      titleEn: "Dust Storm Advisory",
      titleAr: "تنبيه عاصفة ترابية",
      descriptionEn:
        "Moderate dust storm expected. Cover sensitive equipment and consider delaying pesticide applications.",
      descriptionAr:
        "يتوقع عاصفة ترابية متوسطة. قم بتغطية المعدات الحساسة وفكر في تأجيل تطبيقات المبيدات.",
      affectedRegions: ["Northern Borders", "Al-Jawf"],
      validFrom: new Date().toISOString(),
      validTo: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      source: "NCM Saudi Arabia",
    },
  ];

  private readonly sampleNews: AgriculturalNews[] = [
    {
      id: "news_001",
      titleEn: "Saudi Arabia Announces New Agricultural Subsidies for 2025",
      titleAr: "السعودية تعلن عن دعم زراعي جديد لعام 2025",
      summary:
        "The Ministry of Environment, Water and Agriculture has announced expanded support programs for precision agriculture adoption.",
      summaryAr:
        "أعلنت وزارة البيئة والمياه والزراعة عن توسيع برامج الدعم لتبني الزراعة الدقيقة.",
      source: "MEWA",
      url: "https://mewa.gov.sa/news/subsidies-2025",
      publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      category: "policy",
      region: "Saudi Arabia",
      relevanceScore: 0.95,
    },
    {
      id: "news_002",
      titleEn: "New Date Variety Shows 30% Higher Yield in Al-Qassim Trials",
      titleAr: "صنف تمر جديد يظهر زيادة 30% في الإنتاجية في تجارب القصيم",
      summary:
        "Agricultural researchers have developed a new date palm variety that shows significant yield improvements in hot climates.",
      summaryAr:
        "طور الباحثون الزراعيون صنفاً جديداً من نخيل التمر يظهر تحسناً كبيراً في الإنتاجية في المناخات الحارة.",
      source: "KACST",
      url: "https://kacst.edu.sa/research/dates-2025",
      publishedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      category: "research",
      region: "Saudi Arabia",
      relevanceScore: 0.88,
    },
    {
      id: "news_003",
      titleEn: "Global Wheat Prices Rise Amid Supply Concerns",
      titleAr: "ارتفاع أسعار القمح العالمية وسط مخاوف العرض",
      summary:
        "International wheat prices have increased 8% this month due to production challenges in major exporting countries.",
      summaryAr:
        "ارتفعت أسعار القمح الدولية بنسبة 8% هذا الشهر بسبب تحديات الإنتاج في الدول المصدرة الرئيسية.",
      source: "FAO GIEWS",
      url: "https://fao.org/giews/wheat-2025",
      publishedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      category: "market",
      region: "Global",
      relevanceScore: 0.82,
    },
  ];

  private readonly sampleResearch: ResearchPaper[] = [
    {
      id: "paper_001",
      title: "Deficit Irrigation Strategies for Date Palm in Arid Regions",
      authors: ["Al-Yahyai, R.", "Al-Kharusi, L.", "Chartzoulakis, K."],
      abstract:
        "This study evaluates deficit irrigation strategies for date palm cultivation in arid regions, demonstrating water savings of up to 30% without significant yield reduction.",
      journal: "Agricultural Water Management",
      year: 2024,
      doi: "10.1016/j.agwat.2024.107XXX",
      keywords: [
        "date palm",
        "deficit irrigation",
        "water use efficiency",
        "arid agriculture",
      ],
      relevanceToSahool: ["irrigation-decision", "water-balance", "date-palm"],
      impactFactor: 6.7,
    },
    {
      id: "paper_002",
      title: "Machine Learning for Crop Yield Prediction: A Review",
      authors: ["van Klompenburg, T.", "Kassahun, A.", "Catal, C."],
      abstract:
        "Comprehensive review of machine learning approaches for crop yield prediction, analyzing 567 studies from 2015-2024.",
      journal: "Computers and Electronics in Agriculture",
      year: 2024,
      doi: "10.1016/j.compag.2024.108XXX",
      keywords: [
        "machine learning",
        "yield prediction",
        "precision agriculture",
        "deep learning",
      ],
      relevanceToSahool: ["yield-prediction", "biomass", "simulation"],
      impactFactor: 8.3,
    },
  ];

  // ─────────────────────────────────────────────────────────────────────────────
  // Service Methods
  // ─────────────────────────────────────────────────────────────────────────────

  /**
   * Get all available data sources
   */
  getAllDataSources(): DataSource[] {
    return Array.from(this.dataSources.values());
  }

  /**
   * Get data source by ID
   */
  getDataSourceById(id: string): DataSource | undefined {
    return this.dataSources.get(id);
  }

  /**
   * Get data sources by type
   */
  getDataSourcesByType(type: DataSource["type"]): DataSource[] {
    return Array.from(this.dataSources.values()).filter((s) => s.type === type);
  }

  /**
   * Get data sources by region
   */
  getDataSourcesByRegion(region: string): DataSource[] {
    return Array.from(this.dataSources.values()).filter(
      (s) => s.region.includes(region) || s.region.includes("global"),
    );
  }

  /**
   * Get free data sources only
   */
  getFreeDataSources(): DataSource[] {
    return Array.from(this.dataSources.values()).filter((s) => s.isFree);
  }

  /**
   * Simulate collection job
   */
  createCollectionJob(config: CollectorConfig): CollectionJob {
    const source = this.dataSources.get(config.sources[0]);

    if (!source) {
      return {
        id: `job_${Date.now()}`,
        source: {} as DataSource,
        status: "failed",
        error: `Source ${config.sources[0]} not found`,
      };
    }

    // Simulate job
    return {
      id: `job_${Date.now()}`,
      source,
      status: "completed",
      startedAt: new Date(Date.now() - 5000).toISOString(),
      completedAt: new Date().toISOString(),
      recordsCollected: Math.floor(Math.random() * 100) + 10,
    };
  }

  /**
   * Get latest market prices
   */
  getMarketPrices(commodities?: string[]): MarketPrice[] {
    if (commodities && commodities.length > 0) {
      return this.sampleMarketPrices.filter((p) =>
        commodities.some(
          (c) =>
            p.commodity.toLowerCase().includes(c.toLowerCase()) ||
            p.commodityAr.includes(c),
        ),
      );
    }
    return this.sampleMarketPrices;
  }

  /**
   * Get active weather alerts
   */
  getWeatherAlerts(region?: string): WeatherAlert[] {
    if (region) {
      return this.sampleAlerts.filter((a) =>
        a.affectedRegions.some((r) =>
          r.toLowerCase().includes(region.toLowerCase()),
        ),
      );
    }
    return this.sampleAlerts;
  }

  /**
   * Get agricultural news
   */
  getAgriculturalNews(
    category?: AgriculturalNews["category"],
    limit?: number,
  ): AgriculturalNews[] {
    let news = this.sampleNews;

    if (category) {
      news = news.filter((n) => n.category === category);
    }

    // Sort by relevance and date
    news = news.sort((a, b) => b.relevanceScore - a.relevanceScore);

    if (limit) {
      news = news.slice(0, limit);
    }

    return news;
  }

  /**
   * Get research papers
   */
  getResearchPapers(keywords?: string[]): ResearchPaper[] {
    if (keywords && keywords.length > 0) {
      return this.sampleResearch.filter((p) =>
        keywords.some(
          (k) =>
            p.keywords.some((pk) =>
              pk.toLowerCase().includes(k.toLowerCase()),
            ) ||
            p.title.toLowerCase().includes(k.toLowerCase()) ||
            p.relevanceToSahool.some((r) =>
              r.toLowerCase().includes(k.toLowerCase()),
            ),
        ),
      );
    }
    return this.sampleResearch;
  }

  /**
   * Get aggregated agricultural intelligence report
   */
  getAgriculturalIntelligence(region: string = "saudi_arabia"): {
    generatedAt: string;
    region: string;
    summary: { en: string; ar: string };
    marketOverview: MarketPrice[];
    activeAlerts: WeatherAlert[];
    recentNews: AgriculturalNews[];
    relevantResearch: ResearchPaper[];
    dataSources: DataSource[];
  } {
    const sources = this.getDataSourcesByRegion(region);
    const prices = this.getMarketPrices().slice(0, 5);
    const alerts = this.getWeatherAlerts();
    const news = this.getAgriculturalNews(undefined, 3);
    const research = this.getResearchPapers().slice(0, 2);

    return {
      generatedAt: new Date().toISOString(),
      region,
      summary: {
        en: `Agricultural intelligence report for ${region}. Current market conditions are stable with ${prices.length} commodities tracked. ${alerts.length} active weather alerts requiring attention.`,
        ar: `تقرير الاستخبارات الزراعية لـ ${region}. ظروف السوق الحالية مستقرة مع تتبع ${prices.length} سلع. ${alerts.length} تنبيهات جوية نشطة تتطلب الاهتمام.`,
      },
      marketOverview: prices,
      activeAlerts: alerts,
      recentNews: news,
      relevantResearch: research,
      dataSources: sources,
    };
  }

  /**
   * Get source statistics
   */
  getSourceStatistics(): {
    total: number;
    byType: { [key: string]: number };
    byRegion: { [key: string]: number };
    freeCount: number;
    averageReliability: number;
  } {
    const sources = Array.from(this.dataSources.values());

    const byType: { [key: string]: number } = {};
    const byRegion: { [key: string]: number } = {};

    sources.forEach((s) => {
      byType[s.type] = (byType[s.type] || 0) + 1;
      s.region.forEach((r) => {
        byRegion[r] = (byRegion[r] || 0) + 1;
      });
    });

    const avgReliability =
      sources.reduce((sum, s) => sum + s.reliability, 0) / sources.length;

    return {
      total: sources.length,
      byType,
      byRegion,
      freeCount: sources.filter((s) => s.isFree).length,
      averageReliability: Math.round(avgReliability * 100) / 100,
    };
  }
}
