/**
 * Example Admin-Only API Route
 * Demonstrates server-side role verification
 */

import { NextRequest, NextResponse } from "next/server";
import { withAdmin, withRole, withAuth } from "@/lib/auth";

/**
 * GET - Admin only endpoint
 * Example: Fetch admin-only data
 */
export const GET = withAdmin(async (request, { user }) => {
  // Only admins can access this endpoint
  // The withAdmin wrapper ensures server-side role verification

  return NextResponse.json({
    message: "Admin access granted",
    user: {
      id: user.id,
      email: user.email,
      role: user.role,
    },
    data: {
      // Admin-only data
      total_users: 100,
      total_farms: 50,
      system_health: "good",
    },
  });
});

/**
 * POST - Admin or Supervisor endpoint
 * Example: Create a new resource
 */
export const POST = withRole(
  ["admin", "supervisor"],
  async (request, { user }) => {
    // Both admins and supervisors can access this endpoint

    const body = await request.json();

    return NextResponse.json({
      message: "Resource created successfully",
      created_by: user.email,
      role: user.role,
      data: body,
    });
  },
);

/**
 * PATCH - Any authenticated user
 * Example: Update user's own profile
 */
export const PATCH = withAuth(async (request, { user }) => {
  // Any authenticated user can access this endpoint
  // No role restriction

  const body = await request.json();

  return NextResponse.json({
    message: "Profile updated",
    user_id: user.id,
    updated_fields: Object.keys(body),
  });
});

/**
 * DELETE - Admin only endpoint
 * Example: Delete a resource (critical operation)
 */
export const DELETE = withAdmin(async (request, { user }) => {
  // Only admins can delete resources
  // Returns 403 Forbidden for non-admin users

  const { searchParams } = request.nextUrl;
  const resourceId = searchParams.get("id");

  if (!resourceId) {
    return NextResponse.json(
      { error: "Bad Request", message: "Resource ID required" },
      { status: 400 },
    ) as any;
  }

  return NextResponse.json({
    message: "Resource deleted successfully",
    deleted_by: user.email,
    resource_id: resourceId,
  }) as any;
});
