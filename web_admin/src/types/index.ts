// Sahool Admin Dashboard Types
// أنواع البيانات للوحة تحكم سهول

export interface Farm {
  id: string;
  name: string;
  nameAr: string;
  ownerId: string;
  governorate: string;
  district: string;
  area: number; // hectares
  coordinates: {
    lat: number;
    lng: number;
  };
  polygon?: GeoJSON.Polygon;
  crops: string[];
  status: 'active' | 'inactive' | 'pending';
  healthScore: number;
  lastUpdated: string;
  createdAt: string;
}

export interface DiagnosisRecord {
  id: string;
  farmId: string;
  farmName: string;
  imageUrl: string;
  thumbnailUrl: string;
  cropType: string;
  diseaseId: string;
  diseaseName: string;
  diseaseNameAr: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'confirmed' | 'rejected' | 'treated';
  expertReview?: {
    expertId: string;
    expertName: string;
    notes: string;
    reviewedAt: string;
  };
  treatment?: {
    recommendation: string;
    recommendationAr: string;
    appliedAt?: string;
  };
  location: {
    lat: number;
    lng: number;
  };
  diagnosedAt: string;
  createdBy: string;
}

export interface DashboardStats {
  totalFarms: number;
  activeFarms: number;
  totalArea: number;
  totalDiagnoses: number;
  pendingReviews: number;
  criticalAlerts: number;
  avgHealthScore: number;
  weeklyDiagnoses: number;
}

export interface WeatherAlert {
  id: string;
  type: 'frost' | 'heat' | 'drought' | 'flood' | 'wind' | 'pest';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  affectedGovernorates: string[];
  startDate: string;
  endDate?: string;
  isActive: boolean;
}

export interface SensorReading {
  id: string;
  sensorId: string;
  farmId: string;
  type: 'soil_moisture' | 'temperature' | 'humidity' | 'et0' | 'ndvi';
  value: number;
  unit: string;
  isVirtual: boolean;
  timestamp: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  nameAr: string;
  role: 'admin' | 'expert' | 'farmer' | 'viewer';
  governorate?: string;
  isActive: boolean;
  lastLogin?: string;
  createdAt: string;
}

export interface Governorate {
  id: string;
  name: string;
  nameAr: string;
  farmCount: number;
  totalArea: number;
  avgHealthScore: number;
  coordinates: {
    lat: number;
    lng: number;
  };
}

// Yemen governorates for the map
export const YEMEN_GOVERNORATES: Governorate[] = [
  { id: 'sanaa', name: 'Sanaa', nameAr: 'صنعاء', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 15.3694, lng: 44.1910 } },
  { id: 'aden', name: 'Aden', nameAr: 'عدن', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 12.7855, lng: 45.0187 } },
  { id: 'taiz', name: 'Taiz', nameAr: 'تعز', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 13.5789, lng: 44.0219 } },
  { id: 'hadramaut', name: 'Hadramaut', nameAr: 'حضرموت', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 15.9543, lng: 48.7863 } },
  { id: 'ibb', name: 'Ibb', nameAr: 'إب', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 13.9728, lng: 44.1693 } },
  { id: 'hodeidah', name: 'Al Hudaydah', nameAr: 'الحديدة', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 14.7979, lng: 42.9540 } },
  { id: 'dhamar', name: 'Dhamar', nameAr: 'ذمار', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 14.5427, lng: 44.4051 } },
  { id: 'marib', name: 'Marib', nameAr: 'مأرب', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 15.4547, lng: 45.3268 } },
  { id: 'hajjah', name: 'Hajjah', nameAr: 'حجة', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 15.6917, lng: 43.6033 } },
  { id: 'amran', name: 'Amran', nameAr: 'عمران', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 15.6594, lng: 43.9439 } },
  { id: 'saadah', name: 'Saadah', nameAr: 'صعدة', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 16.9410, lng: 43.7636 } },
  { id: 'lahij', name: 'Lahij', nameAr: 'لحج', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 13.0337, lng: 44.8833 } },
  { id: 'abyan', name: 'Abyan', nameAr: 'أبين', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 13.5833, lng: 45.8667 } },
  { id: 'shabwah', name: 'Shabwah', nameAr: 'شبوة', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 14.5333, lng: 46.8333 } },
  { id: 'albaydah', name: 'Al Bayda', nameAr: 'البيضاء', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 14.1667, lng: 45.5667 } },
  { id: 'aljawf', name: 'Al Jawf', nameAr: 'الجوف', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 16.5000, lng: 45.5000 } },
  { id: 'almahwit', name: 'Al Mahwit', nameAr: 'المحويت', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 15.4667, lng: 43.5500 } },
  { id: 'almahrah', name: 'Al Mahrah', nameAr: 'المهرة', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 16.5000, lng: 51.5000 } },
  { id: 'raymah', name: 'Raymah', nameAr: 'ريمة', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 14.6167, lng: 43.7167 } },
  { id: 'socotra', name: 'Socotra', nameAr: 'سقطرى', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 12.4634, lng: 53.8237 } },
  { id: 'aldhalei', name: 'Ad Dali', nameAr: 'الضالع', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 13.6833, lng: 44.7333 } },
  { id: 'sanaa_city', name: 'Sanaa City', nameAr: 'أمانة العاصمة', farmCount: 0, totalArea: 0, avgHealthScore: 0, coordinates: { lat: 15.3694, lng: 44.1910 } },
];
