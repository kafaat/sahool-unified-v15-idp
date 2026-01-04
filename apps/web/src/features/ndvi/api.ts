/**
 * NDVI Feature - API Layer
 * طبقة API لميزة مؤشر NDVI
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface NDVIData {
  fieldId: string;
  fieldName: string;
  date: string;
  ndviMean: number;
  ndviMin: number;
  ndviMax: number;
  ndviStd: number;
  healthStatus: 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';
  cloudCoverage: number;
  source: 'sentinel-2' | 'landsat' | 'modis';
}

export interface NDVITimeSeries {
  fieldId: string;
  data: Array<{
    date: string;
    ndvi: number;
    healthStatus: NDVIData['healthStatus'];
  }>;
  trend: 'improving' | 'stable' | 'declining';
  anomalies: Array<{
    date: string;
    type: 'sudden_drop' | 'unusual_peak';
    severity: 'low' | 'medium' | 'high';
  }>;
}

export interface NDVIMapData {
  fieldId: string;
  date: string;
  rasterUrl: string;
  bounds: [[number, number], [number, number]];
  colorScale: {
    min: number;
    max: number;
    colors: string[];
  };
}

export interface NDVIFilters {
  fieldId?: string;
  governorate?: string;
  startDate?: string;
  endDate?: string;
  minNdvi?: number;
  maxNdvi?: number;
}

// API Functions
export const ndviApi = {
  /**
   * Get latest NDVI data for all fields
   */
  getLatestNDVI: async (filters?: NDVIFilters): Promise<NDVIData[]> => {
    const params = new URLSearchParams();
    if (filters?.governorate) params.set('governorate', filters.governorate);
    if (filters?.minNdvi) params.set('min_ndvi', filters.minNdvi.toString());
    if (filters?.maxNdvi) params.set('max_ndvi', filters.maxNdvi.toString());

    const response = await api.get(`/api/v1/ndvi/latest?${params.toString()}`);
    return response.data;
  },

  /**
   * Get NDVI data for specific field
   */
  getFieldNDVI: async (fieldId: string): Promise<NDVIData> => {
    const response = await api.get(`/api/v1/ndvi/fields/${fieldId}`);
    return response.data;
  },

  /**
   * Get NDVI time series for a field
   */
  getNDVITimeSeries: async (
    fieldId: string,
    startDate?: string,
    endDate?: string
  ): Promise<NDVITimeSeries> => {
    const params = new URLSearchParams();
    if (startDate) params.set('start_date', startDate);
    if (endDate) params.set('end_date', endDate);

    const response = await api.get(`/api/v1/ndvi/fields/${fieldId}/timeseries?${params.toString()}`);
    return response.data;
  },

  /**
   * Get NDVI raster map data
   */
  getNDVIMap: async (fieldId: string, date?: string): Promise<NDVIMapData> => {
    const params = date ? `?date=${date}` : '';
    const response = await api.get(`/api/v1/ndvi/fields/${fieldId}/map${params}`);
    return response.data;
  },

  /**
   * Request new NDVI analysis
   */
  requestNDVIAnalysis: async (fieldId: string): Promise<{ jobId: string; status: string }> => {
    const response = await api.post(`/api/v1/ndvi/fields/${fieldId}/analyze`);
    return response.data;
  },

  /**
   * Get NDVI comparison between dates
   */
  compareNDVI: async (
    fieldId: string,
    date1: string,
    date2: string
  ): Promise<{
    date1: NDVIData;
    date2: NDVIData;
    change: number;
    changePercent: number;
    interpretation: string;
  }> => {
    const response = await api.get(
      `/api/v1/ndvi/fields/${fieldId}/compare?date1=${date1}&date2=${date2}`
    );
    return response.data;
  },

  /**
   * Get regional NDVI statistics
   */
  getRegionalStats: async (governorate?: string): Promise<{
    averageNDVI: number;
    healthDistribution: Record<NDVIData['healthStatus'], number>;
    topFields: Array<{ fieldId: string; name: string; ndvi: number }>;
    bottomFields: Array<{ fieldId: string; name: string; ndvi: number }>;
  }> => {
    const params = governorate ? `?governorate=${governorate}` : '';
    const response = await api.get(`/api/v1/ndvi/stats/regional${params}`);
    return response.data;
  },
};
