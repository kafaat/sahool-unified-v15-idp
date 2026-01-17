// ═══════════════════════════════════════════════════════════════════════════════
// Phenology Service - خدمة مراحل النمو
// Based on WOFOST DVS (Development Stage) and thermal time accumulation
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";

// ─────────────────────────────────────────────────────────────────────────────
// Crop Parameters (WOFOST-style)
// معاملات المحاصيل على طريقة WOFOST
// ─────────────────────────────────────────────────────────────────────────────

export interface CropPhenologyParams {
  nameAr: string;
  nameEn: string;
  TSUM1: number; // Temperature sum from emergence to flowering (°C·day)
  TSUM2: number; // Temperature sum from flowering to maturity (°C·day)
  TBASEM: number; // Base temperature for emergence (°C)
  TEFFMX: number; // Maximum effective temperature (°C)
  TSUMEM: number; // Temperature sum for emergence (°C·day)
  IDSL: number; // Day length sensitivity (0=none, 1=long day, 2=short day)
  DLO: number; // Optimal day length (hours)
  DLC: number; // Critical day length (hours)
  stages: {
    code: string;
    name: string;
    nameAr: string;
    dvsStart: number;
    dvsEnd: number;
  }[];
}

const CROP_PHENOLOGY: Record<string, CropPhenologyParams> = {
  WHEAT: {
    nameAr: "القمح",
    nameEn: "Wheat",
    TSUM1: 1100, // Emergence to flowering
    TSUM2: 1000, // Flowering to maturity
    TBASEM: 0, // Base temperature
    TEFFMX: 30, // Max effective temperature
    TSUMEM: 120, // Emergence temperature sum
    IDSL: 1, // Long day plant
    DLO: 16, // Optimal day length
    DLC: 8, // Critical day length
    stages: [
      {
        code: "EMERGENCE",
        name: "Emergence",
        nameAr: "الإنبات",
        dvsStart: 0,
        dvsEnd: 0.1,
      },
      {
        code: "TILLERING",
        name: "Tillering",
        nameAr: "التفريع",
        dvsStart: 0.1,
        dvsEnd: 0.3,
      },
      {
        code: "STEM_ELONGATION",
        name: "Stem Elongation",
        nameAr: "استطالة الساق",
        dvsStart: 0.3,
        dvsEnd: 0.5,
      },
      {
        code: "BOOTING",
        name: "Booting",
        nameAr: "التبرعم",
        dvsStart: 0.5,
        dvsEnd: 0.7,
      },
      {
        code: "HEADING",
        name: "Heading",
        nameAr: "طرد السنابل",
        dvsStart: 0.7,
        dvsEnd: 0.9,
      },
      {
        code: "FLOWERING",
        name: "Flowering",
        nameAr: "الإزهار",
        dvsStart: 0.9,
        dvsEnd: 1.0,
      },
      {
        code: "GRAIN_FILLING",
        name: "Grain Filling",
        nameAr: "امتلاء الحبوب",
        dvsStart: 1.0,
        dvsEnd: 1.5,
      },
      {
        code: "MATURITY",
        name: "Maturity",
        nameAr: "النضج",
        dvsStart: 1.5,
        dvsEnd: 2.0,
      },
    ],
  },
  RICE: {
    nameAr: "الأرز",
    nameEn: "Rice",
    TSUM1: 1200,
    TSUM2: 900,
    TBASEM: 10,
    TEFFMX: 35,
    TSUMEM: 100,
    IDSL: 2, // Short day plant
    DLO: 12,
    DLC: 14,
    stages: [
      {
        code: "EMERGENCE",
        name: "Emergence",
        nameAr: "الإنبات",
        dvsStart: 0,
        dvsEnd: 0.1,
      },
      {
        code: "SEEDLING",
        name: "Seedling",
        nameAr: "الشتلة",
        dvsStart: 0.1,
        dvsEnd: 0.2,
      },
      {
        code: "TILLERING",
        name: "Tillering",
        nameAr: "التفريع",
        dvsStart: 0.2,
        dvsEnd: 0.4,
      },
      {
        code: "STEM_ELONGATION",
        name: "Stem Elongation",
        nameAr: "استطالة الساق",
        dvsStart: 0.4,
        dvsEnd: 0.6,
      },
      {
        code: "BOOTING",
        name: "Booting",
        nameAr: "التبرعم",
        dvsStart: 0.6,
        dvsEnd: 0.8,
      },
      {
        code: "HEADING",
        name: "Heading",
        nameAr: "طرد السنابل",
        dvsStart: 0.8,
        dvsEnd: 0.9,
      },
      {
        code: "FLOWERING",
        name: "Flowering",
        nameAr: "الإزهار",
        dvsStart: 0.9,
        dvsEnd: 1.0,
      },
      {
        code: "GRAIN_FILLING",
        name: "Grain Filling",
        nameAr: "امتلاء الحبوب",
        dvsStart: 1.0,
        dvsEnd: 1.6,
      },
      {
        code: "MATURITY",
        name: "Maturity",
        nameAr: "النضج",
        dvsStart: 1.6,
        dvsEnd: 2.0,
      },
    ],
  },
  CORN: {
    nameAr: "الذرة",
    nameEn: "Corn/Maize",
    TSUM1: 800,
    TSUM2: 750,
    TBASEM: 10,
    TEFFMX: 30,
    TSUMEM: 80,
    IDSL: 0, // Day neutral
    DLO: 12,
    DLC: 12,
    stages: [
      {
        code: "EMERGENCE",
        name: "Emergence",
        nameAr: "الإنبات",
        dvsStart: 0,
        dvsEnd: 0.1,
      },
      {
        code: "V3_V6",
        name: "V3-V6 Vegetative",
        nameAr: "النمو الخضري المبكر",
        dvsStart: 0.1,
        dvsEnd: 0.3,
      },
      {
        code: "V7_VT",
        name: "V7-VT Vegetative",
        nameAr: "النمو الخضري المتأخر",
        dvsStart: 0.3,
        dvsEnd: 0.6,
      },
      {
        code: "TASSELING",
        name: "Tasseling",
        nameAr: "التزهير",
        dvsStart: 0.6,
        dvsEnd: 0.8,
      },
      {
        code: "SILKING",
        name: "Silking",
        nameAr: "خروج الشعيرات",
        dvsStart: 0.8,
        dvsEnd: 1.0,
      },
      {
        code: "BLISTER",
        name: "Blister (R2)",
        nameAr: "مرحلة البثور",
        dvsStart: 1.0,
        dvsEnd: 1.2,
      },
      {
        code: "DOUGH",
        name: "Dough (R4)",
        nameAr: "مرحلة العجين",
        dvsStart: 1.2,
        dvsEnd: 1.5,
      },
      {
        code: "DENT",
        name: "Dent (R5)",
        nameAr: "مرحلة التضليع",
        dvsStart: 1.5,
        dvsEnd: 1.8,
      },
      {
        code: "MATURITY",
        name: "Physiological Maturity",
        nameAr: "النضج الفسيولوجي",
        dvsStart: 1.8,
        dvsEnd: 2.0,
      },
    ],
  },
  SOYBEAN: {
    nameAr: "فول الصويا",
    nameEn: "Soybean",
    TSUM1: 700,
    TSUM2: 800,
    TBASEM: 10,
    TEFFMX: 30,
    TSUMEM: 90,
    IDSL: 2, // Short day plant
    DLO: 12,
    DLC: 14,
    stages: [
      {
        code: "VE",
        name: "Emergence",
        nameAr: "الإنبات",
        dvsStart: 0,
        dvsEnd: 0.1,
      },
      {
        code: "VC",
        name: "Cotyledon",
        nameAr: "الفلقات",
        dvsStart: 0.1,
        dvsEnd: 0.15,
      },
      {
        code: "V1_V3",
        name: "V1-V3 Vegetative",
        nameAr: "النمو الخضري المبكر",
        dvsStart: 0.15,
        dvsEnd: 0.4,
      },
      {
        code: "V4_V6",
        name: "V4-V6 Vegetative",
        nameAr: "النمو الخضري المتأخر",
        dvsStart: 0.4,
        dvsEnd: 0.7,
      },
      {
        code: "R1",
        name: "Beginning Bloom",
        nameAr: "بداية الإزهار",
        dvsStart: 0.7,
        dvsEnd: 0.85,
      },
      {
        code: "R2",
        name: "Full Bloom",
        nameAr: "الإزهار الكامل",
        dvsStart: 0.85,
        dvsEnd: 1.0,
      },
      {
        code: "R3_R4",
        name: "Pod Development",
        nameAr: "تطور القرون",
        dvsStart: 1.0,
        dvsEnd: 1.3,
      },
      {
        code: "R5_R6",
        name: "Seed Filling",
        nameAr: "امتلاء البذور",
        dvsStart: 1.3,
        dvsEnd: 1.7,
      },
      {
        code: "R7_R8",
        name: "Maturity",
        nameAr: "النضج",
        dvsStart: 1.7,
        dvsEnd: 2.0,
      },
    ],
  },
  SUGARCANE: {
    nameAr: "قصب السكر",
    nameEn: "Sugarcane",
    TSUM1: 2000,
    TSUM2: 2500,
    TBASEM: 15,
    TEFFMX: 35,
    TSUMEM: 200,
    IDSL: 2,
    DLO: 12,
    DLC: 13,
    stages: [
      {
        code: "GERMINATION",
        name: "Germination",
        nameAr: "الإنبات",
        dvsStart: 0,
        dvsEnd: 0.05,
      },
      {
        code: "SPROUTING",
        name: "Sprouting",
        nameAr: "التبرعم",
        dvsStart: 0.05,
        dvsEnd: 0.1,
      },
      {
        code: "TILLERING",
        name: "Tillering",
        nameAr: "التفريع",
        dvsStart: 0.1,
        dvsEnd: 0.3,
      },
      {
        code: "GRAND_GROWTH",
        name: "Grand Growth",
        nameAr: "النمو السريع",
        dvsStart: 0.3,
        dvsEnd: 0.7,
      },
      {
        code: "STALK_ELONGATION",
        name: "Stalk Elongation",
        nameAr: "استطالة الساق",
        dvsStart: 0.7,
        dvsEnd: 1.0,
      },
      {
        code: "RIPENING",
        name: "Ripening",
        nameAr: "النضج",
        dvsStart: 1.0,
        dvsEnd: 1.5,
      },
      {
        code: "MATURITY",
        name: "Maturity",
        nameAr: "النضج الكامل",
        dvsStart: 1.5,
        dvsEnd: 2.0,
      },
    ],
  },
  COFFEE: {
    nameAr: "البن",
    nameEn: "Coffee",
    TSUM1: 3000,
    TSUM2: 2000,
    TBASEM: 10,
    TEFFMX: 30,
    TSUMEM: 300,
    IDSL: 0,
    DLO: 12,
    DLC: 12,
    stages: [
      {
        code: "ESTABLISHMENT",
        name: "Establishment",
        nameAr: "التأسيس",
        dvsStart: 0,
        dvsEnd: 0.1,
      },
      {
        code: "VEGETATIVE",
        name: "Vegetative Growth",
        nameAr: "النمو الخضري",
        dvsStart: 0.1,
        dvsEnd: 0.4,
      },
      {
        code: "BUD_INITIATION",
        name: "Bud Initiation",
        nameAr: "تكوين البراعم",
        dvsStart: 0.4,
        dvsEnd: 0.6,
      },
      {
        code: "FLOWERING",
        name: "Flowering",
        nameAr: "الإزهار",
        dvsStart: 0.6,
        dvsEnd: 0.8,
      },
      {
        code: "FRUIT_SET",
        name: "Fruit Set",
        nameAr: "عقد الثمار",
        dvsStart: 0.8,
        dvsEnd: 1.0,
      },
      {
        code: "EXPANSION",
        name: "Fruit Expansion",
        nameAr: "نمو الثمار",
        dvsStart: 1.0,
        dvsEnd: 1.4,
      },
      {
        code: "RIPENING",
        name: "Ripening",
        nameAr: "النضج",
        dvsStart: 1.4,
        dvsEnd: 1.8,
      },
      {
        code: "HARVEST",
        name: "Harvest Ready",
        nameAr: "جاهز للحصاد",
        dvsStart: 1.8,
        dvsEnd: 2.0,
      },
    ],
  },
};

@Injectable()
export class PhenologyService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Growing Degree Days (GDD)
  // حساب درجات الحرارة المتراكمة
  // ─────────────────────────────────────────────────────────────────────────────

  calculateGDD(
    tmin: number,
    tmax: number,
    tbase: number,
    tmax_eff: number,
  ): number {
    // Average temperature
    const tavg = (tmin + tmax) / 2;

    // Apply temperature limits
    const t_eff = Math.min(Math.max(tavg, tbase), tmax_eff);

    // Calculate GDD
    const gdd = Math.max(0, t_eff - tbase);

    return Math.round(gdd * 100) / 100;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Development Stage (DVS)
  // حساب مرحلة التطور
  // ─────────────────────────────────────────────────────────────────────────────

  calculateDVS(
    accumulatedGDD: number,
    cropType: string,
    afterFlowering: boolean = false,
  ): {
    dvs: number;
    stage: {
      code: string;
      name: string;
      nameAr: string;
    };
    progress: number;
  } {
    const params = CROP_PHENOLOGY[cropType] || CROP_PHENOLOGY.WHEAT;

    let dvs: number;
    if (!afterFlowering) {
      // Pre-flowering: DVS = 0 to 1
      dvs = Math.min(1, accumulatedGDD / params.TSUM1);
    } else {
      // Post-flowering: DVS = 1 to 2
      dvs = 1 + Math.min(1, accumulatedGDD / params.TSUM2);
    }

    // Find current stage
    const currentStage =
      params.stages.find((s) => dvs >= s.dvsStart && dvs < s.dvsEnd) ||
      params.stages[params.stages.length - 1];

    // Calculate progress within stage
    const stageLength = currentStage.dvsEnd - currentStage.dvsStart;
    const stageProgress = (dvs - currentStage.dvsStart) / stageLength;

    return {
      dvs: Math.round(dvs * 1000) / 1000,
      stage: {
        code: currentStage.code,
        name: currentStage.name,
        nameAr: currentStage.nameAr,
      },
      progress: Math.round(Math.min(100, stageProgress * 100)),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Simulate Phenology for Season
  // محاكاة مراحل النمو للموسم
  // ─────────────────────────────────────────────────────────────────────────────

  simulatePhenology(
    cropType: string,
    sowingDate: string,
    weatherData: Array<{ date: string; tmin: number; tmax: number }>,
  ): Array<{
    date: string;
    day: number;
    gdd: number;
    accGDD: number;
    dvs: number;
    stage: string;
    stageAr: string;
  }> {
    const params = CROP_PHENOLOGY[cropType] || CROP_PHENOLOGY.WHEAT;
    const results: Array<{
      date: string;
      day: number;
      gdd: number;
      accGDD: number;
      dvs: number;
      stage: string;
      stageAr: string;
    }> = [];

    let accGDD = 0;
    let afterFlowering = false;
    let floweringGDD = 0;

    weatherData.forEach((day, index) => {
      const gdd = this.calculateGDD(
        day.tmin,
        day.tmax,
        params.TBASEM,
        params.TEFFMX,
      );
      accGDD += gdd;

      // Check if we've reached flowering
      if (!afterFlowering && accGDD >= params.TSUM1) {
        afterFlowering = true;
        floweringGDD = accGDD;
      }

      const gddForDVS = afterFlowering ? accGDD - floweringGDD : accGDD;
      const { dvs, stage } = this.calculateDVS(
        gddForDVS,
        cropType,
        afterFlowering,
      );

      results.push({
        date: day.date,
        day: index + 1,
        gdd,
        accGDD: Math.round(accGDD * 10) / 10,
        dvs,
        stage: stage.name,
        stageAr: stage.nameAr,
      });
    });

    return results;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Predict Key Dates
  // التنبؤ بالتواريخ الرئيسية
  // ─────────────────────────────────────────────────────────────────────────────

  predictKeyDates(
    cropType: string,
    sowingDate: string,
    avgDailyGDD: number = 15,
  ): Array<{
    event: string;
    eventAr: string;
    estimatedDate: string;
    daysFromSowing: number;
  }> {
    const params = CROP_PHENOLOGY[cropType] || CROP_PHENOLOGY.WHEAT;
    const sowDate = new Date(sowingDate);

    const keyEvents = [
      { event: "Emergence", eventAr: "الإنبات", gddRequired: params.TSUMEM },
      { event: "Flowering", eventAr: "الإزهار", gddRequired: params.TSUM1 },
      {
        event: "Maturity",
        eventAr: "النضج",
        gddRequired: params.TSUM1 + params.TSUM2,
      },
    ];

    return keyEvents.map((event) => {
      const daysRequired = Math.ceil(event.gddRequired / avgDailyGDD);
      const eventDate = new Date(sowDate);
      eventDate.setDate(eventDate.getDate() + daysRequired);

      return {
        event: event.event,
        eventAr: event.eventAr,
        estimatedDate: eventDate.toISOString().split("T")[0],
        daysFromSowing: daysRequired,
      };
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Parameters
  // الحصول على معاملات المحصول
  // ─────────────────────────────────────────────────────────────────────────────

  getCropParameters(
    cropType?: string,
  ): CropPhenologyParams | Record<string, CropPhenologyParams> {
    if (cropType) {
      return CROP_PHENOLOGY[cropType] || null;
    }
    return CROP_PHENOLOGY;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Available Crops
  // الحصول على المحاصيل المتاحة
  // ─────────────────────────────────────────────────────────────────────────────

  getAvailableCrops(): Array<{ id: string; nameEn: string; nameAr: string }> {
    return Object.entries(CROP_PHENOLOGY).map(([id, params]) => ({
      id,
      nameEn: params.nameEn,
      nameAr: params.nameAr,
    }));
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Growth Stages for Crop
  // الحصول على مراحل النمو للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  getGrowthStages(cropType: string): Array<{
    code: string;
    name: string;
    nameAr: string;
    dvsStart: number;
    dvsEnd: number;
  }> | null {
    const params = CROP_PHENOLOGY[cropType];
    return params ? params.stages : null;
  }
}
