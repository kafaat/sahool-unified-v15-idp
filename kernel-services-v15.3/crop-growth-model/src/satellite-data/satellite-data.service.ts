// ═══════════════════════════════════════════════════════════════════════════════
// Satellite Data Selector Service - خدمة اختيار البيانات الساتلية
// Intelligent satellite data source selection for agricultural applications
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable } from '@nestjs/common';

// ─────────────────────────────────────────────────────────────────────────────
// Interfaces - الواجهات
// ─────────────────────────────────────────────────────────────────────────────

interface SatelliteSource {
  id: string;
  nameEn: string;
  nameAr: string;
  provider: string;
  sensor: string;
  spatialResolution: number; // meters
  temporalResolution: number; // days
  spectralBands: string[];
  isFree: boolean;
  dataUrl: string;
  applications: string[];
  advantages: string[];
  limitations: string[];
  launchYear: number;
  status: 'active' | 'decommissioned' | 'limited';
}

interface DataRequirements {
  spatialResolution: 'high' | 'medium' | 'low';
  temporalResolution: 'daily' | 'weekly' | 'biweekly' | 'monthly';
  cloudFree: boolean;
  budget: 'free' | 'commercial' | 'any';
  application: 'lai' | 'ndvi' | 'water' | 'disaster' | 'yield' | 'phenology' | 'soil' | 'thermal';
  region?: string;
}

interface SatelliteRecommendation {
  primary: SatelliteSource;
  alternatives: SatelliteSource[];
  reasoning: string;
  reasoningAr: string;
  combinedApproach?: {
    description: string;
    descriptionAr: string;
    sources: SatelliteSource[];
  };
  processingNotes: string[];
  estimatedDataAvailability: string;
}

interface BandCombination {
  name: string;
  nameAr: string;
  formula: string;
  bands: { [satellite: string]: string[] };
  application: string;
  reference: string;
}

@Injectable()
export class SatelliteDataService {
  // ─────────────────────────────────────────────────────────────────────────────
  // Satellite Database - قاعدة بيانات الأقمار الصناعية
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly satellites: Map<string, SatelliteSource> = new Map([
    // Landsat Series - سلسلة لاندسات
    ['LANDSAT_9', {
      id: 'LANDSAT_9',
      nameEn: 'Landsat 9',
      nameAr: 'لاندسات 9',
      provider: 'NASA/USGS',
      sensor: 'OLI-2/TIRS-2',
      spatialResolution: 30, // 15m pan, 30m MS, 100m thermal
      temporalResolution: 16,
      spectralBands: ['Coastal', 'Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'Pan', 'Cirrus', 'TIR1', 'TIR2'],
      isFree: true,
      dataUrl: 'https://earthexplorer.usgs.gov/',
      applications: ['ndvi', 'lai', 'water', 'thermal', 'yield'],
      advantages: ['مجاني', 'سجل تاريخي طويل', 'نطاقات حرارية'],
      limitations: ['دقة مكانية متوسطة', 'دورة 16 يوم'],
      launchYear: 2021,
      status: 'active',
    }],
    ['LANDSAT_8', {
      id: 'LANDSAT_8',
      nameEn: 'Landsat 8',
      nameAr: 'لاندسات 8',
      provider: 'NASA/USGS',
      sensor: 'OLI/TIRS',
      spatialResolution: 30,
      temporalResolution: 16,
      spectralBands: ['Coastal', 'Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'Pan', 'Cirrus', 'TIR1', 'TIR2'],
      isFree: true,
      dataUrl: 'https://earthexplorer.usgs.gov/',
      applications: ['ndvi', 'lai', 'water', 'thermal', 'yield'],
      advantages: ['مجاني', 'أداء مستقر', 'توافق مع Landsat 9'],
      limitations: ['دقة مكانية متوسطة', 'دورة 16 يوم'],
      launchYear: 2013,
      status: 'active',
    }],

    // Sentinel Series - سلسلة سينتينيل
    ['SENTINEL_2', {
      id: 'SENTINEL_2',
      nameEn: 'Sentinel-2',
      nameAr: 'سينتينيل-2',
      provider: 'ESA',
      sensor: 'MSI',
      spatialResolution: 10, // 10m VIS/NIR, 20m RedEdge/SWIR, 60m atmospheric
      temporalResolution: 5,
      spectralBands: ['B1-Coastal', 'B2-Blue', 'B3-Green', 'B4-Red', 'B5-RedEdge1', 'B6-RedEdge2', 'B7-RedEdge3', 'B8-NIR', 'B8A-NIRn', 'B9-WaterVapor', 'B10-Cirrus', 'B11-SWIR1', 'B12-SWIR2'],
      isFree: true,
      dataUrl: 'https://scihub.copernicus.eu/',
      applications: ['ndvi', 'lai', 'phenology', 'water', 'yield'],
      advantages: ['مجاني', 'دقة عالية 10م', 'نطاقات Red Edge', 'دورة 5 أيام'],
      limitations: ['يحتاج معالجة مسبقة', 'تأثر بالغيوم'],
      launchYear: 2015,
      status: 'active',
    }],
    ['SENTINEL_1', {
      id: 'SENTINEL_1',
      nameEn: 'Sentinel-1 (SAR)',
      nameAr: 'سينتينيل-1 (رادار)',
      provider: 'ESA',
      sensor: 'C-SAR',
      spatialResolution: 5,
      temporalResolution: 12,
      spectralBands: ['VV', 'VH', 'HH', 'HV'],
      isFree: true,
      dataUrl: 'https://scihub.copernicus.eu/',
      applications: ['soil', 'water', 'disaster', 'flood'],
      advantages: ['يعمل في الغيوم والليل', 'رصد رطوبة التربة', 'مجاني'],
      limitations: ['يحتاج خبرة في معالجة SAR', 'تفسير معقد'],
      launchYear: 2014,
      status: 'active',
    }],
    ['SENTINEL_3', {
      id: 'SENTINEL_3',
      nameEn: 'Sentinel-3',
      nameAr: 'سينتينيل-3',
      provider: 'ESA',
      sensor: 'OLCI/SLSTR',
      spatialResolution: 300,
      temporalResolution: 1,
      spectralBands: ['21 OLCI bands', 'SLSTR TIR'],
      isFree: true,
      dataUrl: 'https://scihub.copernicus.eu/',
      applications: ['water', 'thermal', 'yield'],
      advantages: ['تغطية يومية', 'مجاني', 'نطاقات حرارية'],
      limitations: ['دقة مكانية منخفضة'],
      launchYear: 2016,
      status: 'active',
    }],

    // MODIS - موديس
    ['MODIS', {
      id: 'MODIS',
      nameEn: 'MODIS (Terra/Aqua)',
      nameAr: 'موديس (تيرا/أكوا)',
      provider: 'NASA',
      sensor: 'MODIS',
      spatialResolution: 250, // 250m-1km
      temporalResolution: 1,
      spectralBands: ['36 bands (250m-1km)'],
      isFree: true,
      dataUrl: 'https://modis.gsfc.nasa.gov/',
      applications: ['ndvi', 'lai', 'yield', 'phenology', 'thermal'],
      advantages: ['منتجات جاهزة (NDVI, LAI, ET)', 'تغطية يومية', 'مجاني', 'سجل تاريخي من 2000'],
      limitations: ['دقة مكانية منخفضة'],
      launchYear: 2002,
      status: 'active',
    }],

    // Chinese Satellites - الأقمار الصينية
    ['GF_1', {
      id: 'GF_1',
      nameEn: 'Gaofen-1',
      nameAr: 'قاوفن-1',
      provider: 'CNSA',
      sensor: 'PAN/MSI',
      spatialResolution: 2, // 2m pan, 16m MS
      temporalResolution: 4,
      spectralBands: ['Pan', 'Blue', 'Green', 'Red', 'NIR'],
      isFree: false,
      dataUrl: 'http://www.cresda.com/',
      applications: ['ndvi', 'yield', 'phenology'],
      advantages: ['دقة عالية', 'دورة 4 أيام'],
      limitations: ['غير مجاني', 'توفر محدود'],
      launchYear: 2013,
      status: 'active',
    }],
    ['GF_2', {
      id: 'GF_2',
      nameEn: 'Gaofen-2',
      nameAr: 'قاوفن-2',
      provider: 'CNSA',
      sensor: 'PAN/MSI',
      spatialResolution: 0.8,
      temporalResolution: 5,
      spectralBands: ['Pan', 'Blue', 'Green', 'Red', 'NIR'],
      isFree: false,
      dataUrl: 'http://www.cresda.com/',
      applications: ['yield', 'phenology'],
      advantages: ['دقة عالية جداً 0.8م'],
      limitations: ['غير مجاني', 'توفر محدود'],
      launchYear: 2014,
      status: 'active',
    }],

    // Commercial - تجاري
    ['PLANET', {
      id: 'PLANET',
      nameEn: 'Planet (Dove/SuperDove)',
      nameAr: 'بلانيت',
      provider: 'Planet Labs',
      sensor: 'PS2/PSB.SD',
      spatialResolution: 3,
      temporalResolution: 1,
      spectralBands: ['Blue', 'Green', 'Red', 'NIR', 'RedEdge', 'CoastalBlue', 'Green-II', 'Yellow'],
      isFree: false,
      dataUrl: 'https://www.planet.com/',
      applications: ['ndvi', 'lai', 'phenology', 'yield', 'disaster'],
      advantages: ['تغطية يومية عالمية', 'دقة 3م', '8 نطاقات'],
      limitations: ['تجاري مدفوع'],
      launchYear: 2016,
      status: 'active',
    }],
    ['WORLDVIEW', {
      id: 'WORLDVIEW',
      nameEn: 'WorldView-3',
      nameAr: 'وورلدفيو-3',
      provider: 'Maxar',
      sensor: 'WV110',
      spatialResolution: 0.31, // 31cm pan
      temporalResolution: 1,
      spectralBands: ['Pan', '8 MS bands', '8 SWIR bands'],
      isFree: false,
      dataUrl: 'https://www.maxar.com/',
      applications: ['yield', 'phenology', 'disaster'],
      advantages: ['أعلى دقة متاحة تجارياً', '16 نطاق طيفي'],
      limitations: ['مكلف جداً'],
      launchYear: 2014,
      status: 'active',
    }],
  ]);

  // ─────────────────────────────────────────────────────────────────────────────
  // Band Combinations for Agricultural Indices
  // تركيبات النطاقات للمؤشرات الزراعية
  // ─────────────────────────────────────────────────────────────────────────────

  private readonly bandCombinations: BandCombination[] = [
    {
      name: 'NDVI',
      nameAr: 'مؤشر الاختلاف النباتي الطبيعي',
      formula: '(NIR - Red) / (NIR + Red)',
      bands: {
        'SENTINEL_2': ['B8', 'B4'],
        'LANDSAT_8': ['B5', 'B4'],
        'MODIS': ['Band 2', 'Band 1'],
        'PLANET': ['NIR', 'Red'],
      },
      application: 'صحة النبات والكتلة الحيوية',
      reference: 'Rouse et al., 1974',
    },
    {
      name: 'LAI (from NDVI)',
      nameAr: 'مؤشر مساحة الأوراق',
      formula: 'LAI = -ln((NDVI_max - NDVI) / (NDVI_max - NDVI_min)) / k',
      bands: {
        'SENTINEL_2': ['B8', 'B4'],
        'MODIS': ['MOD15A2H product'],
      },
      application: 'تقدير مساحة الأوراق',
      reference: 'Myneni et al., 1997',
    },
    {
      name: 'NDWI',
      nameAr: 'مؤشر الماء',
      formula: '(NIR - SWIR) / (NIR + SWIR)',
      bands: {
        'SENTINEL_2': ['B8', 'B11'],
        'LANDSAT_8': ['B5', 'B6'],
      },
      application: 'محتوى الماء في النبات',
      reference: 'Gao, 1996',
    },
    {
      name: 'EVI',
      nameAr: 'مؤشر النبات المحسن',
      formula: '2.5 × (NIR - Red) / (NIR + 6×Red - 7.5×Blue + 1)',
      bands: {
        'SENTINEL_2': ['B8', 'B4', 'B2'],
        'LANDSAT_8': ['B5', 'B4', 'B2'],
        'MODIS': ['MOD13 product'],
      },
      application: 'صحة النبات (تصحيح الغلاف الجوي)',
      reference: 'Huete et al., 2002',
    },
    {
      name: 'SAVI',
      nameAr: 'مؤشر النبات المعدل للتربة',
      formula: '((NIR - Red) / (NIR + Red + L)) × (1 + L)',
      bands: {
        'SENTINEL_2': ['B8', 'B4'],
        'LANDSAT_8': ['B5', 'B4'],
      },
      application: 'صحة النبات في المناطق الجافة',
      reference: 'Huete, 1988',
    },
    {
      name: 'NDRE',
      nameAr: 'مؤشر الحافة الحمراء',
      formula: '(NIR - RedEdge) / (NIR + RedEdge)',
      bands: {
        'SENTINEL_2': ['B8', 'B5'],
        'PLANET': ['NIR', 'RedEdge'],
      },
      application: 'محتوى الكلوروفيل والنيتروجين',
      reference: 'Gitelson & Merzlyak, 1994',
    },
    {
      name: 'LST',
      nameAr: 'درجة حرارة سطح الأرض',
      formula: 'Planck function inversion from TIR',
      bands: {
        'LANDSAT_8': ['B10', 'B11'],
        'MODIS': ['MOD11 product'],
        'SENTINEL_3': ['SLSTR'],
      },
      application: 'الإجهاد الحراري والري',
      reference: 'Wan & Dozier, 1996',
    },
  ];

  // ─────────────────────────────────────────────────────────────────────────────
  // Select Optimal Data Source - اختيار مصدر البيانات الأمثل
  // ─────────────────────────────────────────────────────────────────────────────

  selectOptimalDataSource(requirements: DataRequirements): SatelliteRecommendation {
    const candidates = this.filterCandidates(requirements);
    const scored = this.scoreCandidates(candidates, requirements);

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);

    const primary = scored[0]?.satellite;
    const alternatives = scored.slice(1, 4).map(s => s.satellite);

    // Generate reasoning
    const reasoning = this.generateReasoning(primary, requirements);
    const reasoningAr = this.generateReasoningAr(primary, requirements);

    // Check if combined approach is beneficial
    const combinedApproach = this.suggestCombinedApproach(requirements, scored);

    return {
      primary,
      alternatives,
      reasoning,
      reasoningAr,
      combinedApproach,
      processingNotes: this.getProcessingNotes(primary, requirements),
      estimatedDataAvailability: this.estimateAvailability(primary, requirements),
    };
  }

  private filterCandidates(requirements: DataRequirements): SatelliteSource[] {
    return Array.from(this.satellites.values()).filter(sat => {
      // Filter by budget
      if (requirements.budget === 'free' && !sat.isFree) return false;

      // Filter by status
      if (sat.status === 'decommissioned') return false;

      // Filter by application
      if (!sat.applications.includes(requirements.application)) return false;

      return true;
    });
  }

  private scoreCandidates(
    candidates: SatelliteSource[],
    requirements: DataRequirements,
  ): { satellite: SatelliteSource; score: number }[] {
    return candidates.map(sat => {
      let score = 0;

      // Spatial resolution score (0-30 points)
      const spatialScore = this.scoreSpatialResolution(sat.spatialResolution, requirements.spatialResolution);
      score += spatialScore;

      // Temporal resolution score (0-30 points)
      const temporalScore = this.scoreTemporalResolution(sat.temporalResolution, requirements.temporalResolution);
      score += temporalScore;

      // Cloud-free capability (0-20 points)
      if (requirements.cloudFree && sat.sensor.includes('SAR')) {
        score += 20; // SAR works through clouds
      } else if (!requirements.cloudFree) {
        score += 10;
      }

      // Free data bonus (0-10 points)
      if (sat.isFree) score += 10;

      // Application match bonus (0-10 points)
      if (sat.applications.includes(requirements.application)) score += 10;

      return { satellite: sat, score };
    });
  }

  private scoreSpatialResolution(resolution: number, requirement: 'high' | 'medium' | 'low'): number {
    switch (requirement) {
      case 'high':
        if (resolution <= 5) return 30;
        if (resolution <= 10) return 25;
        if (resolution <= 30) return 15;
        return 5;
      case 'medium':
        if (resolution >= 10 && resolution <= 30) return 30;
        if (resolution < 10) return 25;
        if (resolution <= 100) return 20;
        return 10;
      case 'low':
        if (resolution >= 100) return 30;
        if (resolution >= 30) return 25;
        return 20;
    }
  }

  private scoreTemporalResolution(resolution: number, requirement: 'daily' | 'weekly' | 'biweekly' | 'monthly'): number {
    switch (requirement) {
      case 'daily':
        if (resolution <= 1) return 30;
        if (resolution <= 3) return 25;
        if (resolution <= 5) return 15;
        return 5;
      case 'weekly':
        if (resolution <= 7) return 30;
        if (resolution <= 10) return 25;
        return 15;
      case 'biweekly':
        if (resolution <= 16) return 30;
        if (resolution <= 20) return 25;
        return 20;
      case 'monthly':
        return 30; // Any resolution works
    }
  }

  private generateReasoning(satellite: SatelliteSource, requirements: DataRequirements): string {
    if (!satellite) return 'No suitable satellite found for the given requirements.';

    return `${satellite.nameEn} is recommended for ${requirements.application} application because it offers ` +
           `${satellite.spatialResolution}m spatial resolution with ${satellite.temporalResolution}-day revisit time. ` +
           `${satellite.isFree ? 'Data is freely available.' : 'Commercial data subscription required.'}`;
  }

  private generateReasoningAr(satellite: SatelliteSource, requirements: DataRequirements): string {
    if (!satellite) return 'لم يتم العثور على قمر صناعي مناسب للمتطلبات المحددة.';

    const appNames: { [key: string]: string } = {
      lai: 'تقدير مؤشر مساحة الأوراق',
      ndvi: 'حساب مؤشر NDVI',
      water: 'رصد المياه',
      disaster: 'تقييم الكوارث',
      yield: 'تقدير الإنتاجية',
      phenology: 'رصد الفينولوجيا',
      soil: 'رصد التربة',
      thermal: 'الرصد الحراري',
    };

    return `يُوصى باستخدام ${satellite.nameAr} لتطبيق ${appNames[requirements.application] || requirements.application} ` +
           `لأنه يوفر دقة مكانية ${satellite.spatialResolution} متر مع دورة زمنية ${satellite.temporalResolution} يوم. ` +
           `${satellite.isFree ? 'البيانات متاحة مجاناً.' : 'يتطلب اشتراك تجاري.'}`;
  }

  private suggestCombinedApproach(
    requirements: DataRequirements,
    scored: { satellite: SatelliteSource; score: number }[],
  ): { description: string; descriptionAr: string; sources: SatelliteSource[] } | undefined {
    // Suggest combining high temporal with high spatial
    if (requirements.temporalResolution === 'daily' && requirements.spatialResolution === 'high') {
      const modis = this.satellites.get('MODIS');
      const sentinel2 = this.satellites.get('SENTINEL_2');

      if (modis && sentinel2) {
        return {
          description: 'Combine MODIS daily coverage with Sentinel-2 high resolution using data fusion techniques (e.g., STARFM algorithm)',
          descriptionAr: 'دمج التغطية اليومية من MODIS مع الدقة العالية من Sentinel-2 باستخدام تقنيات دمج البيانات (مثل خوارزمية STARFM)',
          sources: [modis, sentinel2],
        };
      }
    }

    // Suggest SAR + Optical for all-weather
    if (requirements.cloudFree && requirements.application !== 'soil') {
      const sar = this.satellites.get('SENTINEL_1');
      const optical = scored.find(s => !s.satellite.sensor.includes('SAR'))?.satellite;

      if (sar && optical) {
        return {
          description: `Combine ${optical.nameEn} optical data with Sentinel-1 SAR for all-weather monitoring`,
          descriptionAr: `دمج بيانات ${optical.nameAr} البصرية مع رادار Sentinel-1 للرصد في جميع الأحوال الجوية`,
          sources: [optical, sar],
        };
      }
    }

    return undefined;
  }

  private getProcessingNotes(satellite: SatelliteSource, requirements: DataRequirements): string[] {
    const notes: string[] = [];

    if (!satellite) return notes;

    if (satellite.id === 'SENTINEL_2') {
      notes.push('Apply atmospheric correction (Sen2Cor or ACOLITE)');
      notes.push('Cloud masking using QA60 band or s2cloudless');
      notes.push('Resample 20m bands to 10m if needed');
    }

    if (satellite.id === 'SENTINEL_1') {
      notes.push('Apply orbit file and thermal noise removal');
      notes.push('Radiometric and terrain correction');
      notes.push('Speckle filtering (Lee, Refined Lee, or Gamma MAP)');
    }

    if (satellite.id.startsWith('LANDSAT')) {
      notes.push('Apply surface reflectance correction (already in Collection 2 L2)');
      notes.push('Cloud masking using QA_PIXEL band');
    }

    if (satellite.id === 'MODIS') {
      notes.push('Use ready-made products when available (MOD13, MOD15, MOD16)');
      notes.push('Apply quality filtering using QC bands');
    }

    if (requirements.application === 'lai') {
      notes.push('Consider using empirical or physical LAI retrieval models');
      notes.push('Validate with ground measurements if available');
    }

    return notes;
  }

  private estimateAvailability(satellite: SatelliteSource, requirements: DataRequirements): string {
    if (!satellite) return 'Unknown';

    if (satellite.isFree) {
      return `Data typically available within ${satellite.temporalResolution * 2} days of acquisition`;
    } else {
      return `Commercial tasking required, typically 1-7 days for new acquisitions`;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get All Satellites - الحصول على جميع الأقمار الصناعية
  // ─────────────────────────────────────────────────────────────────────────────

  getAllSatellites(): SatelliteSource[] {
    return Array.from(this.satellites.values());
  }

  getSatelliteById(id: string): SatelliteSource | undefined {
    return this.satellites.get(id);
  }

  getFreeSatellites(): SatelliteSource[] {
    return Array.from(this.satellites.values()).filter(s => s.isFree);
  }

  getSatellitesByApplication(application: string): SatelliteSource[] {
    return Array.from(this.satellites.values()).filter(s =>
      s.applications.includes(application)
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Band Combinations - الحصول على تركيبات النطاقات
  // ─────────────────────────────────────────────────────────────────────────────

  getBandCombinations(): BandCombination[] {
    return this.bandCombinations;
  }

  getBandCombinationByIndex(indexName: string): BandCombination | undefined {
    return this.bandCombinations.find(b => b.name.toLowerCase() === indexName.toLowerCase());
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Compare Satellites - مقارنة الأقمار الصناعية
  // ─────────────────────────────────────────────────────────────────────────────

  compareSatellites(ids: string[]): {
    satellites: SatelliteSource[];
    comparison: {
      bestSpatial: string;
      bestTemporal: string;
      bestFree: string;
      summary: string;
      summaryAr: string;
    };
  } {
    const satellites = ids
      .map(id => this.satellites.get(id))
      .filter((s): s is SatelliteSource => s !== undefined);

    if (satellites.length === 0) {
      return {
        satellites: [],
        comparison: {
          bestSpatial: 'N/A',
          bestTemporal: 'N/A',
          bestFree: 'N/A',
          summary: 'No valid satellites found',
          summaryAr: 'لم يتم العثور على أقمار صناعية صالحة',
        },
      };
    }

    const bestSpatial = satellites.reduce((a, b) =>
      a.spatialResolution < b.spatialResolution ? a : b
    );

    const bestTemporal = satellites.reduce((a, b) =>
      a.temporalResolution < b.temporalResolution ? a : b
    );

    const freeSats = satellites.filter(s => s.isFree);
    const bestFree = freeSats.length > 0
      ? freeSats.reduce((a, b) => a.spatialResolution < b.spatialResolution ? a : b)
      : null;

    return {
      satellites,
      comparison: {
        bestSpatial: bestSpatial.nameEn,
        bestTemporal: bestTemporal.nameEn,
        bestFree: bestFree?.nameEn || 'N/A',
        summary: `Best spatial: ${bestSpatial.nameEn} (${bestSpatial.spatialResolution}m), ` +
                 `Best temporal: ${bestTemporal.nameEn} (${bestTemporal.temporalResolution} days)`,
        summaryAr: `أفضل دقة مكانية: ${bestSpatial.nameAr} (${bestSpatial.spatialResolution}م)، ` +
                   `أفضل دقة زمنية: ${bestTemporal.nameAr} (${bestTemporal.temporalResolution} يوم)`,
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Get Recommendation for Specific Crop Model Module
  // توصيات لوحدات نموذج نمو المحاصيل
  // ─────────────────────────────────────────────────────────────────────────────

  getRecommendationForModule(module: 'phenology' | 'photosynthesis' | 'biomass' | 'roots' | 'water'): {
    recommended: SatelliteSource[];
    indices: BandCombination[];
    notes: string[];
    notesAr: string[];
  } {
    switch (module) {
      case 'phenology':
        return {
          recommended: [
            this.satellites.get('MODIS')!,
            this.satellites.get('SENTINEL_2')!,
          ].filter(Boolean),
          indices: this.bandCombinations.filter(b => ['NDVI', 'EVI', 'NDRE'].includes(b.name)),
          notes: [
            'Use MODIS for continuous time series (16-day composites)',
            'Sentinel-2 for detailed phenological stages',
            'Combine with GDD from weather data',
          ],
          notesAr: [
            'استخدم MODIS للسلاسل الزمنية المستمرة (مركبات 16 يوم)',
            'Sentinel-2 للمراحل الفينولوجية التفصيلية',
            'ادمج مع GDD من بيانات الطقس',
          ],
        };

      case 'photosynthesis':
        return {
          recommended: [
            this.satellites.get('SENTINEL_2')!,
            this.satellites.get('MODIS')!,
          ].filter(Boolean),
          indices: this.bandCombinations.filter(b => ['NDVI', 'EVI', 'NDRE'].includes(b.name)),
          notes: [
            'NDRE correlates well with chlorophyll content',
            'Use MODIS GPP product (MOD17) for validation',
            'Red Edge bands essential for accurate estimation',
          ],
          notesAr: [
            'NDRE يرتبط جيداً بمحتوى الكلوروفيل',
            'استخدم منتج GPP من MODIS للتحقق',
            'نطاقات Red Edge ضرورية للتقدير الدقيق',
          ],
        };

      case 'biomass':
        return {
          recommended: [
            this.satellites.get('SENTINEL_2')!,
            this.satellites.get('SENTINEL_1')!,
          ].filter(Boolean),
          indices: this.bandCombinations.filter(b => ['NDVI', 'EVI', 'LAI (from NDVI)'].includes(b.name)),
          notes: [
            'Combine optical NDVI with SAR backscatter',
            'SAR VH polarization sensitive to biomass',
            'Consider time series for growth monitoring',
          ],
          notesAr: [
            'ادمج NDVI البصري مع الانعكاس الراداري',
            'استقطاب VH حساس للكتلة الحيوية',
            'استخدم السلاسل الزمنية لرصد النمو',
          ],
        };

      case 'roots':
        return {
          recommended: [
            this.satellites.get('SENTINEL_1')!,
            this.satellites.get('SENTINEL_2')!,
          ].filter(Boolean),
          indices: this.bandCombinations.filter(b => ['NDWI', 'NDVI'].includes(b.name)),
          notes: [
            'SAR for soil moisture estimation (proxy for root water uptake)',
            'NDWI for plant water content monitoring',
            'Combine with soil maps and weather data',
          ],
          notesAr: [
            'SAR لتقدير رطوبة التربة (مؤشر لامتصاص الجذور للماء)',
            'NDWI لرصد محتوى الماء في النبات',
            'ادمج مع خرائط التربة وبيانات الطقس',
          ],
        };

      case 'water':
        return {
          recommended: [
            this.satellites.get('SENTINEL_1')!,
            this.satellites.get('LANDSAT_8')!,
            this.satellites.get('MODIS')!,
          ].filter(Boolean),
          indices: this.bandCombinations.filter(b => ['NDWI', 'LST'].includes(b.name)),
          notes: [
            'Use MODIS ET product (MOD16) for reference ET',
            'LST for crop water stress detection',
            'SAR for soil moisture monitoring',
            'Combine with FAO-56 Kc values',
          ],
          notesAr: [
            'استخدم منتج ET من MODIS للتبخر-نتح المرجعي',
            'LST للكشف عن إجهاد المياه',
            'SAR لرصد رطوبة التربة',
            'ادمج مع قيم Kc من FAO-56',
          ],
        };
    }
  }
}
