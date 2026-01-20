/**
 * Weather Service Tests for SAHOOL Platform
 *
 * Tests validate weather data processing, risk assessment, and agricultural calculations.
 */

import { Test, TestingModule } from '@nestjs/testing';

// Mock interfaces for testing
interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  precipitation: number;
  pressure?: number;
}

interface RiskAssessment {
  level: 'low' | 'medium' | 'high' | 'critical';
  score: number;
  message: string;
  messageAr: string;
}

// Weather service mock implementation
class WeatherService {
  assessHeatStressRisk(temperatureC: number): RiskAssessment {
    if (temperatureC >= 45) {
      return {
        level: 'critical',
        score: 100,
        message: 'Critical heat stress - immediate action required',
        messageAr: 'إجهاد حراري حرج - يتطلب إجراء فوري',
      };
    } else if (temperatureC >= 42) {
      return {
        level: 'high',
        score: 80,
        message: 'High heat stress risk',
        messageAr: 'خطر إجهاد حراري مرتفع',
      };
    } else if (temperatureC >= 38) {
      return {
        level: 'medium',
        score: 50,
        message: 'Moderate heat stress risk',
        messageAr: 'خطر إجهاد حراري متوسط',
      };
    } else if (temperatureC >= 35) {
      return {
        level: 'low',
        score: 25,
        message: 'Low heat stress risk',
        messageAr: 'خطر إجهاد حراري منخفض',
      };
    }
    return {
      level: 'low',
      score: 0,
      message: 'No heat stress risk',
      messageAr: 'لا يوجد خطر إجهاد حراري',
    };
  }

  assessFrostRisk(temperatureC: number): RiskAssessment {
    if (temperatureC <= 0) {
      return {
        level: 'critical',
        score: 100,
        message: 'Frost conditions - crop damage likely',
        messageAr: 'ظروف صقيع - تلف المحاصيل محتمل',
      };
    } else if (temperatureC <= 2) {
      return {
        level: 'high',
        score: 80,
        message: 'High frost risk',
        messageAr: 'خطر صقيع مرتفع',
      };
    } else if (temperatureC <= 5) {
      return {
        level: 'medium',
        score: 50,
        message: 'Moderate frost risk',
        messageAr: 'خطر صقيع متوسط',
      };
    }
    return {
      level: 'low',
      score: 0,
      message: 'No frost risk',
      messageAr: 'لا يوجد خطر صقيع',
    };
  }

  assessWindRisk(windSpeedKmh: number): RiskAssessment {
    if (windSpeedKmh >= 60) {
      return {
        level: 'critical',
        score: 100,
        message: 'Dangerous wind conditions',
        messageAr: 'ظروف رياح خطيرة',
      };
    } else if (windSpeedKmh >= 40) {
      return {
        level: 'high',
        score: 70,
        message: 'High wind risk - avoid spraying',
        messageAr: 'خطر رياح مرتفع - تجنب الرش',
      };
    } else if (windSpeedKmh >= 25) {
      return {
        level: 'medium',
        score: 40,
        message: 'Moderate wind - caution with spraying',
        messageAr: 'رياح متوسطة - احذر عند الرش',
      };
    }
    return {
      level: 'low',
      score: 0,
      message: 'Wind conditions suitable',
      messageAr: 'ظروف الرياح مناسبة',
    };
  }

  assessDiseaseRisk(temperatureC: number, humidityPercent: number): RiskAssessment {
    // Fungal disease risk increases with high humidity and moderate temperatures
    const isHighHumidity = humidityPercent >= 80;
    const isFavorableTemp = temperatureC >= 15 && temperatureC <= 30;

    if (isHighHumidity && isFavorableTemp) {
      return {
        level: 'high',
        score: 85,
        message: 'High fungal disease risk - monitor crops',
        messageAr: 'خطر مرض فطري مرتفع - راقب المحاصيل',
      };
    } else if (humidityPercent >= 70 && isFavorableTemp) {
      return {
        level: 'medium',
        score: 50,
        message: 'Moderate disease risk',
        messageAr: 'خطر مرض متوسط',
      };
    }
    return {
      level: 'low',
      score: 10,
      message: 'Low disease risk',
      messageAr: 'خطر مرض منخفض',
    };
  }

  calculateEvapotranspiration(
    temperatureC: number,
    humidityPercent: number,
    windSpeedMs: number,
    solarRadiation: number
  ): number {
    // Simplified Penman-Monteith equation approximation
    const delta = 4098 * (0.6108 * Math.exp((17.27 * temperatureC) / (temperatureC + 237.3))) /
                  Math.pow(temperatureC + 237.3, 2);
    const gamma = 0.665 * 0.001 * 101.3; // Psychrometric constant

    // Simplified ET0 calculation (mm/day)
    const et0 = (0.408 * delta * solarRadiation + gamma * (900 / (temperatureC + 273)) *
                windSpeedMs * (1 - humidityPercent / 100)) / (delta + gamma * (1 + 0.34 * windSpeedMs));

    return Math.max(0, Math.round(et0 * 100) / 100);
  }

  calculateGrowingDegreeDays(
    maxTemp: number,
    minTemp: number,
    baseTemp: number = 10
  ): number {
    const avgTemp = (maxTemp + minTemp) / 2;
    const gdd = Math.max(0, avgTemp - baseTemp);
    return Math.round(gdd * 10) / 10;
  }

  calculateIrrigationAdjustment(
    et0: number,
    precipitation: number,
    soilMoisture: number
  ): { adjustment: number; recommendation: string; recommendationAr: string } {
    const cropWaterNeed = et0 * 1.2; // Crop coefficient assumed as 1.2
    const effectivePrecipitation = precipitation * 0.8;
    const netIrrigation = cropWaterNeed - effectivePrecipitation;

    let adjustment = 0;
    let recommendation = '';
    let recommendationAr = '';

    if (soilMoisture < 30) {
      adjustment = netIrrigation * 1.3;
      recommendation = 'Increase irrigation - soil moisture critical';
      recommendationAr = 'زيادة الري - رطوبة التربة حرجة';
    } else if (soilMoisture < 50) {
      adjustment = netIrrigation;
      recommendation = 'Normal irrigation recommended';
      recommendationAr = 'الري الطبيعي موصى به';
    } else if (soilMoisture < 70) {
      adjustment = netIrrigation * 0.7;
      recommendation = 'Reduce irrigation slightly';
      recommendationAr = 'تقليل الري قليلاً';
    } else {
      adjustment = 0;
      recommendation = 'Skip irrigation - sufficient moisture';
      recommendationAr = 'تخطي الري - رطوبة كافية';
    }

    return {
      adjustment: Math.max(0, Math.round(adjustment * 10) / 10),
      recommendation,
      recommendationAr,
    };
  }

  isSprayWindowSuitable(weather: WeatherData): {
    suitable: boolean;
    reasons: string[];
    reasonsAr: string[];
  } {
    const reasons: string[] = [];
    const reasonsAr: string[] = [];

    if (weather.windSpeed > 15) {
      reasons.push('Wind speed too high for spraying');
      reasonsAr.push('سرعة الرياح مرتفعة للرش');
    }

    if (weather.temperature > 35) {
      reasons.push('Temperature too high - evaporation risk');
      reasonsAr.push('درجة الحرارة مرتفعة - خطر التبخر');
    }

    if (weather.humidity < 40) {
      reasons.push('Humidity too low - poor absorption');
      reasonsAr.push('الرطوبة منخفضة - امتصاص ضعيف');
    }

    if (weather.precipitation > 0) {
      reasons.push('Rain expected - chemicals may wash off');
      reasonsAr.push('أمطار متوقعة - المواد الكيميائية قد تُغسل');
    }

    return {
      suitable: reasons.length === 0,
      reasons,
      reasonsAr,
    };
  }
}

describe('WeatherService', () => {
  let service: WeatherService;

  beforeEach(() => {
    service = new WeatherService();
  });

  describe('Heat Stress Assessment', () => {
    it('should return critical risk for temperatures >= 45°C', () => {
      const result = service.assessHeatStressRisk(45);

      expect(result.level).toBe('critical');
      expect(result.score).toBe(100);
      expect(result.messageAr).toContain('حرج');
    });

    it('should return high risk for temperatures >= 42°C', () => {
      const result = service.assessHeatStressRisk(43);

      expect(result.level).toBe('high');
      expect(result.score).toBe(80);
    });

    it('should return medium risk for temperatures >= 38°C', () => {
      const result = service.assessHeatStressRisk(39);

      expect(result.level).toBe('medium');
      expect(result.score).toBe(50);
    });

    it('should return low risk for temperatures >= 35°C', () => {
      const result = service.assessHeatStressRisk(36);

      expect(result.level).toBe('low');
      expect(result.score).toBe(25);
    });

    it('should return no risk for temperatures < 35°C', () => {
      const result = service.assessHeatStressRisk(30);

      expect(result.level).toBe('low');
      expect(result.score).toBe(0);
    });
  });

  describe('Frost Risk Assessment', () => {
    it('should return critical risk for temperatures <= 0°C', () => {
      const result = service.assessFrostRisk(-2);

      expect(result.level).toBe('critical');
      expect(result.score).toBe(100);
      expect(result.messageAr).toContain('صقيع');
    });

    it('should return high risk for temperatures <= 2°C', () => {
      const result = service.assessFrostRisk(1);

      expect(result.level).toBe('high');
      expect(result.score).toBe(80);
    });

    it('should return medium risk for temperatures <= 5°C', () => {
      const result = service.assessFrostRisk(4);

      expect(result.level).toBe('medium');
      expect(result.score).toBe(50);
    });

    it('should return no risk for temperatures > 5°C', () => {
      const result = service.assessFrostRisk(15);

      expect(result.level).toBe('low');
      expect(result.score).toBe(0);
    });
  });

  describe('Wind Risk Assessment', () => {
    it('should return critical risk for wind >= 60 km/h', () => {
      const result = service.assessWindRisk(65);

      expect(result.level).toBe('critical');
      expect(result.score).toBe(100);
    });

    it('should return high risk for wind >= 40 km/h', () => {
      const result = service.assessWindRisk(45);

      expect(result.level).toBe('high');
      expect(result.messageAr).toContain('تجنب الرش');
    });

    it('should return suitable conditions for low wind', () => {
      const result = service.assessWindRisk(10);

      expect(result.level).toBe('low');
      expect(result.message).toContain('suitable');
    });
  });

  describe('Disease Risk Assessment', () => {
    it('should return high risk for high humidity and favorable temperature', () => {
      const result = service.assessDiseaseRisk(22, 85);

      expect(result.level).toBe('high');
      expect(result.score).toBeGreaterThan(80);
    });

    it('should return medium risk for moderate humidity', () => {
      const result = service.assessDiseaseRisk(22, 75);

      expect(result.level).toBe('medium');
    });

    it('should return low risk for unfavorable conditions', () => {
      const result = service.assessDiseaseRisk(5, 40);

      expect(result.level).toBe('low');
    });
  });

  describe('Evapotranspiration Calculation', () => {
    it('should calculate positive ET0 for typical conditions', () => {
      const et0 = service.calculateEvapotranspiration(25, 50, 2, 20);

      expect(et0).toBeGreaterThan(0);
    });

    it('should return non-negative values', () => {
      const et0 = service.calculateEvapotranspiration(10, 90, 0.5, 5);

      expect(et0).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Growing Degree Days', () => {
    it('should calculate GDD correctly', () => {
      const gdd = service.calculateGrowingDegreeDays(30, 20, 10);

      expect(gdd).toBe(15); // (30+20)/2 - 10 = 15
    });

    it('should return 0 for temperatures below base', () => {
      const gdd = service.calculateGrowingDegreeDays(8, 4, 10);

      expect(gdd).toBe(0);
    });

    it('should use default base temperature of 10', () => {
      const gdd = service.calculateGrowingDegreeDays(25, 15);

      expect(gdd).toBe(10); // (25+15)/2 - 10 = 10
    });
  });

  describe('Irrigation Adjustment', () => {
    it('should increase irrigation for low soil moisture', () => {
      const result = service.calculateIrrigationAdjustment(5, 0, 25);

      expect(result.adjustment).toBeGreaterThan(5);
      expect(result.recommendation).toContain('Increase');
    });

    it('should recommend normal irrigation for moderate moisture', () => {
      const result = service.calculateIrrigationAdjustment(5, 0, 45);

      expect(result.recommendation).toContain('Normal');
    });

    it('should skip irrigation for high moisture', () => {
      const result = service.calculateIrrigationAdjustment(5, 0, 75);

      expect(result.adjustment).toBe(0);
      expect(result.recommendation).toContain('Skip');
    });

    it('should account for precipitation', () => {
      const withRain = service.calculateIrrigationAdjustment(5, 10, 45);
      const withoutRain = service.calculateIrrigationAdjustment(5, 0, 45);

      expect(withRain.adjustment).toBeLessThan(withoutRain.adjustment);
    });
  });

  describe('Spray Window Assessment', () => {
    it('should be suitable for ideal conditions', () => {
      const weather: WeatherData = {
        temperature: 25,
        humidity: 60,
        windSpeed: 8,
        precipitation: 0,
      };

      const result = service.isSprayWindowSuitable(weather);

      expect(result.suitable).toBe(true);
      expect(result.reasons).toHaveLength(0);
    });

    it('should be unsuitable for high wind', () => {
      const weather: WeatherData = {
        temperature: 25,
        humidity: 60,
        windSpeed: 20,
        precipitation: 0,
      };

      const result = service.isSprayWindowSuitable(weather);

      expect(result.suitable).toBe(false);
      expect(result.reasons).toContain('Wind speed too high for spraying');
    });

    it('should be unsuitable for high temperature', () => {
      const weather: WeatherData = {
        temperature: 40,
        humidity: 60,
        windSpeed: 8,
        precipitation: 0,
      };

      const result = service.isSprayWindowSuitable(weather);

      expect(result.suitable).toBe(false);
      expect(result.reasons.some(r => r.includes('Temperature'))).toBe(true);
    });

    it('should be unsuitable for expected rain', () => {
      const weather: WeatherData = {
        temperature: 25,
        humidity: 60,
        windSpeed: 8,
        precipitation: 5,
      };

      const result = service.isSprayWindowSuitable(weather);

      expect(result.suitable).toBe(false);
      expect(result.reasons.some(r => r.includes('Rain'))).toBe(true);
    });

    it('should include Arabic translations', () => {
      const weather: WeatherData = {
        temperature: 40,
        humidity: 30,
        windSpeed: 50,
        precipitation: 10,
      };

      const result = service.isSprayWindowSuitable(weather);

      expect(result.reasonsAr.length).toBeGreaterThan(0);
      expect(result.reasonsAr.some(r => /[\u0600-\u06FF]/.test(r))).toBe(true);
    });
  });
});
