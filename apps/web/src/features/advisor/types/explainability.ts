/**
 * Explainability Types
 * أنواع طبقة التفسير
 *
 * TypeScript types mirroring shared/ai/explainability.py
 * for rendering AI recommendation explanations in the UI.
 */

// ---------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------

export enum ExplanationType {
  FACTOR_BASED = 'factor_based',
  RULE_BASED = 'rule_based',
  DATA_DRIVEN = 'data_driven',
  COMPARATIVE = 'comparative',
  CONFIDENCE_BASED = 'confidence_based',
}

export enum FactorType {
  WEATHER = 'weather',
  SOIL = 'soil',
  CROP_STAGE = 'crop_stage',
  HISTORICAL = 'historical',
  SENSOR = 'sensor',
  MARKET = 'market',
  RESOURCE = 'resource',
  CALENDAR = 'calendar',
  USER_PREFERENCE = 'user_preference',
}

export enum ImpactLevel {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

// ---------------------------------------------------------------------------
// Interfaces
// ---------------------------------------------------------------------------

export interface ContributingFactor {
  factorType: FactorType;
  name: string;
  nameAr: string;
  value: string | number;
  description: string;
  descriptionAr: string;
  impact: ImpactLevel;
  weight: number;
  direction: 'supports' | 'opposes' | 'neutral';
  confidence: number;
  evidence?: string;
  evidenceAr?: string;
  source?: string;
}

export interface RuleExplanation {
  ruleId: string;
  ruleName: string;
  ruleNameAr: string;
  condition: string;
  conditionAr: string;
  action: string;
  actionAr: string;
  matched: boolean;
  matchDetails: string;
  matchDetailsAr: string;
  source: string;
  category: string;
}

export interface AlternativeRecommendation {
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  score: number;
  rank: number;
  rejectionReasons: string[];
  rejectionReasonsAr: string[];
  pros: string[];
  cons: string[];
  prosAr: string[];
  consAr: string[];
}

export interface Explanation {
  recommendationId: string;
  explanationType: ExplanationType;
  createdAt: string;
  summary: string;
  summaryAr: string;
  detailedExplanation: string;
  detailedExplanationAr: string;
  factors: ContributingFactor[];
  rules: RuleExplanation[];
  alternatives: AlternativeRecommendation[];
  overallConfidence: number;
  uncertaintyReasons: string[];
  uncertaintyReasonsAr: string[];
  dataSources: string[];
  context: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Request parameters for explanation endpoints
// ---------------------------------------------------------------------------

export interface ExplainIrrigationParams {
  recommendationId: string;
  soilMoisture: number;
  weatherForecast: {
    rainProbability: number;
    temperature: number;
    [key: string]: unknown;
  };
  cropStage: string;
  etValue: number;
  recommendedAmountMm: number;
  alternatives?: Array<{
    title: string;
    titleAr?: string;
    description: string;
    descriptionAr?: string;
    score: number;
    rejectionReasons?: string[];
    rejectionReasonsAr?: string[];
  }>;
}

export interface ExplainFertilizerParams {
  recommendationId: string;
  soilTest: {
    nitrogen: number;
    phosphorus: number;
    potassium: number;
    [key: string]: number;
  };
  cropType: string;
  cropStage: string;
  targetYield: number;
  recommendedFertilizer: string;
  recommendedRate: number;
}
