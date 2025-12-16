/**
 * SAHOOL Input Validation Middleware
 * Uses Zod-like validation patterns for request validation
 */

import { Request, Response, NextFunction } from "express";

// Validation error class
export class ValidationError extends Error {
    public errors: ValidationIssue[];

    constructor(errors: ValidationIssue[]) {
        super("Validation failed");
        this.name = "ValidationError";
        this.errors = errors;
    }
}

interface ValidationIssue {
    path: string[];
    message: string;
    code: string;
    expected?: string;
    received?: string;
}

// Type definitions for schema
type SchemaType = "string" | "number" | "boolean" | "array" | "object" | "date";

interface SchemaDefinition {
    type: SchemaType;
    required?: boolean;
    min?: number;
    max?: number;
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    enum?: any[];
    items?: SchemaDefinition;
    properties?: Record<string, SchemaDefinition>;
    custom?: (value: any) => boolean | string;
}

// Schema builder class (Zod-like API)
export class Schema {
    private definition: SchemaDefinition;

    constructor(type: SchemaType) {
        this.definition = { type, required: true };
    }

    static string() {
        return new Schema("string");
    }

    static number() {
        return new Schema("number");
    }

    static boolean() {
        return new Schema("boolean");
    }

    static array(items?: Schema) {
        const schema = new Schema("array");
        if (items) {
            schema.definition.items = items.definition;
        }
        return schema;
    }

    static object(properties: Record<string, Schema>) {
        const schema = new Schema("object");
        schema.definition.properties = {};
        for (const [key, value] of Object.entries(properties)) {
            schema.definition.properties[key] = value.definition;
        }
        return schema;
    }

    optional() {
        this.definition.required = false;
        return this;
    }

    min(value: number) {
        this.definition.min = value;
        return this;
    }

    max(value: number) {
        this.definition.max = value;
        return this;
    }

    minLength(value: number) {
        this.definition.minLength = value;
        return this;
    }

    maxLength(value: number) {
        this.definition.maxLength = value;
        return this;
    }

    pattern(regex: RegExp) {
        this.definition.pattern = regex;
        return this;
    }

    enum(values: any[]) {
        this.definition.enum = values;
        return this;
    }

    custom(validator: (value: any) => boolean | string) {
        this.definition.custom = validator;
        return this;
    }

    // UUID validation helper
    uuid() {
        return this.pattern(/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    }

    // Email validation helper
    email() {
        return this.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
    }

    // Validate a value against this schema
    validate(value: any, path: string[] = []): ValidationIssue[] {
        const errors: ValidationIssue[] = [];
        const def = this.definition;

        // Check required
        if (value === undefined || value === null) {
            if (def.required) {
                errors.push({
                    path,
                    message: "Required field is missing",
                    code: "required",
                    expected: def.type,
                    received: "undefined"
                });
            }
            return errors;
        }

        // Type checking
        const actualType = Array.isArray(value) ? "array" : typeof value;
        if (def.type === "number" && actualType === "string") {
            // Allow string numbers
            if (isNaN(Number(value))) {
                errors.push({
                    path,
                    message: `Expected ${def.type}, received ${actualType}`,
                    code: "invalid_type",
                    expected: def.type,
                    received: actualType
                });
                return errors;
            }
        } else if (def.type !== actualType && !(def.type === "date" && value instanceof Date)) {
            errors.push({
                path,
                message: `Expected ${def.type}, received ${actualType}`,
                code: "invalid_type",
                expected: def.type,
                received: actualType
            });
            return errors;
        }

        // String validations
        if (def.type === "string" && typeof value === "string") {
            if (def.minLength !== undefined && value.length < def.minLength) {
                errors.push({
                    path,
                    message: `String must be at least ${def.minLength} characters`,
                    code: "too_small"
                });
            }
            if (def.maxLength !== undefined && value.length > def.maxLength) {
                errors.push({
                    path,
                    message: `String must be at most ${def.maxLength} characters`,
                    code: "too_big"
                });
            }
            if (def.pattern && !def.pattern.test(value)) {
                errors.push({
                    path,
                    message: "String does not match required pattern",
                    code: "invalid_pattern"
                });
            }
        }

        // Number validations
        if (def.type === "number") {
            const num = Number(value);
            if (def.min !== undefined && num < def.min) {
                errors.push({
                    path,
                    message: `Number must be at least ${def.min}`,
                    code: "too_small"
                });
            }
            if (def.max !== undefined && num > def.max) {
                errors.push({
                    path,
                    message: `Number must be at most ${def.max}`,
                    code: "too_big"
                });
            }
        }

        // Enum validation
        if (def.enum && !def.enum.includes(value)) {
            errors.push({
                path,
                message: `Value must be one of: ${def.enum.join(", ")}`,
                code: "invalid_enum",
                expected: def.enum.join(" | "),
                received: String(value)
            });
        }

        // Array validations
        if (def.type === "array" && Array.isArray(value)) {
            if (def.min !== undefined && value.length < def.min) {
                errors.push({
                    path,
                    message: `Array must have at least ${def.min} items`,
                    code: "too_small"
                });
            }
            if (def.max !== undefined && value.length > def.max) {
                errors.push({
                    path,
                    message: `Array must have at most ${def.max} items`,
                    code: "too_big"
                });
            }
            if (def.items) {
                const itemSchema = new Schema(def.items.type);
                Object.assign(itemSchema.definition, def.items);
                value.forEach((item, index) => {
                    errors.push(...itemSchema.validate(item, [...path, String(index)]));
                });
            }
        }

        // Object validations
        if (def.type === "object" && def.properties && typeof value === "object") {
            for (const [key, propDef] of Object.entries(def.properties)) {
                const propSchema = new Schema(propDef.type);
                Object.assign(propSchema.definition, propDef);
                errors.push(...propSchema.validate(value[key], [...path, key]));
            }
        }

        // Custom validation
        if (def.custom) {
            const result = def.custom(value);
            if (result !== true) {
                errors.push({
                    path,
                    message: typeof result === "string" ? result : "Custom validation failed",
                    code: "custom"
                });
            }
        }

        return errors;
    }

    parse(value: any): any {
        const errors = this.validate(value);
        if (errors.length > 0) {
            throw new ValidationError(errors);
        }
        return value;
    }

    safeParse(value: any): { success: true; data: any } | { success: false; errors: ValidationIssue[] } {
        const errors = this.validate(value);
        if (errors.length > 0) {
            return { success: false, errors };
        }
        return { success: true, data: value };
    }
}

// Pre-defined schemas for SAHOOL entities

export const FieldCreateSchema = Schema.object({
    name: Schema.string().minLength(1).maxLength(100),
    tenantId: Schema.string().uuid(),
    cropType: Schema.string().minLength(1).maxLength(50),
    coordinates: Schema.array(
        Schema.array(Schema.number())
    ).min(3).optional(),
    ownerId: Schema.string().uuid().optional(),
    irrigationType: Schema.string().enum(["drip", "sprinkler", "flood", "none"]).optional(),
    soilType: Schema.string().maxLength(50).optional(),
    plantingDate: Schema.string().optional(),
    expectedHarvest: Schema.string().optional(),
    metadata: Schema.object({}).optional()
});

export const FieldUpdateSchema = Schema.object({
    name: Schema.string().minLength(1).maxLength(100).optional(),
    cropType: Schema.string().minLength(1).maxLength(50).optional(),
    status: Schema.string().enum(["active", "fallow", "preparing", "harvested"]).optional(),
    irrigationType: Schema.string().enum(["drip", "sprinkler", "flood", "none"]).optional(),
    soilType: Schema.string().maxLength(50).optional(),
    plantingDate: Schema.string().optional(),
    expectedHarvest: Schema.string().optional(),
    metadata: Schema.object({}).optional()
});

export const NdviUpdateSchema = Schema.object({
    value: Schema.number().min(-1).max(1),
    source: Schema.string().maxLength(50).optional()
});

export const PaginationSchema = Schema.object({
    limit: Schema.number().min(1).max(100).optional(),
    offset: Schema.number().min(0).optional()
});

// Express middleware factory
export function validateBody(schema: Schema) {
    return (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse(req.body);

        if (!result.success) {
            return res.status(400).json({
                success: false,
                error: "Validation failed",
                error_ar: "فشل التحقق من البيانات",
                details: result.errors.map(e => ({
                    field: e.path.join("."),
                    message: e.message,
                    code: e.code
                }))
            });
        }

        req.body = result.data;
        next();
    };
}

export function validateQuery(schema: Schema) {
    return (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse(req.query);

        if (!result.success) {
            return res.status(400).json({
                success: false,
                error: "Invalid query parameters",
                error_ar: "معاملات استعلام غير صالحة",
                details: result.errors.map(e => ({
                    field: e.path.join("."),
                    message: e.message,
                    code: e.code
                }))
            });
        }

        next();
    };
}

export function validateParams(schema: Schema) {
    return (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse(req.params);

        if (!result.success) {
            return res.status(400).json({
                success: false,
                error: "Invalid path parameters",
                error_ar: "معاملات مسار غير صالحة",
                details: result.errors.map(e => ({
                    field: e.path.join("."),
                    message: e.message,
                    code: e.code
                }))
            });
        }

        next();
    };
}

// ═══════════════════════════════════════════════════════════════════════════
// GEOSPATIAL VALIDATION - التحقق الجغرافي المكاني
// ═══════════════════════════════════════════════════════════════════════════

export interface GeoValidationResult {
    valid: boolean;
    errors: string[];
    errors_ar: string[];
    warnings?: string[];
}

export interface Coordinate {
    lat: number;
    lng: number;
}

/**
 * Validate latitude value (-90 to 90)
 */
export function validateLatitude(lat: number): GeoValidationResult {
    const errors: string[] = [];
    const errors_ar: string[] = [];

    if (typeof lat !== "number" || isNaN(lat)) {
        errors.push("Latitude must be a valid number");
        errors_ar.push("خط العرض يجب أن يكون رقماً صالحاً");
    } else if (lat < -90 || lat > 90) {
        errors.push("Latitude must be between -90 and 90");
        errors_ar.push("خط العرض يجب أن يكون بين -90 و 90");
    }

    return { valid: errors.length === 0, errors, errors_ar };
}

/**
 * Validate longitude value (-180 to 180)
 */
export function validateLongitude(lng: number): GeoValidationResult {
    const errors: string[] = [];
    const errors_ar: string[] = [];

    if (typeof lng !== "number" || isNaN(lng)) {
        errors.push("Longitude must be a valid number");
        errors_ar.push("خط الطول يجب أن يكون رقماً صالحاً");
    } else if (lng < -180 || lng > 180) {
        errors.push("Longitude must be between -180 and 180");
        errors_ar.push("خط الطول يجب أن يكون بين -180 و 180");
    }

    return { valid: errors.length === 0, errors, errors_ar };
}

/**
 * Validate a coordinate pair [lng, lat] (GeoJSON format)
 */
export function validateCoordinatePair(coord: [number, number]): GeoValidationResult {
    const errors: string[] = [];
    const errors_ar: string[] = [];

    if (!Array.isArray(coord) || coord.length !== 2) {
        errors.push("Coordinate must be an array of [longitude, latitude]");
        errors_ar.push("الإحداثي يجب أن يكون مصفوفة [خط الطول، خط العرض]");
        return { valid: false, errors, errors_ar };
    }

    const [lng, lat] = coord;

    const latResult = validateLatitude(lat);
    const lngResult = validateLongitude(lng);

    return {
        valid: latResult.valid && lngResult.valid,
        errors: [...lngResult.errors, ...latResult.errors],
        errors_ar: [...lngResult.errors_ar, ...latResult.errors_ar]
    };
}

/**
 * Validate polygon coordinates (GeoJSON format)
 * - Must have at least 4 points (3 unique + closing point)
 * - First and last point must be the same (closed polygon)
 * - All coordinates must be valid
 */
export function validatePolygonCoordinates(coordinates: number[][][]): GeoValidationResult {
    const errors: string[] = [];
    const errors_ar: string[] = [];
    const warnings: string[] = [];

    // Check if coordinates is an array
    if (!Array.isArray(coordinates)) {
        errors.push("Polygon coordinates must be an array");
        errors_ar.push("إحداثيات المضلع يجب أن تكون مصفوفة");
        return { valid: false, errors, errors_ar };
    }

    // GeoJSON Polygon has an outer ring at index 0
    if (coordinates.length === 0) {
        errors.push("Polygon must have at least one ring (outer boundary)");
        errors_ar.push("المضلع يجب أن يحتوي على حلقة خارجية واحدة على الأقل");
        return { valid: false, errors, errors_ar };
    }

    const outerRing = coordinates[0];

    // Check minimum points (4 = 3 unique + 1 closing)
    if (!Array.isArray(outerRing) || outerRing.length < 4) {
        errors.push("Polygon must have at least 4 points (3 unique vertices + closing point)");
        errors_ar.push("المضلع يجب أن يحتوي على 4 نقاط على الأقل (3 رؤوس فريدة + نقطة إغلاق)");
        return { valid: false, errors, errors_ar };
    }

    // Validate each coordinate
    for (let i = 0; i < outerRing.length; i++) {
        const coord = outerRing[i];
        const result = validateCoordinatePair(coord as [number, number]);
        if (!result.valid) {
            errors.push(`Invalid coordinate at index ${i}: ${result.errors.join(", ")}`);
            errors_ar.push(`إحداثي غير صالح في الموقع ${i}: ${result.errors_ar.join("، ")}`);
        }
    }

    // Check if polygon is closed (first point equals last point)
    const firstPoint = outerRing[0];
    const lastPoint = outerRing[outerRing.length - 1];

    if (firstPoint[0] !== lastPoint[0] || firstPoint[1] !== lastPoint[1]) {
        errors.push("Polygon must be closed (first and last coordinates must be identical)");
        errors_ar.push("المضلع يجب أن يكون مغلقاً (الإحداثي الأول والأخير يجب أن يكونا متطابقين)");
    }

    // Check for self-intersection (simplified check)
    if (outerRing.length > 4 && hasSelfIntersection(outerRing)) {
        errors.push("Polygon has self-intersection (invalid geometry)");
        errors_ar.push("المضلع يحتوي على تقاطع ذاتي (شكل هندسي غير صالح)");
    }

    // Warning for very large polygons
    if (outerRing.length > 1000) {
        warnings.push("Polygon has many vertices, consider simplifying");
    }

    return { valid: errors.length === 0, errors, errors_ar, warnings };
}

/**
 * Validate GeoJSON object
 */
export function validateGeoJSON(geojson: any): GeoValidationResult {
    const errors: string[] = [];
    const errors_ar: string[] = [];

    if (!geojson || typeof geojson !== "object") {
        errors.push("GeoJSON must be an object");
        errors_ar.push("GeoJSON يجب أن يكون كائناً");
        return { valid: false, errors, errors_ar };
    }

    // Check type
    if (!geojson.type) {
        errors.push("GeoJSON must have a 'type' property");
        errors_ar.push("GeoJSON يجب أن يحتوي على خاصية 'type'");
        return { valid: false, errors, errors_ar };
    }

    const validTypes = ["Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon", "GeometryCollection", "Feature", "FeatureCollection"];
    if (!validTypes.includes(geojson.type)) {
        errors.push(`Invalid GeoJSON type: ${geojson.type}. Must be one of: ${validTypes.join(", ")}`);
        errors_ar.push(`نوع GeoJSON غير صالح: ${geojson.type}`);
        return { valid: false, errors, errors_ar };
    }

    // Validate coordinates based on type
    if (geojson.type === "Polygon") {
        if (!geojson.coordinates) {
            errors.push("Polygon must have 'coordinates' property");
            errors_ar.push("المضلع يجب أن يحتوي على خاصية 'coordinates'");
            return { valid: false, errors, errors_ar };
        }
        return validatePolygonCoordinates(geojson.coordinates);
    }

    if (geojson.type === "Point") {
        if (!geojson.coordinates) {
            errors.push("Point must have 'coordinates' property");
            errors_ar.push("النقطة يجب أن تحتوي على خاصية 'coordinates'");
            return { valid: false, errors, errors_ar };
        }
        return validateCoordinatePair(geojson.coordinates);
    }

    if (geojson.type === "Feature") {
        if (!geojson.geometry) {
            errors.push("Feature must have 'geometry' property");
            errors_ar.push("Feature يجب أن يحتوي على خاصية 'geometry'");
            return { valid: false, errors, errors_ar };
        }
        return validateGeoJSON(geojson.geometry);
    }

    return { valid: true, errors: [], errors_ar: [] };
}

/**
 * Calculate approximate area of polygon in hectares
 * Uses Shoelace formula with latitude correction
 */
export function calculatePolygonArea(coordinates: number[][]): number {
    if (!coordinates || coordinates.length < 3) return 0;

    // Earth's radius in meters
    const R = 6371000;

    let area = 0;
    const n = coordinates.length;

    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        const [lng1, lat1] = coordinates[i];
        const [lng2, lat2] = coordinates[j];

        // Convert to radians
        const lat1Rad = lat1 * Math.PI / 180;
        const lat2Rad = lat2 * Math.PI / 180;
        const lng1Rad = lng1 * Math.PI / 180;
        const lng2Rad = lng2 * Math.PI / 180;

        // Spherical excess formula
        area += (lng2Rad - lng1Rad) * (2 + Math.sin(lat1Rad) + Math.sin(lat2Rad));
    }

    area = Math.abs(area * R * R / 2);

    // Convert to hectares (1 hectare = 10,000 m²)
    return area / 10000;
}

/**
 * Check if polygon has self-intersection (simplified)
 */
function hasSelfIntersection(ring: number[][]): boolean {
    const n = ring.length - 1; // Exclude closing point

    for (let i = 0; i < n - 1; i++) {
        for (let j = i + 2; j < n; j++) {
            // Skip adjacent segments
            if (i === 0 && j === n - 1) continue;

            if (segmentsIntersect(ring[i], ring[i + 1], ring[j], ring[(j + 1) % n])) {
                return true;
            }
        }
    }
    return false;
}

/**
 * Check if two line segments intersect
 */
function segmentsIntersect(p1: number[], p2: number[], p3: number[], p4: number[]): boolean {
    const d1 = direction(p3, p4, p1);
    const d2 = direction(p3, p4, p2);
    const d3 = direction(p1, p2, p3);
    const d4 = direction(p1, p2, p4);

    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
        ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
        return true;
    }
    return false;
}

function direction(p1: number[], p2: number[], p3: number[]): number {
    return (p3[0] - p1[0]) * (p2[1] - p1[1]) - (p2[0] - p1[0]) * (p3[1] - p1[1]);
}

/**
 * Middleware to validate GeoJSON boundary in request body
 */
export function validateBoundary() {
    return (req: Request, res: Response, next: NextFunction) => {
        const { boundary, coordinates } = req.body;

        // If boundary is provided as GeoJSON
        if (boundary) {
            const result = validateGeoJSON(boundary);
            if (!result.valid) {
                return res.status(400).json({
                    success: false,
                    error: "Invalid boundary geometry",
                    error_ar: "شكل الحدود غير صالح",
                    details: result.errors.map((e, i) => ({
                        message: e,
                        message_ar: result.errors_ar[i]
                    }))
                });
            }
        }

        // If coordinates are provided as array
        if (coordinates && Array.isArray(coordinates)) {
            // Convert to GeoJSON format if needed
            const geoJsonCoords = [coordinates.map((c: any) => [c[0] || c.lng, c[1] || c.lat])];

            // Ensure closed polygon
            const first = geoJsonCoords[0][0];
            const last = geoJsonCoords[0][geoJsonCoords[0].length - 1];
            if (first[0] !== last[0] || first[1] !== last[1]) {
                geoJsonCoords[0].push([...first]);
            }

            const result = validatePolygonCoordinates(geoJsonCoords);
            if (!result.valid) {
                return res.status(400).json({
                    success: false,
                    error: "Invalid polygon coordinates",
                    error_ar: "إحداثيات المضلع غير صالحة",
                    details: result.errors.map((e, i) => ({
                        message: e,
                        message_ar: result.errors_ar[i]
                    }))
                });
            }

            // Store validated GeoJSON in body
            req.body.validatedBoundary = {
                type: "Polygon",
                coordinates: geoJsonCoords
            };
        }

        next();
    };
}

/**
 * Enhanced Field Create Schema with geospatial validation
 */
export const FieldCreateSchemaWithGeo = Schema.object({
    name: Schema.string().minLength(1).maxLength(255),
    tenantId: Schema.string().minLength(1).maxLength(100),
    cropType: Schema.string().minLength(1).maxLength(100),
    ownerId: Schema.string().uuid().optional(),
    coordinates: Schema.array(Schema.array(Schema.number())).min(3).optional(),
    boundary: Schema.object({}).optional(), // Will be validated by validateBoundary middleware
    irrigationType: Schema.string().enum(["drip", "sprinkler", "flood", "pivot", "furrow", "none"]).optional(),
    soilType: Schema.string().maxLength(100).optional(),
    plantingDate: Schema.string().optional(),
    expectedHarvest: Schema.string().optional(),
    metadata: Schema.object({}).optional()
}).custom((value) => {
    // Require either coordinates or boundary
    if (!value.coordinates && !value.boundary) {
        return "Either 'coordinates' or 'boundary' is required";
    }
    return true;
});

/**
 * Nearby query validation schema
 */
export const NearbyQuerySchema = Schema.object({
    lat: Schema.number().min(-90).max(90),
    lng: Schema.number().min(-180).max(180),
    radius: Schema.number().min(1).max(100000).optional() // meters, default 5000
});

/**
 * UUID parameter validation
 */
export const UuidParamSchema = Schema.object({
    id: Schema.string().uuid()
});
