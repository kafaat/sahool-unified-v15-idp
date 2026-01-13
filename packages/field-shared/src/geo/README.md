# SAHOOL Geospatial Module (PostGIS)

This module provides comprehensive geospatial functionality for the Field Core service using PostGIS spatial database extensions.

## Features

- **Spatial Queries**: Find fields and farms within a radius, bounding box, or by distance
- **Area Calculations**: Calculate field areas in hectares from polygon boundaries
- **Point-in-Polygon**: Check if a coordinate is inside a field boundary
- **Distance Calculations**: Calculate distances between fields or from a point
- **GeoJSON Support**: Create and update fields/farms with GeoJSON geometries
- **Regional Analytics**: Get agricultural statistics for a region

## Database Setup

### 1. Apply Migrations

```bash
cd apps/services/field-core
npm run prisma:migrate:deploy
```

This will apply:

- Migration `0001_init_postgis`: Initial PostGIS setup and field tables
- Migration `0002_add_geospatial_indexes`: Farm table and advanced geospatial functions

### 2. Verify PostGIS

```sql
-- Check PostGIS extension
SELECT PostGIS_Version();

-- Verify GIST indexes
SELECT indexname, tablename
FROM pg_indexes
WHERE indexname LIKE 'idx_%_location' OR indexname LIKE 'idx_%_boundary';

-- List available geospatial functions
\df find_*
\df calculate_*
\df check_*
```

## API Endpoints

All endpoints are prefixed with `/api/v1/geo`

### Query Endpoints

#### Find Fields in Radius

```http
GET /api/v1/geo/fields/radius?lat=15.3694&lng=44.1910&radius=10&tenantId=tenant123
```

Returns all fields within the specified radius (in km) from a point.

**Response:**

```json
{
  "center": { "lat": 15.3694, "lng": 44.191 },
  "radius_km": 10,
  "total_fields": 5,
  "fields": [
    {
      "field_id": "uuid",
      "field_name": "Field 1",
      "distance_km": 2.5,
      "area_hectares": 5.25,
      "crop_type": "wheat",
      "centroid_lat": 15.37,
      "centroid_lng": 44.192
    }
  ]
}
```

#### Find Nearby Farms

```http
GET /api/v1/geo/farms/nearby?lat=15.3694&lng=44.1910&limit=5
```

Returns the nearest farms to a location.

#### Calculate Field Area

```http
GET /api/v1/geo/fields/{fieldId}/area
```

Calculates the area of a field in hectares from its boundary geometry.

#### Check Point in Field

```http
POST /api/v1/geo/fields/{fieldId}/contains-point
Content-Type: application/json

{
  "lat": 15.3694,
  "lng": 44.1910
}
```

Checks if a coordinate is inside a field's boundary.

#### Find Fields in Bounding Box

```http
GET /api/v1/geo/fields/bbox?minLat=15.0&minLng=44.0&maxLat=16.0&maxLng=45.0
```

Returns all fields that intersect with the bounding box.

#### Calculate Distance Between Fields

```http
GET /api/v1/geo/fields/{fieldId1}/distance/{fieldId2}
```

Calculates the distance in kilometers between two fields.

#### Get Regional Statistics

```http
GET /api/v1/geo/region/stats?minLat=15.0&minLng=44.0&maxLat=16.0&maxLng=45.0&tenantId=tenant123
```

Returns agricultural statistics for a region:

- Total fields
- Total area (ha)
- Average field size
- Crop distribution

#### Get GeoJSON Representations

```http
GET /api/v1/geo/fields/{fieldId}/geojson
GET /api/v1/geo/farms/{farmId}/geojson
GET /api/v1/geo/farms/{farmId}/fields
```

### Mutation Endpoints

#### Create Field with Boundary

```http
POST /api/v1/geo/fields
Content-Type: application/json

{
  "name": "New Field",
  "tenant_id": "tenant123",
  "crop_type": "wheat",
  "farm_id": "farm-uuid",
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [
      [
        [44.1910, 15.3694],
        [44.1920, 15.3694],
        [44.1920, 15.3704],
        [44.1910, 15.3704],
        [44.1910, 15.3694]
      ]
    ]
  }
}
```

Creates a field with a GeoJSON polygon boundary. The area and centroid are automatically calculated.

#### Update Field Boundary

```http
PUT /api/v1/geo/fields/{fieldId}/boundary
Content-Type: application/json

{
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [...]
  }
}
```

#### Create Farm with Location

```http
POST /api/v1/geo/farms
Content-Type: application/json

{
  "name": "My Farm",
  "tenant_id": "tenant123",
  "owner_id": "owner123",
  "location_lat": 15.3694,
  "location_lng": 44.1910,
  "address": "Sana'a, Yemen",
  "phone": "+967 123456789",
  "email": "farm@example.com",
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [...]
  }
}
```

## Using the GeoService Programmatically

```typescript
import { geoService } from "@sahool/field-shared";

// Find fields in radius
const fields = await geoService.findFieldsInRadius(15.3694, 44.1910, 10, "tenant123");

// Find nearby farms
const farms = await geoService.findNearbyFarms(15.3694, 44.1910, 5);

// Calculate field area
const area = await geoService.calculateFieldArea("field-uuid");

// Check if point is in field
const result = await geoService.checkPointInField(15.3694, 44.1910, "field-uuid");

// Get field GeoJSON
const geojson = await geoService.getFieldGeoJSON("field-uuid");

// Create field with boundary
const newField = await geoService.createFieldWithBoundary({
  name: "New Field",
  tenant_id: "tenant123",
  crop_type: "wheat",
  boundary_geojson: { type: "Polygon", coordinates: [...] }
});
```

## PostGIS Functions

The following PostgreSQL functions are available:

- `find_fields_in_radius(lat, lng, radius_km, tenant_id)`: Find fields within radius
- `find_nearby_farms(lat, lng, limit, tenant_id)`: Find nearest farms
- `get_field_area(field_id)`: Calculate field area
- `check_point_in_field(lat, lng, field_id)`: Point-in-polygon check
- `find_fields_in_bbox(min_lat, min_lng, max_lat, max_lng, tenant_id)`: Find fields in bounding box
- `calculate_fields_distance(field_id_1, field_id_2)`: Distance between fields
- `get_region_field_stats(min_lat, min_lng, max_lat, max_lng, tenant_id)`: Regional statistics

## Database Views

- `farms_geojson`: Farms with GeoJSON representation
- `fields_with_farm`: Fields joined with their farm information
- `fields_geojson`: Fields with GeoJSON boundaries (from initial migration)

## GIST Indexes

The following spatial indexes are created for optimal query performance:

- `idx_fields_boundary`: GIST index on field boundaries
- `idx_fields_centroid`: GIST index on field centroids
- `idx_farms_location`: GIST index on farm locations
- `idx_farms_boundary`: GIST index on farm boundaries

## Coordinate System

All geometries use **SRID 4326** (WGS 84, standard GPS coordinates):

- Longitude: -180 to 180
- Latitude: -90 to 90
- Format: [longitude, latitude] (note: GeoJSON uses lng/lat order)

## Performance Considerations

1. **Always use GIST indexes**: The spatial queries use GIST indexes for fast lookups
2. **Limit result sets**: Use limit parameters for large datasets
3. **Tenant filtering**: Always filter by tenant_id when possible
4. **Geography vs Geometry**: We use `geography` type for accurate distance calculations
5. **Bounding box queries**: More efficient than radius queries for large regions

## Testing

```bash
# Run geospatial query tests
curl "http://localhost:3000/api/v1/geo/fields/radius?lat=15.3694&lng=44.1910&radius=10"

# Check field area
curl "http://localhost:3000/api/v1/geo/fields/{uuid}/area"

# Create field with boundary
curl -X POST http://localhost:3000/api/v1/geo/fields \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Field","tenant_id":"test","crop_type":"wheat","boundary_geojson":{"type":"Polygon","coordinates":[[[44.19,15.37],[44.20,15.37],[44.20,15.38],[44.19,15.38],[44.19,15.37]]]}}'
```

## References

- [PostGIS Documentation](https://postgis.net/docs/)
- [GeoJSON Specification](https://geojson.org/)
- [Prisma PostGIS Guide](https://www.prisma.io/docs/concepts/database-connectors/postgresql#postgis)
