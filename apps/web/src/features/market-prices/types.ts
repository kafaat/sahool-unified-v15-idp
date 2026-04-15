/**
 * Market Prices Feature - Types
 * أنواع ميزة أسعار السوق
 */

export type Currency = 'SAR' | 'YER' | 'USD';
export type PriceUnit = 'kg' | 'ton' | 'quintal' | 'sack' | 'box' | 'piece';
export type PriceQuality =
  | 'premium'
  | 'grade_a'
  | 'grade_b'
  | 'grade_c'
  | 'standard'
  | 'mixed';
export type MarketType =
  | 'wholesale'
  | 'retail'
  | 'farm_gate'
  | 'export'
  | 'import'
  | 'futures';
export type AlertType =
  | 'price_above'
  | 'price_below'
  | 'price_change_pct'
  | 'price_drop'
  | 'price_spike'
  | 'best_selling_time'
  | 'market_opportunity';
export type AlertStatus =
  | 'active'
  | 'triggered'
  | 'expired'
  | 'disabled'
  | 'acknowledged';
export type TrendDirection =
  | 'rising'
  | 'falling'
  | 'stable'
  | 'volatile'
  | 'unknown';
export type Country = 'saudi_arabia' | 'yemen';

export interface MarketRegion {
  id: string;
  name: string;
  nameAr: string;
  country: Country;
  parentRegionId?: string;
  latitude: number;
  longitude: number;
  isActive: boolean;
}

export interface Market {
  id: string;
  name: string;
  nameAr: string;
  regionId: string;
  regionName: string;
  regionNameAr: string;
  country: Country;
  marketType: MarketType;
  majorCrops: string[];
  phone?: string;
  email?: string;
  isActive: boolean;
  establishedDate: string;
}

export interface CropPriceRecord {
  id: string;
  cropType: string;
  cropTypeAr: string;
  marketId: string;
  marketName: string;
  marketNameAr: string;
  date: string;
  priceValue: number;
  currency: Currency;
  unit: PriceUnit;
  quality: PriceQuality;
  marketType: MarketType;
  volumeTraded?: number;
  priceSource?: string;
}

export interface PriceAlert {
  id: string;
  farmerId: string;
  alertType: AlertType;
  cropType: string;
  cropTypeAr: string;
  marketId: string;
  marketName: string;
  targetValue: number;
  currency: Currency;
  unit: PriceUnit;
  status: AlertStatus;
  createdDate: string;
  triggeredDate?: string;
  message?: string;
  messageAr?: string;
}

export interface PriceTrend {
  id: string;
  cropType: string;
  cropTypeAr: string;
  marketId: string;
  marketName: string;
  periodStart: string;
  periodEnd: string;
  priceOpen: number;
  priceHigh: number;
  priceLow: number;
  priceClose: number;
  avgPrice: number;
  trendDirection: TrendDirection;
  trendStrength: number;
  changePercent: number;
}

export interface MarketComparison {
  id: string;
  cropType: string;
  cropTypeAr: string;
  date: string;
  marketPrices: Record<
    string,
    {
      marketName: string;
      marketNameAr: string;
      price: number;
      currency: Currency;
    }
  >;
  bestMarket: string;
  bestMarketAr: string;
  priceDifferencePercent: number;
}

export interface SellingRecommendation {
  id: string;
  farmerId: string;
  cropType: string;
  cropTypeAr: string;
  recommendedMarket: string;
  recommendedMarketAr: string;
  recommendedTiming: string;
  expectedPrice: number;
  currency: Currency;
  unit: PriceUnit;
  confidenceLevel: number;
  reasoning: string;
  reasoningAr: string;
}

export interface PriceFilters {
  cropType?: string;
  marketId?: string;
  region?: string;
  marketType?: MarketType;
  quality?: PriceQuality;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface AlertFilters {
  status?: AlertStatus;
  alertType?: AlertType;
  cropType?: string;
}

export interface AlertFormData {
  alertType: AlertType;
  cropType: string;
  marketId: string;
  targetValue: number;
  currency: Currency;
  unit: PriceUnit;
}

export interface MarketPriceStats {
  totalMarkets: number;
  totalCropsTracked: number;
  averagePriceChange: number;
  topGainers: string[];
  topLosers: string[];
  mostTraded: string[];
}
