// ═══════════════════════════════════════════════════════════════════════════════
// Vegetation Indices Service - خدمة مؤشرات الغطاء النباتي
// Based on LAI-TransNet research feature extraction
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from "@nestjs/common";

// ─────────────────────────────────────────────────────────────────────────────
// Index Information
// ─────────────────────────────────────────────────────────────────────────────
export interface IndexInfo {
  name: string;
  nameAr: string;
  formula: string;
  description: string;
  descriptionAr: string;
  range: { min: number; max: number };
  optimalRange: { min: number; max: number };
  reference: string;
}

const VEGETATION_INDICES: Record<string, IndexInfo> = {
  NDVI: {
    name: "Normalized Difference Vegetation Index",
    nameAr: "مؤشر الاختلاف المعياري للغطاء النباتي",
    formula: "(NIR - Red) / (NIR + Red)",
    description:
      "Most widely used vegetation index for monitoring plant health and density",
    descriptionAr: "المؤشر الأكثر استخداماً لرصد صحة النبات وكثافته",
    range: { min: -1, max: 1 },
    optimalRange: { min: 0.6, max: 0.9 },
    reference: "Rouse et al., 1974",
  },
  EVI2: {
    name: "Enhanced Vegetation Index 2",
    nameAr: "مؤشر الغطاء النباتي المحسن 2",
    formula: "2.5 × (NIR - Red) / (NIR + 2.4 × Red + 1)",
    description:
      "Optimized to enhance vegetation signal with improved sensitivity in high biomass regions",
    descriptionAr:
      "محسّن لتعزيز إشارة الغطاء النباتي مع حساسية محسنة في مناطق الكتلة الحيوية العالية",
    range: { min: -1, max: 1 },
    optimalRange: { min: 0.4, max: 0.8 },
    reference: "Jiang et al., 2008",
  },
  GNDVI: {
    name: "Green Normalized Difference Vegetation Index",
    nameAr: "مؤشر الاختلاف المعياري الأخضر",
    formula: "(NIR - Green) / (NIR + Green)",
    description: "More sensitive to chlorophyll concentration than NDVI",
    descriptionAr: "أكثر حساسية لتركيز الكلوروفيل من NDVI",
    range: { min: -1, max: 1 },
    optimalRange: { min: 0.5, max: 0.85 },
    reference: "Gitelson et al., 1996",
  },
  SAVI: {
    name: "Soil Adjusted Vegetation Index",
    nameAr: "مؤشر الغطاء النباتي المعدل للتربة",
    formula: "((NIR - Red) × (1 + L)) / (NIR + Red + L)",
    description:
      "Minimizes soil brightness influences using a soil brightness correction factor (L=0.5)",
    descriptionAr:
      "يقلل من تأثيرات سطوع التربة باستخدام معامل تصحيح سطوع التربة",
    range: { min: -1, max: 1 },
    optimalRange: { min: 0.4, max: 0.7 },
    reference: "Huete, 1988",
  },
  MSAVI: {
    name: "Modified Soil Adjusted Vegetation Index",
    nameAr: "مؤشر الغطاء النباتي المعدل للتربة المحسّن",
    formula: "(2 × NIR + 1 - √((2 × NIR + 1)² - 8 × (NIR - Red))) / 2",
    description:
      "Self-adjusting soil factor to minimize soil background effects",
    descriptionAr: "معامل تربة ذاتي التعديل لتقليل تأثيرات خلفية التربة",
    range: { min: 0, max: 1 },
    optimalRange: { min: 0.3, max: 0.7 },
    reference: "Qi et al., 1994",
  },
  NDRE: {
    name: "Normalized Difference Red Edge",
    nameAr: "الاختلاف المعياري للحافة الحمراء",
    formula: "(NIR - RedEdge) / (NIR + RedEdge)",
    description:
      "Sensitive to chlorophyll content in moderately vegetated areas",
    descriptionAr:
      "حساس لمحتوى الكلوروفيل في المناطق ذات الغطاء النباتي المتوسط",
    range: { min: -1, max: 1 },
    optimalRange: { min: 0.2, max: 0.6 },
    reference: "Barnes et al., 2000",
  },
  CIgreen: {
    name: "Chlorophyll Index Green",
    nameAr: "مؤشر الكلوروفيل الأخضر",
    formula: "(NIR / Green) - 1",
    description: "Estimates chlorophyll content using green band",
    descriptionAr: "يقدر محتوى الكلوروفيل باستخدام النطاق الأخضر",
    range: { min: 0, max: 15 },
    optimalRange: { min: 3, max: 10 },
    reference: "Gitelson et al., 2003",
  },
  CIrededge: {
    name: "Chlorophyll Index Red Edge",
    nameAr: "مؤشر الكلوروفيل للحافة الحمراء",
    formula: "(NIR / RedEdge) - 1",
    description: "Estimates chlorophyll content using red edge band",
    descriptionAr: "يقدر محتوى الكلوروفيل باستخدام نطاق الحافة الحمراء",
    range: { min: 0, max: 10 },
    optimalRange: { min: 1, max: 5 },
    reference: "Gitelson et al., 2003",
  },
  MTVI2: {
    name: "Modified Triangular Vegetation Index 2",
    nameAr: "مؤشر الغطاء النباتي المثلثي المعدل 2",
    formula:
      "1.5 × (1.2 × (NIR - Green) - 2.5 × (Red - Green)) / √((2 × NIR + 1)² - (6 × NIR - 5 × √Red) - 0.5)",
    description:
      "Optimized LAI estimation index with reduced soil background sensitivity",
    descriptionAr: "مؤشر محسن لتقدير LAI مع تقليل حساسية خلفية التربة",
    range: { min: 0, max: 1 },
    optimalRange: { min: 0.3, max: 0.7 },
    reference: "Haboudane et al., 2004",
  },
};

@Injectable()
export class VegetationIndicesService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate All Indices
  // حساب جميع المؤشرات
  // ─────────────────────────────────────────────────────────────────────────────

  calculateAllIndices(bands: {
    green: number;
    red: number;
    redEdge: number;
    nir: number;
    blue?: number;
    swir?: number;
  }): Record<string, { value: number; status: string; statusAr: string }> {
    const { green, red, redEdge, nir } = bands;

    const indices: Record<
      string,
      { value: number; status: string; statusAr: string }
    > = {};

    // NDVI
    const ndvi = (nir - red) / (nir + red + 0.0001);
    indices.NDVI = {
      value: this.round(ndvi),
      ...this.getStatus("NDVI", ndvi),
    };

    // EVI2
    const evi2 = 2.5 * ((nir - red) / (nir + 2.4 * red + 1));
    indices.EVI2 = {
      value: this.round(evi2),
      ...this.getStatus("EVI2", evi2),
    };

    // GNDVI
    const gndvi = (nir - green) / (nir + green + 0.0001);
    indices.GNDVI = {
      value: this.round(gndvi),
      ...this.getStatus("GNDVI", gndvi),
    };

    // SAVI (L=0.5)
    const L = 0.5;
    const savi = ((nir - red) * (1 + L)) / (nir + red + L);
    indices.SAVI = {
      value: this.round(savi),
      ...this.getStatus("SAVI", savi),
    };

    // MSAVI
    const msavi =
      (2 * nir + 1 - Math.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red))) / 2;
    indices.MSAVI = {
      value: this.round(msavi),
      ...this.getStatus("MSAVI", msavi),
    };

    // NDRE
    const ndre = (nir - redEdge) / (nir + redEdge + 0.0001);
    indices.NDRE = {
      value: this.round(ndre),
      ...this.getStatus("NDRE", ndre),
    };

    // CIgreen
    const cigreen = nir / (green + 0.0001) - 1;
    indices.CIgreen = {
      value: this.round(cigreen),
      ...this.getStatus("CIgreen", cigreen),
    };

    // CIrededge
    const cirededge = nir / (redEdge + 0.0001) - 1;
    indices.CIrededge = {
      value: this.round(cirededge),
      ...this.getStatus("CIrededge", cirededge),
    };

    // MTVI2
    const mtvi2Num = 1.5 * (1.2 * (nir - green) - 2.5 * (red - green));
    const mtvi2Den = Math.sqrt(
      (2 * nir + 1) ** 2 - (6 * nir - 5 * Math.sqrt(Math.max(0, red))) - 0.5,
    );
    const mtvi2 = mtvi2Den > 0 ? mtvi2Num / mtvi2Den : 0;
    indices.MTVI2 = {
      value: this.round(mtvi2),
      ...this.getStatus("MTVI2", mtvi2),
    };

    return indices;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculate Single Index
  // حساب مؤشر واحد
  // ─────────────────────────────────────────────────────────────────────────────

  calculateIndex(
    indexName: string,
    bands: { green: number; red: number; redEdge: number; nir: number },
  ): {
    value: number;
    status: string;
    statusAr: string;
    info: IndexInfo;
  } | null {
    const allIndices = this.calculateAllIndices(bands);
    const upperName = indexName.toUpperCase();

    if (allIndices[upperName]) {
      return {
        ...allIndices[upperName],
        info: VEGETATION_INDICES[upperName],
      };
    }

    return null;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Index Information
  // الحصول على معلومات المؤشر
  // ─────────────────────────────────────────────────────────────────────────────

  getIndexInfo(
    indexName?: string,
  ): IndexInfo | Record<string, IndexInfo> | null {
    if (indexName) {
      return VEGETATION_INDICES[indexName.toUpperCase()] || null;
    }
    return VEGETATION_INDICES;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Available Indices
  // الحصول على المؤشرات المتاحة
  // ─────────────────────────────────────────────────────────────────────────────

  getAvailableIndices(): Array<{ id: string; name: string; nameAr: string }> {
    return Object.entries(VEGETATION_INDICES).map(([id, info]) => ({
      id,
      name: info.name,
      nameAr: info.nameAr,
    }));
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Analyze Vegetation Health
  // تحليل صحة الغطاء النباتي
  // ─────────────────────────────────────────────────────────────────────────────

  analyzeVegetationHealth(bands: {
    green: number;
    red: number;
    redEdge: number;
    nir: number;
  }): {
    overallHealth: number;
    overallHealthAr: string;
    category: string;
    categoryAr: string;
    indices: Record<string, number>;
    recommendations: string[];
    recommendationsAr: string[];
  } {
    const indices = this.calculateAllIndices(bands);

    // Weight indices for overall health score
    const weights = {
      NDVI: 0.3,
      EVI2: 0.25,
      GNDVI: 0.2,
      SAVI: 0.15,
      NDRE: 0.1,
    };

    let weightedSum = 0;
    let totalWeight = 0;

    for (const [key, weight] of Object.entries(weights)) {
      if (indices[key]) {
        // Normalize to 0-100 scale
        const indexInfo = VEGETATION_INDICES[key];
        const normalized =
          ((indices[key].value - indexInfo.range.min) /
            (indexInfo.range.max - indexInfo.range.min)) *
          100;
        weightedSum += normalized * weight;
        totalWeight += weight;
      }
    }

    const overallHealth = Math.round(weightedSum / totalWeight);

    let category: string;
    let categoryAr: string;
    const recommendations: string[] = [];
    const recommendationsAr: string[] = [];

    if (overallHealth >= 80) {
      category = "Excellent";
      categoryAr = "ممتاز";
      recommendations.push(
        "Vegetation is in excellent condition. Maintain current practices.",
      );
      recommendationsAr.push(
        "الغطاء النباتي في حالة ممتازة. استمر في الممارسات الحالية.",
      );
    } else if (overallHealth >= 60) {
      category = "Good";
      categoryAr = "جيد";
      recommendations.push(
        "Vegetation health is good. Monitor for any changes.",
      );
      recommendationsAr.push("صحة الغطاء النباتي جيدة. راقب أي تغييرات.");
    } else if (overallHealth >= 40) {
      category = "Moderate";
      categoryAr = "متوسط";
      recommendations.push(
        "Vegetation shows moderate stress. Consider irrigation or fertilization.",
      );
      recommendationsAr.push(
        "يظهر الغطاء النباتي إجهادًا متوسطًا. فكر في الري أو التسميد.",
      );
    } else if (overallHealth >= 20) {
      category = "Poor";
      categoryAr = "ضعيف";
      recommendations.push(
        "Vegetation is stressed. Immediate intervention recommended.",
      );
      recommendationsAr.push("الغطاء النباتي متأثر. يُنصح بالتدخل الفوري.");
    } else {
      category = "Critical";
      categoryAr = "حرج";
      recommendations.push(
        "Vegetation is in critical condition. Urgent action required.",
      );
      recommendationsAr.push("الغطاء النباتي في حالة حرجة. يتطلب إجراء عاجل.");
    }

    // Add specific recommendations based on index values
    if (indices.NDVI && indices.NDVI.value < 0.4) {
      recommendations.push(
        "Low NDVI suggests sparse vegetation or poor health.",
      );
      recommendationsAr.push(
        "انخفاض NDVI يشير إلى غطاء نباتي متفرق أو صحة ضعيفة.",
      );
    }

    if (indices.GNDVI && indices.GNDVI.value < 0.3) {
      recommendations.push(
        "Low GNDVI indicates potential chlorophyll deficiency.",
      );
      recommendationsAr.push("انخفاض GNDVI يشير إلى نقص محتمل في الكلوروفيل.");
    }

    return {
      overallHealth,
      overallHealthAr: `${overallHealth}%`,
      category,
      categoryAr,
      indices: Object.fromEntries(
        Object.entries(indices).map(([k, v]) => [k, v.value]),
      ),
      recommendations,
      recommendationsAr,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helper Methods
  // ─────────────────────────────────────────────────────────────────────────────

  private getStatus(
    indexName: string,
    value: number,
  ): { status: string; statusAr: string } {
    const info = VEGETATION_INDICES[indexName];
    if (!info) {
      return { status: "unknown", statusAr: "غير معروف" };
    }

    const { optimalRange } = info;

    if (value >= optimalRange.min && value <= optimalRange.max) {
      return { status: "optimal", statusAr: "مثالي" };
    } else if (value < optimalRange.min) {
      return { status: "below_optimal", statusAr: "أقل من المثالي" };
    } else {
      return { status: "above_optimal", statusAr: "أعلى من المثالي" };
    }
  }

  private round(value: number, decimals: number = 4): number {
    const factor = Math.pow(10, decimals);
    return Math.round(value * factor) / factor;
  }
}
