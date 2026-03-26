/**
 * SAHOOL Shared Types Package
 * Centralized type definitions for the SAHOOL platform
 *
 * @packageDocumentation
 * @module @sahool/shared-types
 * @version 16.0.0
 */

// Auth types - أنواع المصادقة
export * from './auth';

// API types - أنواع واجهة برمجة التطبيقات
export * from './api';

// Express types - أنواع Express
export * from './express';

// WebSocket types - أنواع WebSocket
export * from './websocket';

// Agricultural Monitoring types (Remote Sensing + AI)
// أنواع الرصد الزراعي (الاستشعار عن بعد + الذكاء الاصطناعي)
export * from './monitoring';

// Field & Farm types - أنواع الحقول والمزارع
export * from './field';

// Vision Service types - أنواع خدمة الرؤية الحاسوبية
export * from './vision';

// Terrain Service types - أنواع خدمة التضاريس
export * from './terrain';

// Hydrology Service types - أنواع خدمة الهيدرولوجيا
export * from './hydrology';

// Leveling Optimizer Service types - أنواع خدمة تحسين التسوية
export * from './leveling';

// Edge Device types - أنواع أجهزة الحوسبة الطرفية
export * from './edge';

// Unified API Contracts - العقود الموحدة لواجهة برمجة التطبيقات
// Import via "@sahool/shared-types/contracts" subpath to avoid
// name collisions with existing type modules (ApiResponse, FieldStatus, etc.).
// Re-export only the non-conflicting contract modules here:
export * from './contracts/service-ports';
export * from './contracts/error-codes';
export * from './contracts/api-endpoints';

// Zod Validation Schemas - مخططات التحقق باستخدام Zod
// Import via "@sahool/shared-types/schemas" subpath for runtime validation.
// NOTE: Requires `zod` package to be installed as a dependency.
// NOT re-exported here to avoid name collisions (LoginResponse, UserRole,
// CreateFieldPayload, UpdateFieldPayload). Use subpath import instead:
//   import { LoginRequestSchema } from "@sahool/shared-types/schemas";
