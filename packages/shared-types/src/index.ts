/**
 * SAHOOL Shared Types Package
 * Centralized TypeScript type definitions for the SAHOOL platform
 *
 * @packageDocumentation
 *
 * This package provides comprehensive type definitions for:
 * - Common utilities (branded types, base entities, utility types)
 * - GeoJSON types for geospatial data
 * - Domain entities (fields, farms, tasks, alerts)
 * - Authentication and authorization
 * - API responses and pagination
 * - WebSocket communication
 * - Weather and sensor data
 * - Agricultural monitoring
 *
 * @example
 * ```typescript
 * import type { Field, Farm, Task, Alert } from '@sahool/shared-types';
 * import type { ApiResponse, PaginatedResponse } from '@sahool/shared-types/api';
 * import type { GeoPolygon, GeoFeature } from '@sahool/shared-types/geo';
 * ```
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Common Types - Base utilities and branded types
// ═══════════════════════════════════════════════════════════════════════════════
export * from "./common";

// ═══════════════════════════════════════════════════════════════════════════════
// GeoJSON Types - Geospatial data structures
// ═══════════════════════════════════════════════════════════════════════════════
export * from "./geo";

// ═══════════════════════════════════════════════════════════════════════════════
// Auth Types - Authentication and authorization
// ═══════════════════════════════════════════════════════════════════════════════
export * from "./auth";

// ═══════════════════════════════════════════════════════════════════════════════
// API Types - Response structures and pagination
// ═══════════════════════════════════════════════════════════════════════════════
export * from "./api";

// ═══════════════════════════════════════════════════════════════════════════════
// Domain Types - Core business entities
// ═══════════════════════════════════════════════════════════════════════════════
export * from "./field";
export * from "./farm";
export * from "./task";
export * from "./alert";

// ═══════════════════════════════════════════════════════════════════════════════
// Environmental Types - Weather and sensors
// ═══════════════════════════════════════════════════════════════════════════════
export * from "./weather";
export * from "./sensor";

// ═══════════════════════════════════════════════════════════════════════════════
// Communication Types - WebSocket and Express
// ═══════════════════════════════════════════════════════════════════════════════
export * from "./websocket";
export * from "./express";

// ═══════════════════════════════════════════════════════════════════════════════
// Agricultural Monitoring Types - Remote Sensing and AI
// ═══════════════════════════════════════════════════════════════════════════════
export * from "./monitoring";
