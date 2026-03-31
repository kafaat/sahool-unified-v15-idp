/**
 * Agricultural Calendar Feature - Types
 * أنواع ميزة التقويم الزراعي
 */

export type CalendarType = 'gregorian' | 'hijri' | 'both';

export type Region =
  | 'riyadh'
  | 'makkah'
  | 'madinah'
  | 'eastern'
  | 'asir'
  | 'tabuk'
  | 'hail'
  | 'northern_borders'
  | 'jazan'
  | 'najran'
  | 'al_baha'
  | 'al_jouf'
  | 'qassim'
  | 'sanaa'
  | 'aden'
  | 'taiz'
  | 'hodeidah'
  | 'hadramaut'
  | 'ibb'
  | 'dhamar'
  | 'marib'
  | 'al_mahwit'
  | 'lahij';

export type ClimateZone =
  | 'arid_hot'
  | 'arid_mild'
  | 'semi_arid'
  | 'subtropical'
  | 'highland'
  | 'coastal';

export type AgriculturalSeason =
  | 'winter'
  | 'spring'
  | 'summer'
  | 'autumn'
  | 'saif'
  | 'kharif'
  | 'shita'
  | 'rabi';

export type PlantingEventType =
  | 'planting'
  | 'harvesting'
  | 'transplanting'
  | 'pruning'
  | 'irrigation'
  | 'fertilization'
  | 'pest_control'
  | 'disease_management';

export type EventPriority = 'critical' | 'high' | 'medium' | 'low';

export type RecommendationConfidence = 'high' | 'medium' | 'low';

export interface HijriDate {
  hijriYear: number;
  hijriMonth: number;
  hijriDay: number;
  hijriMonthName: string;
  hijriMonthNameAr: string;
}

export interface IslamicEvent {
  eventName: string;
  eventNameAr: string;
  eventType: string;
  hijriDate: HijriDate;
  gregorianDateRange: { start: string; end: string };
  significance: string;
  significanceAr: string;
  agriculturalNotes: string;
  agriculturalNotesAr: string;
}

export interface TraditionalSeasonInfo {
  season: string;
  seasonAr: string;
  startDate: string;
  endDate: string;
  characteristics: string;
  characteristicsAr: string;
  agriculturalActivities: string[];
  agriculturalActivitiesAr: string[];
}

export interface SeasonDefinition {
  season: AgriculturalSeason;
  seasonAr: string;
  startMonth: number;
  endMonth: number;
  climateCharacteristics: string;
  climateCharacteristicsAr: string;
}

export interface PlantingWindow {
  cropType: string;
  cropTypeAr: string;
  region: Region;
  season: AgriculturalSeason;
  startMonth: number;
  endMonth: number;
  daysBeforeWindowEnd: number;
}

export interface CalendarEvent {
  id: string;
  eventType: PlantingEventType;
  eventDate: string;
  cropType: string;
  cropTypeAr: string;
  region: Region;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  priority: EventPriority;
  linkedTaskId?: string;
  isCompleted: boolean;
}

export interface PlantingRecommendation {
  cropType: string;
  cropNameAr: string;
  region: Region;
  season: AgriculturalSeason;
  urgency: EventPriority;
  recommendedDate: string;
  windowEndDate: string;
  reasoning: string;
  reasoningAr: string;
  confidenceLevel: RecommendationConfidence;
  alternativeCrops: string[];
}

export interface SeasonalCalendar {
  id: string;
  region: Region;
  regionAr: string;
  climateZone: ClimateZone;
  events: CalendarEvent[];
  plantingRecommendations: PlantingRecommendation[];
}

export interface RegionMetadata {
  region: Region;
  nameAr: string;
  climateZone: ClimateZone;
  agricultureType: string;
  majorCrops: string[];
  bestSeasons: AgriculturalSeason[];
}

export interface CalendarFilters {
  region?: Region;
  season?: AgriculturalSeason;
  month?: number;
  cropType?: string;
  eventType?: PlantingEventType;
}

export interface CalendarEventFormData {
  eventType: PlantingEventType;
  eventDate: string;
  cropType: string;
  cropTypeAr: string;
  region: Region;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  priority: EventPriority;
  linkedTaskId?: string;
}

export interface AgriCalendarStats {
  totalEvents: number;
  upcomingEvents: number;
  completedEvents: number;
  byEventType: Record<string, number>;
  byRegion: Record<string, number>;
  byPriority: Record<string, number>;
  activeRecommendations: number;
}
