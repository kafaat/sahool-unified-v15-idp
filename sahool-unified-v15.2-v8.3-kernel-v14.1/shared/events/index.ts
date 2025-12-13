/**
 * Shared event contracts (minimal, v8.3 enhanced).
 * Extend this file as you add more domain events.
 */

export type EventEnvelope<T> = {
  eventId: string;
  eventType: string;
  timestamp: string; // ISO
  tenantId?: string;
  payload: T;
};

export type WeatherSignal = {
  location: string;
  summary: string;
  tempC: number;
  windKph?: number;
};

export type NdviSignal = {
  fieldId: string;
  date: string;
  ndvi: number;
  note?: string;
};

export type AstralSignal = {
  region: string;
  date: string;
  lunarMansion: string;
  recommendation?: string;
};

export type CropAdvice = {
  fieldId: string;
  crop: string;
  tips: string[];
  signals?: Record<string, unknown>;
};
