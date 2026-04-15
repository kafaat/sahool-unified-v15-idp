/**
 * UserRole Serialization Layer (Prisma <-> Canonical)
 *
 * The Prisma schema defines 8 uppercase UserRole values:
 *   SUPER_ADMIN, ADMIN, MANAGER, AGRONOMIST, FARMER, WORKER, RESEARCHER, VIEWER
 *
 * The frontend (admin portal, web, mobile) expects 5 canonical lowercase values:
 *   admin, manager, farmer, viewer, agronomist
 *
 * This module provides bi-directional mapping:
 *   - toCanonical(): Prisma enum -> canonical lowercase (output serialization)
 *   - toPrisma():    Client input (any case) -> Prisma enum (input normalization)
 */

/**
 * Canonical role values exposed to clients.
 */
export const CANONICAL_ROLES = [
  "admin",
  "manager",
  "farmer",
  "viewer",
  "agronomist",
] as const;

export type CanonicalRole = (typeof CANONICAL_ROLES)[number];

/**
 * Prisma UserRole enum values (mirrors prisma/schema.prisma).
 */
export const PRISMA_ROLES = [
  "SUPER_ADMIN",
  "ADMIN",
  "MANAGER",
  "AGRONOMIST",
  "FARMER",
  "WORKER",
  "RESEARCHER",
  "VIEWER",
] as const;

export type PrismaRole = (typeof PRISMA_ROLES)[number];

/**
 * Prisma -> canonical (output).
 * Collapses legacy/extra backend roles onto the 5 canonical values the
 * frontend understands. SUPER_ADMIN -> admin, WORKER/RESEARCHER -> viewer.
 */
const PRISMA_TO_CANONICAL: Record<PrismaRole, CanonicalRole> = {
  SUPER_ADMIN: "admin",
  ADMIN: "admin",
  MANAGER: "manager",
  AGRONOMIST: "agronomist",
  FARMER: "farmer",
  WORKER: "viewer",
  RESEARCHER: "viewer",
  VIEWER: "viewer",
};

/**
 * Canonical -> Prisma (input).
 */
const CANONICAL_TO_PRISMA: Record<CanonicalRole, PrismaRole> = {
  admin: "ADMIN",
  manager: "MANAGER",
  agronomist: "AGRONOMIST",
  farmer: "FARMER",
  viewer: "VIEWER",
};

/**
 * Normalize a Prisma role value to its canonical lowercase form for API
 * responses. Accepts any string; unknown values fall back to "viewer".
 */
export function toCanonicalRole(value: unknown): CanonicalRole {
  if (typeof value !== "string") {
    return "viewer";
  }
  const upper = value.toUpperCase() as PrismaRole;
  if (upper in PRISMA_TO_CANONICAL) {
    return PRISMA_TO_CANONICAL[upper];
  }
  // Maybe already canonical lowercase
  const lower = value.toLowerCase();
  if ((CANONICAL_ROLES as readonly string[]).includes(lower)) {
    return lower as CanonicalRole;
  }
  return "viewer";
}

/**
 * Normalize an incoming role value (from client input) to the Prisma enum
 * representation used for persistence. Accepts both cases.
 *
 * Returns `undefined` for null/undefined inputs (so callers can preserve
 * "unset" semantics) and throws for unknown values.
 */
export function toPrismaRole(value: unknown): PrismaRole | undefined {
  if (value === null || value === undefined || value === "") {
    return undefined;
  }
  if (typeof value !== "string") {
    throw new Error(`Invalid role type: ${typeof value}`);
  }

  const upper = value.toUpperCase();
  if ((PRISMA_ROLES as readonly string[]).includes(upper)) {
    return upper as PrismaRole;
  }

  const lower = value.toLowerCase() as CanonicalRole;
  if (lower in CANONICAL_TO_PRISMA) {
    return CANONICAL_TO_PRISMA[lower];
  }

  throw new Error(`Unknown role value: ${value}`);
}

/**
 * Serialize a user-shaped object for API responses.
 * - Replaces `role` with its canonical lowercase form.
 * - Strips `passwordHash` if present (defense-in-depth).
 * Accepts any object (Prisma partial selects, etc.).
 */
export function serializeUser<T extends Record<string, any>>(
  user: T | null | undefined,
): (Omit<T, "role" | "passwordHash"> & { role?: CanonicalRole }) | null {
  if (!user) {
    return null;
  }
  const { passwordHash: _pw, role, ...rest } = user as any;
  const out: Record<string, any> = { ...rest };
  if (role !== undefined) {
    out.role = toCanonicalRole(role);
  }
  return out as Omit<T, "role" | "passwordHash"> & { role?: CanonicalRole };
}

/**
 * Serialize a list of users.
 */
export function serializeUsers<T extends Record<string, any>>(
  users: T[] | null | undefined,
): Array<Omit<T, "role" | "passwordHash"> & { role?: CanonicalRole }> {
  if (!users) {
    return [];
  }
  return users
    .map((u) => serializeUser(u))
    .filter((u): u is Omit<T, "role" | "passwordHash"> & { role?: CanonicalRole } => u !== null);
}
