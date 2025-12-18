/**
 * Test Fixtures - Research Core
 * بيانات الاختبار - نواة البحث
 */

/**
 * Experiment fixtures
 * بيانات التجارب للاختبار
 */
export const experimentFixtures = {
  active: {
    title: 'Active Test Experiment',
    titleAr: 'تجربة اختبار نشطة',
    description: 'Test experiment for unit tests',
    farmId: 'test-farm-001',
    startDate: '2025-01-01',
    endDate: '2025-12-31',
    status: 'active',
    metadata: {
      cropType: 'wheat',
      variety: 'local',
      season: 'winter',
    },
  },

  draft: {
    title: 'Draft Test Experiment',
    titleAr: 'مسودة تجربة اختبار',
    description: 'Draft experiment',
    farmId: 'test-farm-001',
    startDate: '2025-02-01',
    status: 'draft',
  },

  completed: {
    title: 'Completed Test Experiment',
    titleAr: 'تجربة اختبار مكتملة',
    description: 'Completed experiment',
    farmId: 'test-farm-001',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    status: 'completed',
  },

  locked: {
    title: 'Locked Test Experiment',
    titleAr: 'تجربة اختبار مقفلة',
    description: 'Locked experiment for integrity',
    farmId: 'test-farm-001',
    startDate: '2024-06-01',
    endDate: '2024-11-30',
    status: 'locked',
  },
};

/**
 * Research log fixtures
 * بيانات سجلات البحث للاختبار
 */
export const logFixtures = {
  observation: {
    logDate: '2025-01-15',
    logTime: '09:30',
    category: 'observation',
    title: 'Daily Field Observation',
    titleAr: 'ملاحظة يومية للحقل',
    notes: 'Observed healthy crop growth with good leaf color',
    notesAr: 'لوحظ نمو صحي للمحصول مع لون أوراق جيد',
    measurements: {
      temperature: 25,
      humidity: 65,
      soilMoisture: 40,
      plantHeight: 45,
    },
    weatherConditions: {
      sky: 'clear',
      wind: 'light',
      precipitation: 'none',
    },
  },

  irrigation: {
    logDate: '2025-01-16',
    logTime: '07:00',
    category: 'irrigation',
    title: 'Irrigation Application',
    titleAr: 'تطبيق الري',
    notes: 'Applied drip irrigation for 2 hours',
    measurements: {
      waterAmount: 500,
      duration: 120,
      soilMoistureBefore: 30,
      soilMoistureAfter: 55,
    },
  },

  fertilization: {
    logDate: '2025-01-20',
    logTime: '08:00',
    category: 'fertilization',
    title: 'Fertilizer Application',
    titleAr: 'تطبيق الأسمدة',
    notes: 'Applied NPK fertilizer',
    measurements: {
      fertilizerType: 'NPK',
      amount: 50,
      unit: 'kg/ha',
      method: 'broadcast',
    },
  },

  pestControl: {
    logDate: '2025-01-25',
    logTime: '06:00',
    category: 'pest_control',
    title: 'Pest Control Application',
    titleAr: 'مكافحة الآفات',
    notes: 'Sprayed insecticide for aphid control',
    measurements: {
      pestType: 'aphids',
      treatmentType: 'insecticide',
      concentration: 2.5,
      coverageArea: 100,
    },
  },

  harvest: {
    logDate: '2025-05-15',
    logTime: '10:00',
    category: 'harvest',
    title: 'Harvest Data',
    titleAr: 'بيانات الحصاد',
    notes: 'Final harvest completed',
    measurements: {
      yieldPerHa: 4500,
      moisture: 12,
      quality: 'grade_a',
      totalArea: 2.5,
    },
  },
};

/**
 * Sample fixtures
 * بيانات العينات للاختبار
 */
export const sampleFixtures = {
  soil: {
    sampleCode: 'SOIL-2025-001',
    sampleType: 'soil',
    collectionDate: '2025-01-10',
    collectionTime: '09:00',
    depth: '0-30cm',
    location: { lat: 15.3694, lng: 44.1910 },
    status: 'collected',
  },

  plant: {
    sampleCode: 'PLANT-2025-001',
    sampleType: 'plant_tissue',
    collectionDate: '2025-01-15',
    collectionTime: '10:00',
    plantPart: 'leaf',
    status: 'submitted',
  },

  water: {
    sampleCode: 'WATER-2025-001',
    sampleType: 'water',
    collectionDate: '2025-01-12',
    collectionTime: '08:00',
    source: 'irrigation_well',
    status: 'analyzed',
    results: {
      ph: 7.2,
      ec: 1.5,
      hardness: 150,
    },
  },
};

/**
 * Plot fixtures
 * بيانات القطع للاختبار
 */
export const plotFixtures = {
  control: {
    plotCode: 'P001-CTRL',
    name: 'Control Plot',
    nameAr: 'قطعة التحكم',
    area: 100,
    coordinates: [
      [15.3690, 44.1905],
      [15.3695, 44.1905],
      [15.3695, 44.1910],
      [15.3690, 44.1910],
    ],
    soilType: 'clay_loam',
  },

  treatment1: {
    plotCode: 'P002-T1',
    name: 'Treatment 1 Plot',
    nameAr: 'قطعة المعاملة 1',
    area: 100,
    coordinates: [
      [15.3695, 44.1905],
      [15.3700, 44.1905],
      [15.3700, 44.1910],
      [15.3695, 44.1910],
    ],
    soilType: 'clay_loam',
  },

  treatment2: {
    plotCode: 'P003-T2',
    name: 'Treatment 2 Plot',
    nameAr: 'قطعة المعاملة 2',
    area: 100,
    coordinates: [
      [15.3700, 44.1905],
      [15.3705, 44.1905],
      [15.3705, 44.1910],
      [15.3700, 44.1910],
    ],
    soilType: 'clay_loam',
  },
};

/**
 * Treatment fixtures
 * بيانات المعاملات للاختبار
 */
export const treatmentFixtures = {
  control: {
    treatmentCode: 'T0-CTRL',
    name: 'Control',
    nameAr: 'تحكم',
    description: 'No treatment applied',
    descriptionAr: 'بدون معاملة',
    parameters: {},
  },

  lowDose: {
    treatmentCode: 'T1-LOW',
    name: 'Low Dose Fertilizer',
    nameAr: 'جرعة سماد منخفضة',
    description: 'Low dose NPK application',
    parameters: {
      fertilizerType: 'NPK',
      doseRate: 25,
      unit: 'kg/ha',
    },
  },

  highDose: {
    treatmentCode: 'T2-HIGH',
    name: 'High Dose Fertilizer',
    nameAr: 'جرعة سماد عالية',
    description: 'High dose NPK application',
    parameters: {
      fertilizerType: 'NPK',
      doseRate: 75,
      unit: 'kg/ha',
    },
  },
};

/**
 * User fixtures
 * بيانات المستخدمين للاختبار
 */
export const userFixtures = {
  researcher: {
    id: 'test-researcher-001',
    name: 'Test Researcher',
    email: 'researcher@test.com',
    role: 'researcher',
  },

  fieldWorker: {
    id: 'test-worker-001',
    name: 'Test Field Worker',
    email: 'worker@test.com',
    role: 'field_worker',
  },

  admin: {
    id: 'test-admin-001',
    name: 'Test Admin',
    email: 'admin@test.com',
    role: 'admin',
  },
};

/**
 * Create a complete experiment with related data
 * إنشاء تجربة كاملة مع البيانات المرتبطة
 */
export function createFullExperimentFixture() {
  return {
    experiment: experimentFixtures.active,
    plots: [plotFixtures.control, plotFixtures.treatment1, plotFixtures.treatment2],
    treatments: [treatmentFixtures.control, treatmentFixtures.lowDose, treatmentFixtures.highDose],
    logs: [
      logFixtures.observation,
      logFixtures.irrigation,
      logFixtures.fertilization,
    ],
    samples: [sampleFixtures.soil, sampleFixtures.plant],
  };
}

/**
 * Generate random measurement data
 * توليد بيانات قياس عشوائية
 */
export function generateMeasurements(type: string) {
  const random = (min: number, max: number) =>
    Math.round((Math.random() * (max - min) + min) * 10) / 10;

  switch (type) {
    case 'weather':
      return {
        temperature: random(15, 40),
        humidity: random(20, 90),
        windSpeed: random(0, 30),
        precipitation: random(0, 50),
      };
    case 'soil':
      return {
        moisture: random(10, 60),
        ph: random(5.5, 8.5),
        ec: random(0.5, 3),
        temperature: random(15, 35),
      };
    case 'plant':
      return {
        height: random(10, 150),
        leafCount: Math.round(random(5, 50)),
        chlorophyll: random(30, 60),
        ndvi: random(0.3, 0.9),
      };
    default:
      return {};
  }
}
