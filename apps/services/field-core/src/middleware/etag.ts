import { Request, Response, NextFunction } from "express";
import crypto from "crypto";

/**
 * ETag Middleware for SAHOOL Field Core API
 *
 * Implements optimistic locking and caching using HTTP ETag headers:
 * - ETag: Generated from entity ID + version using SHA-256
 * - If-Match: Client sends expected ETag for updates (write operations)
 * - If-None-Match: Client sends ETag for conditional GET (read operations)
 * - 409 Conflict: Returned when ETag doesn't match (concurrent modification)
 * - 304 Not Modified: Returned when client has current version (caching)
 * - Cache-Control: Optional header for cache directives
 */

/**
 * Generate ETag from entity ID and version
 * Format: "field:{id}:v{version}"
 */
export function generateETag(id: string, version: number): string {
    const data = `field:${id}:v${version}`;
    const hash = crypto.createHash("sha256").update(data).digest("hex").substring(0, 16);
    return `"${hash}"`;
}

/**
 * Parse ETag from header value
 * Handles both quoted and unquoted ETags
 */
export function parseETag(etag: string | undefined): string | null {
    if (!etag) return null;
    // Remove quotes if present
    return etag.replace(/^["']|["']$/g, "");
}

/**
 * Validate If-Match header against current entity version
 * Returns true if ETags match, false otherwise
 */
export function validateIfMatch(
    ifMatchHeader: string | undefined,
    currentId: string,
    currentVersion: number
): boolean {
    if (!ifMatchHeader) {
        // No If-Match header = allow update (first-write-wins scenario)
        return true;
    }

    const clientETag = parseETag(ifMatchHeader);
    const serverETag = parseETag(generateETag(currentId, currentVersion));

    return clientETag === serverETag;
}

/**
 * Handle If-None-Match header for GET requests (304 Not Modified support)
 * Returns true if client ETag matches server ETag (304 can be returned)
 * Returns false if ETags don't match (200 with content should be returned)
 */
export function handleIfNoneMatch(
    ifNoneMatchHeader: string | undefined,
    currentId: string,
    currentVersion: number
): boolean {
    if (!ifNoneMatchHeader) {
        // No If-None-Match header = return full content
        return false;
    }

    const clientETag = parseETag(ifNoneMatchHeader);
    const serverETag = parseETag(generateETag(currentId, currentVersion));

    // Return true if ETags match (client has current version, return 304)
    return clientETag === serverETag;
}

/**
 * Interface for conflict response
 * Enhanced for mobile sync with server_version
 */
export interface ConflictResponse {
    success: false;
    error: "Conflict";
    code: "CONFLICT_VERSION_MISMATCH";
    message: string;
    messageAr: string;
    serverData: object;
    serverETag: string;
    server_version: number;
    serverTime: string;
}

/**
 * Create 409 Conflict response with server data and version
 * This allows the client to see the current server state and resolve the conflict
 *
 * Enhanced for mobile sync:
 * - Includes server_version for version comparison
 * - Includes serverTime for sync tracking
 * - Includes Arabic message for mobile UI
 */
export function createConflictResponse(
    serverEntity: object & { version?: number },
    serverETag: string,
    entityType: string = "field"
): ConflictResponse {
    return {
        success: false,
        error: "Conflict",
        code: "CONFLICT_VERSION_MISMATCH",
        message: `The ${entityType} has been modified by another user. Please refresh and try again.`,
        messageAr: `تم تعديل ${entityType === "field" ? "الحقل" : entityType} بواسطة مستخدم آخر. يرجى التحديث والمحاولة مجدداً.`,
        serverData: serverEntity,
        serverETag: serverETag,
        server_version: serverEntity.version || 0,
        serverTime: new Date().toISOString()
    };
}

/**
 * Middleware to set ETag header on responses
 * Use with res.locals.etag to set the ETag value
 * Also supports Cache-Control header via res.locals.cacheControl
 */
export function setETagHeader(
    _req: Request,
    res: Response,
    next: NextFunction
): void {
    const originalJson = res.json.bind(res);

    res.json = function (body: any): Response {
        // If etag is set in locals, add it to headers
        if (res.locals.etag) {
            res.setHeader("ETag", res.locals.etag);
        }

        // If cacheControl is set in locals, add it to headers
        if (res.locals.cacheControl) {
            res.setHeader("Cache-Control", res.locals.cacheControl);
        }

        return originalJson(body);
    };

    next();
}

/**
 * Extract If-Match header from request
 */
export function getIfMatchHeader(req: Request): string | undefined {
    return req.headers["if-match"] as string | undefined;
}

/**
 * Extract If-None-Match header from request
 */
export function getIfNoneMatchHeader(req: Request): string | undefined {
    return req.headers["if-none-match"] as string | undefined;
}
