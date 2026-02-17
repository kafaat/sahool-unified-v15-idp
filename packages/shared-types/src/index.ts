/**
 * SAHOOL Shared Types Package
 * Centralized type definitions for the SAHOOL platform
 *
 * @packageDocumentation
 * @module @sahool/shared-types
 * @version 16.0.0
 */

// Auth types - أنواع المصادقة
export * from "./auth";

// API types - أنواع واجهة برمجة التطبيقات
export * from "./api";

// Express types - أنواع Express
export * from "./express";

// WebSocket types - أنواع WebSocket
export * from "./websocket";

// Agricultural Monitoring types (Remote Sensing + AI)
// أنواع الرصد الزراعي (الاستشعار عن بعد + الذكاء الاصطناعي)
export * from "./monitoring";

// Field & Farm types - أنواع الحقول والمزارع
export * from "./field";

// Vision Service types - أنواع خدمة الرؤية الحاسوبية
export * from "./vision";

// Terrain Service types - أنواع خدمة التضاريس
export * from "./terrain";

// Hydrology Service types - أنواع خدمة الهيدرولوجيا
export * from "./hydrology";

// Leveling Optimizer Service types - أنواع خدمة تحسين التسوية
export * from "./leveling";

// Edge Device types - أنواع أجهزة الحوسبة الطرفية
export * from "./edge";

// Unified API Contracts - العقود الموحدة لواجهة برمجة التطبيقات
// Service ports, error codes, endpoint paths, and response shapes
export * from "./contracts";
