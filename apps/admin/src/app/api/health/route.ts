/**
 * Health Check API Endpoint - Admin Dashboard
 * نقطة نهاية فحص الصحة - لوحة التحكم
 */

import { NextResponse } from "next/server";

// ═══════════════════════════════════════════════════════════════════════════
// Health Check Handler
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GET /api/health
 * Health check endpoint for Docker and monitoring systems
 */
export async function GET() {
  try {
    // Basic health check - verify the app is running
    const healthStatus = {
      status: "healthy",
      service: "sahool-admin",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || "unknown",
    };

    return NextResponse.json(healthStatus, { status: 200 });
  } catch (error) {
    // If we reach here, something is wrong
    return NextResponse.json(
      {
        status: "unhealthy",
        service: "sahool-admin",
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 503 },
    );
  }
}
