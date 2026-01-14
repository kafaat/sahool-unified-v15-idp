/**
 * Health Check API Endpoint - Web Dashboard
 * نقطة نهاية فحص الصحة - لوحة التحكم الرئيسية
 */

import { NextResponse } from "next/server";

// ═══════════════════════════════════════════════════════════════════════════
// Health Check Handler
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GET /api/health
 * Health check endpoint for Kubernetes and monitoring systems
 * نقطة نهاية لفحص صحة التطبيق لـ Kubernetes وأنظمة المراقبة
 */
export async function GET() {
  try {
    // Basic health check - verify the app is running
    const healthStatus = {
      status: "healthy",
      service: "sahool-web",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || "unknown",
    };

    return NextResponse.json(healthStatus, { status: 200 });
  } catch {
    // If we reach here, something is wrong
    // SECURITY: Don't expose internal error details to clients
    return NextResponse.json(
      {
        status: "unhealthy",
        service: "sahool-web",
        timestamp: new Date().toISOString(),
      },
      { status: 503 },
    );
  }
}
