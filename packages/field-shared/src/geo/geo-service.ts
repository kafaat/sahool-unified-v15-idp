/**
 * SAHOOL Geospatial Service
 * PostGIS-powered geospatial operations for fields and farms
 */

import { AppDataSource } from "../data-source";

// ─────────────────────────────────────────────────────────────────────────────
// Type Definitions
// ─────────────────────────────────────────────────────────────────────────────

export interface FieldInRadius {
    field_id: string;
    field_name: string;
    distance_km: number;
    area_hectares: number;
    crop_type: string;
    centroid_lat: number;
    centroid_lng: number;
}

export interface NearbyFarm {
    farm_id: string;
    farm_name: string;
    distance_km: number;
    total_area_hectares: number;
    location_lat: number;
    location_lng: number;
    phone: string | null;
    email: string | null;
}

export interface FieldInBBox {
    field_id: string;
    field_name: string;
    area_hectares: number;
    crop_type: string;
    boundary_geojson: any;
}

export interface RegionStats {
    total_fields: string;
    total_area_ha: number;
    avg_field_size_ha: number;
    crop_distribution: Record<string, number>;
}

export interface FieldAreaResult {
    field_id: string;
    area_hectares: number;
    calculated_at: string;
}

export interface PointInFieldResult {
    field_id: string;
    is_inside: boolean;
    checked_at: string;
}

export interface FieldsDistanceResult {
    field_id_1: string;
    field_id_2: string;
    distance_km: number;
    calculated_at: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// GeoService Class
// ─────────────────────────────────────────────────────────────────────────────

export class GeoService {
    /**
     * Find fields within a radius from a point
     * @param lat - Latitude of the center point
     * @param lng - Longitude of the center point
     * @param radiusKm - Radius in kilometers
     * @param tenantId - Optional tenant filter
     * @returns Array of fields within the radius, sorted by distance
     */
    async findFieldsInRadius(
        lat: number,
        lng: number,
        radiusKm: number,
        tenantId?: string
    ): Promise<FieldInRadius[]> {
        const query = `
            SELECT * FROM find_fields_in_radius($1, $2, $3, $4)
        `;

        const result = await AppDataSource.query(query, [
            lat,
            lng,
            radiusKm,
            tenantId || null
        ]);

        return result;
    }

    /**
     * Find nearby farms from a location
     * @param lat - Latitude of the center point
     * @param lng - Longitude of the center point
     * @param limit - Maximum number of farms to return
     * @param tenantId - Optional tenant filter
     * @returns Array of nearby farms, sorted by distance
     */
    async findNearbyFarms(
        lat: number,
        lng: number,
        limit: number = 10,
        tenantId?: string
    ): Promise<NearbyFarm[]> {
        const query = `
            SELECT * FROM find_nearby_farms($1, $2, $3, $4)
        `;

        const result = await AppDataSource.query(query, [
            lat,
            lng,
            limit,
            tenantId || null
        ]);

        return result;
    }

    /**
     * Calculate the area of a field
     * @param fieldId - UUID of the field
     * @returns Field area in hectares
     */
    async calculateFieldArea(fieldId: string): Promise<FieldAreaResult> {
        const query = `
            SELECT get_field_area($1) as area_hectares
        `;

        const result = await AppDataSource.query(query, [fieldId]);

        if (!result || result.length === 0 || result[0].area_hectares === null) {
            throw new Error(`Field with ID ${fieldId} not found or has no boundary`);
        }

        return {
            field_id: fieldId,
            area_hectares: parseFloat(result[0].area_hectares),
            calculated_at: new Date().toISOString()
        };
    }

    /**
     * Check if a point is inside a field boundary
     * @param lat - Latitude of the point
     * @param lng - Longitude of the point
     * @param fieldId - UUID of the field
     * @returns Boolean indicating if the point is inside the field
     */
    async checkPointInField(
        lat: number,
        lng: number,
        fieldId: string
    ): Promise<PointInFieldResult> {
        const query = `
            SELECT check_point_in_field($1, $2, $3) as is_inside
        `;

        const result = await AppDataSource.query(query, [lat, lng, fieldId]);

        return {
            field_id: fieldId,
            is_inside: result[0]?.is_inside || false,
            checked_at: new Date().toISOString()
        };
    }

    /**
     * Find fields within a bounding box
     * @param minLat - Minimum latitude (south)
     * @param minLng - Minimum longitude (west)
     * @param maxLat - Maximum latitude (north)
     * @param maxLng - Maximum longitude (east)
     * @param tenantId - Optional tenant filter
     * @returns Array of fields within the bounding box
     */
    async findFieldsInBBox(
        minLat: number,
        minLng: number,
        maxLat: number,
        maxLng: number,
        tenantId?: string
    ): Promise<FieldInBBox[]> {
        const query = `
            SELECT * FROM find_fields_in_bbox($1, $2, $3, $4, $5)
        `;

        const result = await AppDataSource.query(query, [
            minLat,
            minLng,
            maxLat,
            maxLng,
            tenantId || null
        ]);

        return result;
    }

    /**
     * Calculate distance between two fields
     * @param fieldId1 - UUID of the first field
     * @param fieldId2 - UUID of the second field
     * @returns Distance in kilometers
     */
    async calculateFieldsDistance(
        fieldId1: string,
        fieldId2: string
    ): Promise<FieldsDistanceResult> {
        const query = `
            SELECT calculate_fields_distance($1, $2) as distance_km
        `;

        const result = await AppDataSource.query(query, [fieldId1, fieldId2]);

        if (!result || result.length === 0 || result[0].distance_km === null) {
            throw new Error(`Could not calculate distance between fields`);
        }

        return {
            field_id_1: fieldId1,
            field_id_2: fieldId2,
            distance_km: parseFloat(result[0].distance_km),
            calculated_at: new Date().toISOString()
        };
    }

    /**
     * Get field statistics for a region (bounding box)
     * @param minLat - Minimum latitude (south)
     * @param minLng - Minimum longitude (west)
     * @param maxLat - Maximum latitude (north)
     * @param maxLng - Maximum longitude (east)
     * @param tenantId - Optional tenant filter
     * @returns Regional statistics
     */
    async getRegionFieldStats(
        minLat: number,
        minLng: number,
        maxLat: number,
        maxLng: number,
        tenantId?: string
    ): Promise<RegionStats> {
        const query = `
            SELECT * FROM get_region_field_stats($1, $2, $3, $4, $5)
        `;

        const result = await AppDataSource.query(query, [
            minLat,
            minLng,
            maxLat,
            maxLng,
            tenantId || null
        ]);

        if (!result || result.length === 0) {
            return {
                total_fields: "0",
                total_area_ha: 0,
                avg_field_size_ha: 0,
                crop_distribution: {}
            };
        }

        return result[0];
    }

    /**
     * Get GeoJSON representation of a field boundary
     * @param fieldId - UUID of the field
     * @returns GeoJSON object
     */
    async getFieldGeoJSON(fieldId: string): Promise<any> {
        const query = `
            SELECT
                id,
                name,
                ST_AsGeoJSON(boundary)::jsonb as boundary_geojson,
                ST_AsGeoJSON(centroid)::jsonb as centroid_geojson,
                area_hectares,
                crop_type
            FROM fields
            WHERE id = $1 AND is_deleted = FALSE
        `;

        const result = await AppDataSource.query(query, [fieldId]);

        if (!result || result.length === 0) {
            throw new Error(`Field with ID ${fieldId} not found`);
        }

        return result[0];
    }

    /**
     * Get GeoJSON representation of a farm
     * @param farmId - UUID of the farm
     * @returns GeoJSON object
     */
    async getFarmGeoJSON(farmId: string): Promise<any> {
        const query = `
            SELECT
                id,
                name,
                ST_AsGeoJSON(location)::jsonb as location_geojson,
                ST_AsGeoJSON(boundary)::jsonb as boundary_geojson,
                total_area_hectares,
                address,
                phone,
                email
            FROM farms
            WHERE id = $1 AND is_deleted = FALSE
        `;

        const result = await AppDataSource.query(query, [farmId]);

        if (!result || result.length === 0) {
            throw new Error(`Farm with ID ${farmId} not found`);
        }

        return result[0];
    }

    /**
     * Get all fields for a farm with their boundaries
     * @param farmId - UUID of the farm
     * @returns Array of fields with GeoJSON
     */
    async getFarmFields(farmId: string): Promise<any[]> {
        const query = `
            SELECT
                id,
                name,
                crop_type,
                ST_AsGeoJSON(boundary)::jsonb as boundary_geojson,
                ST_AsGeoJSON(centroid)::jsonb as centroid_geojson,
                area_hectares,
                status,
                health_score,
                ndvi_value
            FROM fields
            WHERE farm_id = $1 AND is_deleted = FALSE
            ORDER BY name
        `;

        const result = await AppDataSource.query(query, [farmId]);
        return result;
    }

    /**
     * Create a field with GeoJSON boundary
     * @param fieldData - Field data including GeoJSON boundary
     * @returns Created field
     */
    async createFieldWithBoundary(fieldData: {
        name: string;
        tenant_id: string;
        crop_type: string;
        owner_id?: string;
        farm_id?: string;
        boundary_geojson: any; // GeoJSON object
    }): Promise<any> {
        const query = `
            INSERT INTO fields (
                name,
                tenant_id,
                crop_type,
                owner_id,
                farm_id,
                boundary
            ) VALUES (
                $1, $2, $3, $4, $5,
                ST_SetSRID(ST_GeomFromGeoJSON($6), 4326)
            )
            RETURNING id, name, area_hectares,
                ST_AsGeoJSON(boundary)::jsonb as boundary_geojson,
                ST_AsGeoJSON(centroid)::jsonb as centroid_geojson
        `;

        const result = await AppDataSource.query(query, [
            fieldData.name,
            fieldData.tenant_id,
            fieldData.crop_type,
            fieldData.owner_id || null,
            fieldData.farm_id || null,
            JSON.stringify(fieldData.boundary_geojson)
        ]);

        return result[0];
    }

    /**
     * Update field boundary
     * @param fieldId - UUID of the field
     * @param boundaryGeoJSON - New boundary as GeoJSON
     * @returns Updated field
     */
    async updateFieldBoundary(fieldId: string, boundaryGeoJSON: any): Promise<any> {
        const query = `
            UPDATE fields
            SET boundary = ST_SetSRID(ST_GeomFromGeoJSON($1), 4326)
            WHERE id = $2
            RETURNING id, name, area_hectares,
                ST_AsGeoJSON(boundary)::jsonb as boundary_geojson,
                ST_AsGeoJSON(centroid)::jsonb as centroid_geojson
        `;

        const result = await AppDataSource.query(query, [
            JSON.stringify(boundaryGeoJSON),
            fieldId
        ]);

        if (!result || result.length === 0) {
            throw new Error(`Field with ID ${fieldId} not found`);
        }

        return result[0];
    }

    /**
     * Create a farm with location
     * @param farmData - Farm data including location
     * @returns Created farm
     */
    async createFarmWithLocation(farmData: {
        name: string;
        tenant_id: string;
        owner_id: string;
        location_lat: number;
        location_lng: number;
        boundary_geojson?: any;
        address?: string;
        phone?: string;
        email?: string;
    }): Promise<any> {
        const query = `
            INSERT INTO farms (
                name,
                tenant_id,
                owner_id,
                location,
                boundary,
                address,
                phone,
                email
            ) VALUES (
                $1, $2, $3,
                ST_SetSRID(ST_MakePoint($4, $5), 4326),
                ${farmData.boundary_geojson ? 'ST_SetSRID(ST_GeomFromGeoJSON($6), 4326)' : 'NULL'},
                $7, $8, $9
            )
            RETURNING id, name,
                ST_AsGeoJSON(location)::jsonb as location_geojson,
                ${farmData.boundary_geojson ? 'ST_AsGeoJSON(boundary)::jsonb as boundary_geojson,' : ''}
                total_area_hectares
        `;

        const params: (string | number | null)[] = [
            farmData.name,
            farmData.tenant_id,
            farmData.owner_id,
            farmData.location_lng,
            farmData.location_lat,
        ];

        if (farmData.boundary_geojson) {
            params.push(JSON.stringify(farmData.boundary_geojson));
        }

        params.push(
            farmData.address ?? null,
            farmData.phone ?? null,
            farmData.email ?? null
        );

        const result = await AppDataSource.query(query, params as (string | number)[]);
        return result[0];
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Export singleton instance
// ─────────────────────────────────────────────────────────────────────────────

export const geoService = new GeoService();
