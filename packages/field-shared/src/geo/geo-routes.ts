/**
 * SAHOOL Geospatial API Routes
 * RESTful endpoints for geospatial operations
 */

import { Router, Request, Response } from "express";
import { geoService } from "./geo-service";

export const geoRoutes = Router();

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Validate latitude value
 */
function isValidLatitude(lat: number): boolean {
    return lat >= -90 && lat <= 90;
}

/**
 * Validate longitude value
 */
function isValidLongitude(lng: number): boolean {
    return lng >= -180 && lng <= 180;
}

/**
 * Validate UUID format
 */
function isValidUUID(uuid: string): boolean {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
}

// ─────────────────────────────────────────────────────────────────────────────
// Query Endpoints
// ─────────────────────────────────────────────────────────────────────────────

/**
 * GET /api/geo/fields/radius
 * Find fields within a radius from a point
 *
 * Query parameters:
 * - lat: Latitude (required)
 * - lng: Longitude (required)
 * - radius: Radius in kilometers (required)
 * - tenantId: Tenant ID filter (optional)
 */
geoRoutes.get("/fields/radius", async (req: Request, res: Response) => {
    try {
        const lat = parseFloat(req.query.lat as string);
        const lng = parseFloat(req.query.lng as string);
        const radius = parseFloat(req.query.radius as string);
        const tenantId = req.query.tenantId as string | undefined;

        // Validation
        if (isNaN(lat) || isNaN(lng) || isNaN(radius)) {
            return res.status(400).json({
                error: "Invalid parameters. lat, lng, and radius must be valid numbers"
            });
        }

        if (!isValidLatitude(lat)) {
            return res.status(400).json({
                error: "Invalid latitude. Must be between -90 and 90"
            });
        }

        if (!isValidLongitude(lng)) {
            return res.status(400).json({
                error: "Invalid longitude. Must be between -180 and 180"
            });
        }

        if (radius <= 0 || radius > 1000) {
            return res.status(400).json({
                error: "Invalid radius. Must be between 0 and 1000 km"
            });
        }

        const fields = await geoService.findFieldsInRadius(lat, lng, radius, tenantId);

        res.json({
            center: { lat, lng },
            radius_km: radius,
            total_fields: fields.length,
            fields
        });
    } catch (error: any) {
        console.error("Error finding fields in radius:", error);
        res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * GET /api/geo/farms/nearby
 * Find nearby farms from a location
 *
 * Query parameters:
 * - lat: Latitude (required)
 * - lng: Longitude (required)
 * - limit: Maximum number of results (optional, default: 10)
 * - tenantId: Tenant ID filter (optional)
 */
geoRoutes.get("/farms/nearby", async (req: Request, res: Response) => {
    try {
        const lat = parseFloat(req.query.lat as string);
        const lng = parseFloat(req.query.lng as string);
        const limit = parseInt(req.query.limit as string) || 10;
        const tenantId = req.query.tenantId as string | undefined;

        // Validation
        if (isNaN(lat) || isNaN(lng)) {
            return res.status(400).json({
                error: "Invalid parameters. lat and lng must be valid numbers"
            });
        }

        if (!isValidLatitude(lat)) {
            return res.status(400).json({
                error: "Invalid latitude. Must be between -90 and 90"
            });
        }

        if (!isValidLongitude(lng)) {
            return res.status(400).json({
                error: "Invalid longitude. Must be between -180 and 180"
            });
        }

        if (limit <= 0 || limit > 100) {
            return res.status(400).json({
                error: "Invalid limit. Must be between 1 and 100"
            });
        }

        const farms = await geoService.findNearbyFarms(lat, lng, limit, tenantId);

        res.json({
            location: { lat, lng },
            limit,
            total_farms: farms.length,
            farms
        });
    } catch (error: any) {
        console.error("Error finding nearby farms:", error);
        res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * GET /api/geo/fields/:fieldId/area
 * Calculate the area of a field
 *
 * Path parameters:
 * - fieldId: UUID of the field
 */
geoRoutes.get("/fields/:fieldId/area", async (req: Request, res: Response) => {
    try {
        const { fieldId } = req.params;

        if (!isValidUUID(fieldId)) {
            return res.status(400).json({
                error: "Invalid field ID format"
            });
        }

        const result = await geoService.calculateFieldArea(fieldId);
        res.json(result);
    } catch (error: any) {
        console.error("Error calculating field area:", error);
        if (error.message.includes("not found")) {
            res.status(404).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message || "Internal server error" });
        }
    }
});

/**
 * POST /api/geo/fields/:fieldId/contains-point
 * Check if a point is inside a field boundary
 *
 * Path parameters:
 * - fieldId: UUID of the field
 *
 * Body:
 * - lat: Latitude
 * - lng: Longitude
 */
geoRoutes.post("/fields/:fieldId/contains-point", async (req: Request, res: Response) => {
    try {
        const { fieldId } = req.params;
        const { lat, lng } = req.body;

        if (!isValidUUID(fieldId)) {
            return res.status(400).json({
                error: "Invalid field ID format"
            });
        }

        if (typeof lat !== "number" || typeof lng !== "number") {
            return res.status(400).json({
                error: "lat and lng must be numbers"
            });
        }

        if (!isValidLatitude(lat) || !isValidLongitude(lng)) {
            return res.status(400).json({
                error: "Invalid coordinates"
            });
        }

        const result = await geoService.checkPointInField(lat, lng, fieldId);
        res.json(result);
    } catch (error: any) {
        console.error("Error checking point in field:", error);
        res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * GET /api/geo/fields/bbox
 * Find fields within a bounding box
 *
 * Query parameters:
 * - minLat: Minimum latitude (south)
 * - minLng: Minimum longitude (west)
 * - maxLat: Maximum latitude (north)
 * - maxLng: Maximum longitude (east)
 * - tenantId: Tenant ID filter (optional)
 */
geoRoutes.get("/fields/bbox", async (req: Request, res: Response) => {
    try {
        const minLat = parseFloat(req.query.minLat as string);
        const minLng = parseFloat(req.query.minLng as string);
        const maxLat = parseFloat(req.query.maxLat as string);
        const maxLng = parseFloat(req.query.maxLng as string);
        const tenantId = req.query.tenantId as string | undefined;

        // Validation
        if (isNaN(minLat) || isNaN(minLng) || isNaN(maxLat) || isNaN(maxLng)) {
            return res.status(400).json({
                error: "Invalid parameters. All coordinates must be valid numbers"
            });
        }

        if (!isValidLatitude(minLat) || !isValidLatitude(maxLat) ||
            !isValidLongitude(minLng) || !isValidLongitude(maxLng)) {
            return res.status(400).json({
                error: "Invalid coordinates"
            });
        }

        if (minLat >= maxLat || minLng >= maxLng) {
            return res.status(400).json({
                error: "Invalid bounding box. Min values must be less than max values"
            });
        }

        const fields = await geoService.findFieldsInBBox(minLat, minLng, maxLat, maxLng, tenantId);

        res.json({
            bbox: { minLat, minLng, maxLat, maxLng },
            total_fields: fields.length,
            fields
        });
    } catch (error: any) {
        console.error("Error finding fields in bbox:", error);
        res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * GET /api/geo/fields/:fieldId1/distance/:fieldId2
 * Calculate distance between two fields
 *
 * Path parameters:
 * - fieldId1: UUID of the first field
 * - fieldId2: UUID of the second field
 */
geoRoutes.get("/fields/:fieldId1/distance/:fieldId2", async (req: Request, res: Response) => {
    try {
        const { fieldId1, fieldId2 } = req.params;

        if (!isValidUUID(fieldId1) || !isValidUUID(fieldId2)) {
            return res.status(400).json({
                error: "Invalid field ID format"
            });
        }

        if (fieldId1 === fieldId2) {
            return res.status(400).json({
                error: "Cannot calculate distance between the same field"
            });
        }

        const result = await geoService.calculateFieldsDistance(fieldId1, fieldId2);
        res.json(result);
    } catch (error: any) {
        console.error("Error calculating fields distance:", error);
        if (error.message.includes("not found") || error.message.includes("Could not calculate")) {
            res.status(404).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message || "Internal server error" });
        }
    }
});

/**
 * GET /api/geo/region/stats
 * Get field statistics for a region
 *
 * Query parameters:
 * - minLat: Minimum latitude (south)
 * - minLng: Minimum longitude (west)
 * - maxLat: Maximum latitude (north)
 * - maxLng: Maximum longitude (east)
 * - tenantId: Tenant ID filter (optional)
 */
geoRoutes.get("/region/stats", async (req: Request, res: Response) => {
    try {
        const minLat = parseFloat(req.query.minLat as string);
        const minLng = parseFloat(req.query.minLng as string);
        const maxLat = parseFloat(req.query.maxLat as string);
        const maxLng = parseFloat(req.query.maxLng as string);
        const tenantId = req.query.tenantId as string | undefined;

        // Validation
        if (isNaN(minLat) || isNaN(minLng) || isNaN(maxLat) || isNaN(maxLng)) {
            return res.status(400).json({
                error: "Invalid parameters. All coordinates must be valid numbers"
            });
        }

        if (!isValidLatitude(minLat) || !isValidLatitude(maxLat) ||
            !isValidLongitude(minLng) || !isValidLongitude(maxLng)) {
            return res.status(400).json({
                error: "Invalid coordinates"
            });
        }

        if (minLat >= maxLat || minLng >= maxLng) {
            return res.status(400).json({
                error: "Invalid bounding box"
            });
        }

        const stats = await geoService.getRegionFieldStats(minLat, minLng, maxLat, maxLng, tenantId);

        res.json({
            region: { minLat, minLng, maxLat, maxLng },
            statistics: stats
        });
    } catch (error: any) {
        console.error("Error getting region stats:", error);
        res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * GET /api/geo/fields/:fieldId/geojson
 * Get GeoJSON representation of a field
 *
 * Path parameters:
 * - fieldId: UUID of the field
 */
geoRoutes.get("/fields/:fieldId/geojson", async (req: Request, res: Response) => {
    try {
        const { fieldId } = req.params;

        if (!isValidUUID(fieldId)) {
            return res.status(400).json({
                error: "Invalid field ID format"
            });
        }

        const geojson = await geoService.getFieldGeoJSON(fieldId);
        res.json(geojson);
    } catch (error: any) {
        console.error("Error getting field GeoJSON:", error);
        if (error.message.includes("not found")) {
            res.status(404).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message || "Internal server error" });
        }
    }
});

/**
 * GET /api/geo/farms/:farmId/geojson
 * Get GeoJSON representation of a farm
 *
 * Path parameters:
 * - farmId: UUID of the farm
 */
geoRoutes.get("/farms/:farmId/geojson", async (req: Request, res: Response) => {
    try {
        const { farmId } = req.params;

        if (!isValidUUID(farmId)) {
            return res.status(400).json({
                error: "Invalid farm ID format"
            });
        }

        const geojson = await geoService.getFarmGeoJSON(farmId);
        res.json(geojson);
    } catch (error: any) {
        console.error("Error getting farm GeoJSON:", error);
        if (error.message.includes("not found")) {
            res.status(404).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message || "Internal server error" });
        }
    }
});

/**
 * GET /api/geo/farms/:farmId/fields
 * Get all fields for a farm with their boundaries
 *
 * Path parameters:
 * - farmId: UUID of the farm
 */
geoRoutes.get("/farms/:farmId/fields", async (req: Request, res: Response) => {
    try {
        const { farmId } = req.params;

        if (!isValidUUID(farmId)) {
            return res.status(400).json({
                error: "Invalid farm ID format"
            });
        }

        const fields = await geoService.getFarmFields(farmId);

        res.json({
            farm_id: farmId,
            total_fields: fields.length,
            fields
        });
    } catch (error: any) {
        console.error("Error getting farm fields:", error);
        res.status(500).json({ error: error.message || "Internal server error" });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// Mutation Endpoints
// ─────────────────────────────────────────────────────────────────────────────

/**
 * POST /api/geo/fields
 * Create a field with GeoJSON boundary
 *
 * Body:
 * - name: Field name
 * - tenant_id: Tenant ID
 * - crop_type: Crop type
 * - owner_id: Owner ID (optional)
 * - farm_id: Farm ID (optional)
 * - boundary_geojson: GeoJSON Polygon object
 */
geoRoutes.post("/fields", async (req: Request, res: Response) => {
    try {
        const { name, tenant_id, crop_type, owner_id, farm_id, boundary_geojson } = req.body;

        // Validation
        if (!name || !tenant_id || !crop_type || !boundary_geojson) {
            return res.status(400).json({
                error: "Missing required fields: name, tenant_id, crop_type, boundary_geojson"
            });
        }

        if (farm_id && !isValidUUID(farm_id)) {
            return res.status(400).json({
                error: "Invalid farm ID format"
            });
        }

        const field = await geoService.createFieldWithBoundary({
            name,
            tenant_id,
            crop_type,
            owner_id,
            farm_id,
            boundary_geojson
        });

        res.status(201).json(field);
    } catch (error: any) {
        console.error("Error creating field:", error);
        res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * PUT /api/geo/fields/:fieldId/boundary
 * Update field boundary
 *
 * Path parameters:
 * - fieldId: UUID of the field
 *
 * Body:
 * - boundary_geojson: GeoJSON Polygon object
 */
geoRoutes.put("/fields/:fieldId/boundary", async (req: Request, res: Response) => {
    try {
        const { fieldId } = req.params;
        const { boundary_geojson } = req.body;

        if (!isValidUUID(fieldId)) {
            return res.status(400).json({
                error: "Invalid field ID format"
            });
        }

        if (!boundary_geojson) {
            return res.status(400).json({
                error: "Missing required field: boundary_geojson"
            });
        }

        const field = await geoService.updateFieldBoundary(fieldId, boundary_geojson);
        res.json(field);
    } catch (error: any) {
        console.error("Error updating field boundary:", error);
        if (error.message.includes("not found")) {
            res.status(404).json({ error: error.message });
        } else {
            res.status(500).json({ error: error.message || "Internal server error" });
        }
    }
});

/**
 * POST /api/geo/farms
 * Create a farm with location
 *
 * Body:
 * - name: Farm name
 * - tenant_id: Tenant ID
 * - owner_id: Owner ID
 * - location_lat: Latitude
 * - location_lng: Longitude
 * - boundary_geojson: GeoJSON Polygon object (optional)
 * - address: Address (optional)
 * - phone: Phone number (optional)
 * - email: Email (optional)
 */
geoRoutes.post("/farms", async (req: Request, res: Response) => {
    try {
        const {
            name,
            tenant_id,
            owner_id,
            location_lat,
            location_lng,
            boundary_geojson,
            address,
            phone,
            email
        } = req.body;

        // Validation
        if (!name || !tenant_id || !owner_id || typeof location_lat !== "number" || typeof location_lng !== "number") {
            return res.status(400).json({
                error: "Missing required fields: name, tenant_id, owner_id, location_lat, location_lng"
            });
        }

        if (!isValidLatitude(location_lat) || !isValidLongitude(location_lng)) {
            return res.status(400).json({
                error: "Invalid coordinates"
            });
        }

        const farm = await geoService.createFarmWithLocation({
            name,
            tenant_id,
            owner_id,
            location_lat,
            location_lng,
            boundary_geojson,
            address,
            phone,
            email
        });

        res.status(201).json(farm);
    } catch (error: any) {
        console.error("Error creating farm:", error);
        res.status(500).json({ error: error.message || "Internal server error" });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// Export routes
// ─────────────────────────────────────────────────────────────────────────────

export default geoRoutes;
