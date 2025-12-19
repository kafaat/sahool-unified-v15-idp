// ═══════════════════════════════════════════════════════════════════════════════
// Photosynthesis Service - خدمة التمثيل الضوئي
// Based on Farquhar-von Caemmerer-Berry (FvCB) Model and Light Use Efficiency
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from '@nestjs/common';

// ─────────────────────────────────────────────────────────────────────────────
// Constants and Parameters
// الثوابت والمعاملات
// ─────────────────────────────────────────────────────────────────────────────

export interface PhotosynthesisParams {
  nameAr: string;
  nameEn: string;
  pathway: 'C3' | 'C4' | 'CAM';
  LUE: number;                  // Light Use Efficiency (g MJ⁻¹)
  Vcmax25: number;              // Max Rubisco carboxylation rate at 25°C (μmol m⁻² s⁻¹)
  Jmax25: number;               // Max electron transport rate at 25°C (μmol m⁻² s⁻¹)
  Rd25: number;                 // Dark respiration at 25°C (μmol m⁻² s⁻¹)
  Kc25: number;                 // Michaelis-Menten constant for CO2 (μmol mol⁻¹)
  Ko25: number;                 // Michaelis-Menten constant for O2 (mmol mol⁻¹)
  gammastar25: number;          // CO2 compensation point (μmol mol⁻¹)
  optimalTemp: number;          // Optimal temperature for photosynthesis (°C)
  tempMin: number;              // Minimum temperature for photosynthesis (°C)
  tempMax: number;              // Maximum temperature for photosynthesis (°C)
}

const CROP_PHOTOSYNTHESIS: Record<string, PhotosynthesisParams> = {
  WHEAT: {
    nameAr: 'القمح',
    nameEn: 'Wheat',
    pathway: 'C3',
    LUE: 2.8,
    Vcmax25: 120,
    Jmax25: 180,
    Rd25: 1.5,
    Kc25: 404,
    Ko25: 278,
    gammastar25: 42.75,
    optimalTemp: 22,
    tempMin: 4,
    tempMax: 35,
  },
  RICE: {
    nameAr: 'الأرز',
    nameEn: 'Rice',
    pathway: 'C3',
    LUE: 2.5,
    Vcmax25: 110,
    Jmax25: 165,
    Rd25: 1.4,
    Kc25: 404,
    Ko25: 278,
    gammastar25: 42.75,
    optimalTemp: 28,
    tempMin: 15,
    tempMax: 40,
  },
  CORN: {
    nameAr: 'الذرة',
    nameEn: 'Corn/Maize',
    pathway: 'C4',
    LUE: 3.8,
    Vcmax25: 50,
    Jmax25: 120,
    Rd25: 0.8,
    Kc25: 650,
    Ko25: 450,
    gammastar25: 5,
    optimalTemp: 32,
    tempMin: 10,
    tempMax: 42,
  },
  SOYBEAN: {
    nameAr: 'فول الصويا',
    nameEn: 'Soybean',
    pathway: 'C3',
    LUE: 2.4,
    Vcmax25: 100,
    Jmax25: 150,
    Rd25: 1.2,
    Kc25: 404,
    Ko25: 278,
    gammastar25: 42.75,
    optimalTemp: 28,
    tempMin: 10,
    tempMax: 38,
  },
  SUGARCANE: {
    nameAr: 'قصب السكر',
    nameEn: 'Sugarcane',
    pathway: 'C4',
    LUE: 4.2,
    Vcmax25: 55,
    Jmax25: 130,
    Rd25: 0.9,
    Kc25: 650,
    Ko25: 450,
    gammastar25: 5,
    optimalTemp: 32,
    tempMin: 15,
    tempMax: 45,
  },
  COFFEE: {
    nameAr: 'البن',
    nameEn: 'Coffee',
    pathway: 'C3',
    LUE: 2.0,
    Vcmax25: 80,
    Jmax25: 120,
    Rd25: 1.0,
    Kc25: 404,
    Ko25: 278,
    gammastar25: 42.75,
    optimalTemp: 23,
    tempMin: 10,
    tempMax: 32,
  },
};

@Injectable()
export class PhotosynthesisService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Light Use Efficiency (LUE) Model
  // نموذج كفاءة استخدام الضوء
  // ─────────────────────────────────────────────────────────────────────────────

  calculateGrossPrimaryProduction(
    par: number,            // Photosynthetically Active Radiation (MJ m⁻² day⁻¹)
    fpar: number,           // Fraction of PAR absorbed (0-1)
    cropType: string,
    temperature?: number,
  ): {
    gpp: number;
    unit: string;
    efficiency: number;
    temperatureScalar: number;
  } {
    const params = CROP_PHOTOSYNTHESIS[cropType] || CROP_PHOTOSYNTHESIS.WHEAT;

    // Temperature scalar (reduce LUE outside optimal range)
    let tempScalar = 1.0;
    if (temperature !== undefined) {
      tempScalar = this.calculateTemperatureScalar(
        temperature,
        params.optimalTemp,
        params.tempMin,
        params.tempMax,
      );
    }

    // GPP = PAR × fPAR × LUE × temperature_scalar
    const effectiveLUE = params.LUE * tempScalar;
    const gpp = par * fpar * effectiveLUE;

    return {
      gpp: Math.round(gpp * 100) / 100,
      unit: 'g C m⁻² day⁻¹',
      efficiency: effectiveLUE,
      temperatureScalar: Math.round(tempScalar * 100) / 100,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Temperature Response Function
  // دالة استجابة درجة الحرارة
  // ─────────────────────────────────────────────────────────────────────────────

  calculateTemperatureScalar(
    temp: number,
    optTemp: number,
    minTemp: number,
    maxTemp: number,
  ): number {
    if (temp <= minTemp || temp >= maxTemp) {
      return 0;
    }

    // Beta function for temperature response
    const alpha = Math.log(2) / Math.log((maxTemp - minTemp) / (optTemp - minTemp));
    const scalar =
      (2 * Math.pow(temp - minTemp, alpha) * Math.pow(optTemp - minTemp, alpha) -
        Math.pow(temp - minTemp, 2 * alpha)) /
      Math.pow(optTemp - minTemp, 2 * alpha);

    return Math.max(0, Math.min(1, scalar));
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Simplified Farquhar Model - Rubisco Limited
  // نموذج فاركوار المبسط - محدود بـ Rubisco
  // ─────────────────────────────────────────────────────────────────────────────

  calculateRubiscoLimited(
    ci: number,            // Intercellular CO2 concentration (μmol mol⁻¹)
    cropType: string,
    temperature: number = 25,
  ): {
    Ac: number;
    unit: string;
    description: string;
  } {
    const params = CROP_PHOTOSYNTHESIS[cropType] || CROP_PHOTOSYNTHESIS.WHEAT;

    // Temperature adjustment for Vcmax
    const Vcmax = params.Vcmax25 * this.temperatureAdjustment(temperature, 25, 65.33);

    // Temperature adjustment for Kc and Ko
    const Kc = params.Kc25 * this.temperatureAdjustment(temperature, 25, 79.43);
    const Ko = params.Ko25 * this.temperatureAdjustment(temperature, 25, 36.38);

    // Temperature adjustment for Gamma*
    const gammastar = params.gammastar25 * this.temperatureAdjustment(temperature, 25, 37.83);

    // O2 partial pressure (mmol mol⁻¹)
    const O = 210;

    // Rubisco-limited rate
    const Ac = Vcmax * (ci - gammastar) / (ci + Kc * (1 + O / Ko));

    return {
      Ac: Math.round(Math.max(0, Ac) * 100) / 100,
      unit: 'μmol CO₂ m⁻² s⁻¹',
      description: 'Rubisco-limited photosynthesis rate (Ac)',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Simplified Farquhar Model - RuBP Limited (Light Limited)
  // نموذج فاركوار المبسط - محدود بـ RuBP (الضوء)
  // ─────────────────────────────────────────────────────────────────────────────

  calculateLightLimited(
    ci: number,            // Intercellular CO2 concentration (μmol mol⁻¹)
    par: number,           // PAR (μmol m⁻² s⁻¹)
    cropType: string,
    temperature: number = 25,
  ): {
    Aj: number;
    unit: string;
    description: string;
  } {
    const params = CROP_PHOTOSYNTHESIS[cropType] || CROP_PHOTOSYNTHESIS.WHEAT;

    // Temperature adjustment for Jmax
    const Jmax = params.Jmax25 * this.temperatureAdjustment(temperature, 25, 43.9);

    // Temperature adjustment for Gamma*
    const gammastar = params.gammastar25 * this.temperatureAdjustment(temperature, 25, 37.83);

    // Quantum yield of electron transport
    const phi = params.pathway === 'C4' ? 0.06 : 0.385;

    // Electron transport rate (rectangular hyperbola)
    const theta = 0.7;  // Curvature parameter
    const J = (phi * par + Jmax - Math.sqrt(Math.pow(phi * par + Jmax, 2) - 4 * theta * phi * par * Jmax)) / (2 * theta);

    // RuBP-limited rate
    const Aj = J * (ci - gammastar) / (4 * ci + 8 * gammastar);

    return {
      Aj: Math.round(Math.max(0, Aj) * 100) / 100,
      unit: 'μmol CO₂ m⁻² s⁻¹',
      description: 'RuBP/Light-limited photosynthesis rate (Aj)',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Net Photosynthesis Rate
  // معدل التمثيل الضوئي الصافي
  // ─────────────────────────────────────────────────────────────────────────────

  calculateNetPhotosynthesis(
    ci: number,            // Intercellular CO2 concentration (μmol mol⁻¹)
    par: number,           // PAR (μmol m⁻² s⁻¹)
    cropType: string,
    temperature: number = 25,
  ): {
    An: number;
    Ac: number;
    Aj: number;
    Rd: number;
    limitingFactor: string;
    limitingFactorAr: string;
    unit: string;
  } {
    const params = CROP_PHOTOSYNTHESIS[cropType] || CROP_PHOTOSYNTHESIS.WHEAT;

    const { Ac } = this.calculateRubiscoLimited(ci, cropType, temperature);
    const { Aj } = this.calculateLightLimited(ci, par, cropType, temperature);

    // Dark respiration (temperature adjusted)
    const Rd = params.Rd25 * this.temperatureAdjustment(temperature, 25, 46.39);

    // Net photosynthesis (minimum of Ac and Aj minus respiration)
    const grossA = Math.min(Ac, Aj);
    const An = grossA - Rd;

    // Determine limiting factor
    const isRubiscoLimited = Ac < Aj;

    return {
      An: Math.round(Math.max(0, An) * 100) / 100,
      Ac: Math.round(Ac * 100) / 100,
      Aj: Math.round(Aj * 100) / 100,
      Rd: Math.round(Rd * 100) / 100,
      limitingFactor: isRubiscoLimited ? 'Rubisco (Ac)' : 'RuBP/Light (Aj)',
      limitingFactorAr: isRubiscoLimited ? 'روبيسكو (Ac)' : 'الضوء/RuBP (Aj)',
      unit: 'μmol CO₂ m⁻² s⁻¹',
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Light Response Curve
  // منحنى استجابة الضوء
  // ─────────────────────────────────────────────────────────────────────────────

  generateLightResponseCurve(
    cropType: string,
    ci: number = 400,
    temperature: number = 25,
  ): Array<{
    par: number;
    An: number;
  }> {
    const parValues = [0, 50, 100, 200, 400, 600, 800, 1000, 1200, 1500, 1800, 2000];

    return parValues.map((par) => {
      const { An } = this.calculateNetPhotosynthesis(ci, par, cropType, temperature);
      return { par, An };
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // CO2 Response Curve (A-Ci Curve)
  // منحنى استجابة ثاني أكسيد الكربون
  // ─────────────────────────────────────────────────────────────────────────────

  generateCO2ResponseCurve(
    cropType: string,
    par: number = 1500,
    temperature: number = 25,
  ): Array<{
    ci: number;
    An: number;
    limitingFactor: string;
  }> {
    const ciValues = [50, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1200];

    return ciValues.map((ci) => {
      const result = this.calculateNetPhotosynthesis(ci, par, cropType, temperature);
      return {
        ci,
        An: result.An,
        limitingFactor: result.limitingFactor,
      };
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Temperature Response Curve
  // منحنى استجابة درجة الحرارة
  // ─────────────────────────────────────────────────────────────────────────────

  generateTemperatureResponseCurve(
    cropType: string,
    par: number = 1500,
    ci: number = 400,
  ): Array<{
    temperature: number;
    An: number;
    temperatureScalar: number;
  }> {
    const temps = [5, 10, 15, 20, 25, 30, 35, 40, 45];
    const params = CROP_PHOTOSYNTHESIS[cropType] || CROP_PHOTOSYNTHESIS.WHEAT;

    return temps.map((temperature) => {
      const { An } = this.calculateNetPhotosynthesis(ci, par, cropType, temperature);
      const temperatureScalar = this.calculateTemperatureScalar(
        temperature,
        params.optimalTemp,
        params.tempMin,
        params.tempMax,
      );
      return {
        temperature,
        An,
        temperatureScalar: Math.round(temperatureScalar * 100) / 100,
      };
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helper: Temperature Adjustment (Arrhenius)
  // مساعد: تعديل درجة الحرارة (أرهينيوس)
  // ─────────────────────────────────────────────────────────────────────────────

  private temperatureAdjustment(
    temp: number,
    refTemp: number,
    activationEnergy: number,
  ): number {
    const R = 8.314; // Gas constant (J mol⁻¹ K⁻¹)
    const tempK = temp + 273.15;
    const refTempK = refTemp + 273.15;

    return Math.exp((activationEnergy * 1000 * (tempK - refTempK)) / (refTempK * R * tempK));
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Crop Photosynthesis Parameters
  // الحصول على معاملات التمثيل الضوئي للمحصول
  // ─────────────────────────────────────────────────────────────────────────────

  getCropParameters(cropType?: string): PhotosynthesisParams | Record<string, PhotosynthesisParams> | null {
    if (cropType) {
      return CROP_PHOTOSYNTHESIS[cropType] || null;
    }
    return CROP_PHOTOSYNTHESIS;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Available Crops
  // الحصول على المحاصيل المتاحة
  // ─────────────────────────────────────────────────────────────────────────────

  getAvailableCrops(): Array<{ id: string; nameEn: string; nameAr: string; pathway: string }> {
    return Object.entries(CROP_PHOTOSYNTHESIS).map(([id, params]) => ({
      id,
      nameEn: params.nameEn,
      nameAr: params.nameAr,
      pathway: params.pathway,
    }));
  }
}
