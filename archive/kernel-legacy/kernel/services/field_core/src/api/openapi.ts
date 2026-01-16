/**
 * SAHOOL Field Core API - OpenAPI Documentation
 * Provides Swagger/OpenAPI 3.0 specification
 */

import { Router, Request, Response } from "express";

// OpenAPI 3.0 Specification
export const openApiSpec = {
  openapi: "3.0.3",
  info: {
    title: "SAHOOL Field Core API",
    description: `
# SAHOOL Field Management API

واجهة برمجة تطبيقات إدارة الحقول الزراعية

This API provides comprehensive field management capabilities for the SAHOOL agricultural platform.

## Features
- Field CRUD operations
- NDVI data management
- Multi-tenant support
- Arabic/English bilingual responses

## Authentication
All endpoints require JWT authentication via the \`Authorization: Bearer <token>\` header.

## Rate Limiting
- Free tier: 30 requests/minute
- Standard: 60 requests/minute
- Premium: 120 requests/minute
        `,
    version: "15.3.0",
    contact: {
      name: "SAHOOL Support",
      email: "support@sahool.sa",
    },
    license: {
      name: "Proprietary",
      url: "https://sahool.sa/terms",
    },
  },
  servers: [
    {
      url: "https://api.sahool.sa/v1",
      description: "Production server",
    },
    {
      url: "https://staging-api.sahool.sa/v1",
      description: "Staging server",
    },
    {
      url: "http://localhost:3001",
      description: "Development server",
    },
  ],
  tags: [
    {
      name: "Fields",
      description: "Field management operations - إدارة الحقول",
    },
    {
      name: "NDVI",
      description: "Vegetation index data - بيانات مؤشر الغطاء النباتي",
    },
    {
      name: "Health",
      description: "Service health endpoints",
    },
  ],
  paths: {
    "/fields": {
      get: {
        tags: ["Fields"],
        summary: "List all fields",
        description:
          "Get paginated list of fields for the tenant - قائمة الحقول",
        operationId: "listFields",
        parameters: [
          { $ref: "#/components/parameters/TenantId" },
          { $ref: "#/components/parameters/Limit" },
          { $ref: "#/components/parameters/Offset" },
          {
            name: "status",
            in: "query",
            description: "Filter by field status",
            schema: {
              type: "string",
              enum: ["active", "fallow", "preparing", "harvested"],
            },
          },
          {
            name: "cropType",
            in: "query",
            description: "Filter by crop type",
            schema: { type: "string" },
          },
        ],
        responses: {
          "200": {
            description: "Successful response",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/FieldListResponse",
                },
              },
            },
          },
          "401": { $ref: "#/components/responses/Unauthorized" },
          "429": { $ref: "#/components/responses/RateLimitExceeded" },
        },
        security: [{ bearerAuth: [] }],
      },
      post: {
        tags: ["Fields"],
        summary: "Create a new field",
        description: "Create a new agricultural field - إنشاء حقل جديد",
        operationId: "createField",
        parameters: [{ $ref: "#/components/parameters/TenantId" }],
        requestBody: {
          required: true,
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/FieldCreate" },
              examples: {
                wheat: {
                  summary: "Wheat field",
                  value: {
                    name: "حقل القمح الشمالي",
                    cropType: "wheat",
                    coordinates: [
                      [46.7, 24.6],
                      [46.8, 24.6],
                      [46.8, 24.7],
                      [46.7, 24.7],
                    ],
                    irrigationType: "drip",
                    soilType: "sandy_loam",
                  },
                },
              },
            },
          },
        },
        responses: {
          "201": {
            description: "Field created successfully",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/FieldResponse" },
              },
            },
          },
          "400": { $ref: "#/components/responses/ValidationError" },
          "401": { $ref: "#/components/responses/Unauthorized" },
          "429": { $ref: "#/components/responses/RateLimitExceeded" },
        },
        security: [{ bearerAuth: [] }],
      },
    },
    "/fields/{fieldId}": {
      get: {
        tags: ["Fields"],
        summary: "Get field by ID",
        description: "Get detailed field information - تفاصيل الحقل",
        operationId: "getField",
        parameters: [
          { $ref: "#/components/parameters/FieldId" },
          { $ref: "#/components/parameters/TenantId" },
        ],
        responses: {
          "200": {
            description: "Successful response",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/FieldResponse" },
              },
            },
          },
          "404": { $ref: "#/components/responses/NotFound" },
          "401": { $ref: "#/components/responses/Unauthorized" },
        },
        security: [{ bearerAuth: [] }],
      },
      patch: {
        tags: ["Fields"],
        summary: "Update field",
        description: "Update field properties - تحديث الحقل",
        operationId: "updateField",
        parameters: [
          { $ref: "#/components/parameters/FieldId" },
          { $ref: "#/components/parameters/TenantId" },
          { $ref: "#/components/parameters/IfMatch" },
        ],
        requestBody: {
          required: true,
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/FieldUpdate" },
            },
          },
        },
        responses: {
          "200": {
            description: "Field updated successfully",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/FieldResponse" },
              },
            },
          },
          "400": { $ref: "#/components/responses/ValidationError" },
          "404": { $ref: "#/components/responses/NotFound" },
          "409": { $ref: "#/components/responses/Conflict" },
          "412": { $ref: "#/components/responses/PreconditionFailed" },
        },
        security: [{ bearerAuth: [] }],
      },
      delete: {
        tags: ["Fields"],
        summary: "Delete field",
        description: "Soft delete a field - حذف الحقل",
        operationId: "deleteField",
        parameters: [
          { $ref: "#/components/parameters/FieldId" },
          { $ref: "#/components/parameters/TenantId" },
        ],
        responses: {
          "204": { description: "Field deleted successfully" },
          "404": { $ref: "#/components/responses/NotFound" },
          "401": { $ref: "#/components/responses/Unauthorized" },
        },
        security: [{ bearerAuth: [] }],
      },
    },
    "/fields/{fieldId}/ndvi": {
      get: {
        tags: ["NDVI"],
        summary: "Get NDVI history",
        description: "Get vegetation index history for a field - سجل مؤشر NDVI",
        operationId: "getFieldNdvi",
        parameters: [
          { $ref: "#/components/parameters/FieldId" },
          { $ref: "#/components/parameters/TenantId" },
          {
            name: "startDate",
            in: "query",
            schema: { type: "string", format: "date" },
          },
          {
            name: "endDate",
            in: "query",
            schema: { type: "string", format: "date" },
          },
        ],
        responses: {
          "200": {
            description: "NDVI data retrieved",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/NdviListResponse" },
              },
            },
          },
          "404": { $ref: "#/components/responses/NotFound" },
        },
        security: [{ bearerAuth: [] }],
      },
      post: {
        tags: ["NDVI"],
        summary: "Add NDVI reading",
        description: "Add new NDVI measurement - إضافة قراءة NDVI",
        operationId: "addFieldNdvi",
        parameters: [
          { $ref: "#/components/parameters/FieldId" },
          { $ref: "#/components/parameters/TenantId" },
        ],
        requestBody: {
          required: true,
          content: {
            "application/json": {
              schema: { $ref: "#/components/schemas/NdviCreate" },
            },
          },
        },
        responses: {
          "201": {
            description: "NDVI reading added",
            content: {
              "application/json": {
                schema: { $ref: "#/components/schemas/NdviResponse" },
              },
            },
          },
          "400": { $ref: "#/components/responses/ValidationError" },
          "404": { $ref: "#/components/responses/NotFound" },
        },
        security: [{ bearerAuth: [] }],
      },
    },
    "/healthz": {
      get: {
        tags: ["Health"],
        summary: "Liveness probe",
        operationId: "healthCheck",
        responses: {
          "200": {
            description: "Service is alive",
            content: {
              "application/json": {
                schema: {
                  type: "object",
                  properties: {
                    status: { type: "string", example: "ok" },
                    timestamp: { type: "string", format: "date-time" },
                  },
                },
              },
            },
          },
        },
        security: [],
      },
    },
    "/readyz": {
      get: {
        tags: ["Health"],
        summary: "Readiness probe",
        operationId: "readinessCheck",
        responses: {
          "200": {
            description: "Service is ready",
            content: {
              "application/json": {
                schema: {
                  type: "object",
                  properties: {
                    status: { type: "string", example: "ready" },
                    checks: {
                      type: "object",
                      properties: {
                        database: { type: "string" },
                        cache: { type: "string" },
                      },
                    },
                  },
                },
              },
            },
          },
          "503": { description: "Service not ready" },
        },
        security: [],
      },
    },
  },
  components: {
    schemas: {
      Field: {
        type: "object",
        properties: {
          id: { type: "string", format: "uuid" },
          tenantId: { type: "string", format: "uuid" },
          name: { type: "string", maxLength: 100 },
          cropType: { type: "string" },
          status: {
            type: "string",
            enum: ["active", "fallow", "preparing", "harvested"],
          },
          coordinates: {
            type: "array",
            items: {
              type: "array",
              items: { type: "number" },
              minItems: 2,
              maxItems: 2,
            },
          },
          area: { type: "number", description: "Area in hectares" },
          irrigationType: {
            type: "string",
            enum: ["drip", "sprinkler", "flood", "none"],
          },
          soilType: { type: "string" },
          currentNdvi: { type: "number", minimum: -1, maximum: 1 },
          plantingDate: { type: "string", format: "date" },
          expectedHarvest: { type: "string", format: "date" },
          createdAt: { type: "string", format: "date-time" },
          updatedAt: { type: "string", format: "date-time" },
          version: { type: "integer" },
        },
      },
      FieldCreate: {
        type: "object",
        required: ["name", "cropType"],
        properties: {
          name: { type: "string", minLength: 1, maxLength: 100 },
          cropType: { type: "string", minLength: 1, maxLength: 50 },
          coordinates: {
            type: "array",
            items: {
              type: "array",
              items: { type: "number" },
            },
            minItems: 3,
          },
          ownerId: { type: "string", format: "uuid" },
          irrigationType: {
            type: "string",
            enum: ["drip", "sprinkler", "flood", "none"],
          },
          soilType: { type: "string", maxLength: 50 },
          plantingDate: { type: "string", format: "date" },
          expectedHarvest: { type: "string", format: "date" },
          metadata: { type: "object" },
        },
      },
      FieldUpdate: {
        type: "object",
        properties: {
          name: { type: "string", minLength: 1, maxLength: 100 },
          cropType: { type: "string", minLength: 1, maxLength: 50 },
          status: {
            type: "string",
            enum: ["active", "fallow", "preparing", "harvested"],
          },
          irrigationType: {
            type: "string",
            enum: ["drip", "sprinkler", "flood", "none"],
          },
          soilType: { type: "string", maxLength: 50 },
          plantingDate: { type: "string", format: "date" },
          expectedHarvest: { type: "string", format: "date" },
          metadata: { type: "object" },
        },
      },
      FieldResponse: {
        type: "object",
        properties: {
          success: { type: "boolean" },
          data: { $ref: "#/components/schemas/Field" },
          message: { type: "string" },
          message_ar: { type: "string" },
        },
      },
      FieldListResponse: {
        type: "object",
        properties: {
          success: { type: "boolean" },
          data: {
            type: "array",
            items: { $ref: "#/components/schemas/Field" },
          },
          pagination: { $ref: "#/components/schemas/Pagination" },
        },
      },
      NdviReading: {
        type: "object",
        properties: {
          id: { type: "string", format: "uuid" },
          fieldId: { type: "string", format: "uuid" },
          value: { type: "number", minimum: -1, maximum: 1 },
          source: { type: "string" },
          recordedAt: { type: "string", format: "date-time" },
        },
      },
      NdviCreate: {
        type: "object",
        required: ["value"],
        properties: {
          value: { type: "number", minimum: -1, maximum: 1 },
          source: { type: "string", maxLength: 50 },
        },
      },
      NdviResponse: {
        type: "object",
        properties: {
          success: { type: "boolean" },
          data: { $ref: "#/components/schemas/NdviReading" },
        },
      },
      NdviListResponse: {
        type: "object",
        properties: {
          success: { type: "boolean" },
          data: {
            type: "array",
            items: { $ref: "#/components/schemas/NdviReading" },
          },
        },
      },
      Pagination: {
        type: "object",
        properties: {
          total: { type: "integer" },
          limit: { type: "integer" },
          offset: { type: "integer" },
          hasMore: { type: "boolean" },
        },
      },
      Error: {
        type: "object",
        properties: {
          success: { type: "boolean", example: false },
          error: { type: "string" },
          error_ar: { type: "string" },
          details: {
            type: "array",
            items: {
              type: "object",
              properties: {
                field: { type: "string" },
                message: { type: "string" },
                code: { type: "string" },
              },
            },
          },
        },
      },
    },
    parameters: {
      TenantId: {
        name: "X-Tenant-ID",
        in: "header",
        required: true,
        description: "Tenant identifier",
        schema: { type: "string", format: "uuid" },
      },
      FieldId: {
        name: "fieldId",
        in: "path",
        required: true,
        description: "Field identifier",
        schema: { type: "string", format: "uuid" },
      },
      Limit: {
        name: "limit",
        in: "query",
        description: "Number of items to return",
        schema: { type: "integer", minimum: 1, maximum: 100, default: 20 },
      },
      Offset: {
        name: "offset",
        in: "query",
        description: "Number of items to skip",
        schema: { type: "integer", minimum: 0, default: 0 },
      },
      IfMatch: {
        name: "If-Match",
        in: "header",
        description: "ETag for optimistic concurrency",
        schema: { type: "string" },
      },
    },
    responses: {
      Unauthorized: {
        description: "Authentication required",
        content: {
          "application/json": {
            schema: { $ref: "#/components/schemas/Error" },
            example: {
              success: false,
              error: "Unauthorized",
              error_ar: "غير مصرح",
            },
          },
        },
      },
      NotFound: {
        description: "Resource not found",
        content: {
          "application/json": {
            schema: { $ref: "#/components/schemas/Error" },
            example: {
              success: false,
              error: "Field not found",
              error_ar: "الحقل غير موجود",
            },
          },
        },
      },
      ValidationError: {
        description: "Validation error",
        content: {
          "application/json": {
            schema: { $ref: "#/components/schemas/Error" },
            example: {
              success: false,
              error: "Validation failed",
              error_ar: "فشل التحقق من البيانات",
              details: [
                {
                  field: "name",
                  message: "Required field is missing",
                  code: "required",
                },
              ],
            },
          },
        },
      },
      Conflict: {
        description: "Conflict - resource already exists or version mismatch",
        content: {
          "application/json": {
            schema: { $ref: "#/components/schemas/Error" },
            example: {
              success: false,
              error: "Conflict detected",
              error_ar: "تم اكتشاف تعارض",
            },
          },
        },
      },
      PreconditionFailed: {
        description: "ETag mismatch - resource was modified",
        content: {
          "application/json": {
            schema: { $ref: "#/components/schemas/Error" },
            example: {
              success: false,
              error: "Resource was modified",
              error_ar: "تم تعديل المورد",
            },
          },
        },
      },
      RateLimitExceeded: {
        description: "Rate limit exceeded",
        headers: {
          "X-RateLimit-Limit": {
            schema: { type: "integer" },
            description: "Request limit per minute",
          },
          "X-RateLimit-Remaining": {
            schema: { type: "integer" },
            description: "Remaining requests",
          },
          "X-RateLimit-Reset": {
            schema: { type: "integer" },
            description: "Unix timestamp when limit resets",
          },
          "Retry-After": {
            schema: { type: "integer" },
            description: "Seconds to wait before retry",
          },
        },
        content: {
          "application/json": {
            schema: { $ref: "#/components/schemas/Error" },
            example: {
              success: false,
              error: "Rate limit exceeded",
              error_ar: "تم تجاوز حد الطلبات",
            },
          },
        },
      },
    },
    securitySchemes: {
      bearerAuth: {
        type: "http",
        scheme: "bearer",
        bearerFormat: "JWT",
        description: "JWT token obtained from authentication service",
      },
    },
  },
};

// Create router for OpenAPI endpoints
export function createOpenApiRouter(): Router {
  const router = Router();

  // Serve OpenAPI JSON spec
  router.get("/openapi.json", (_req: Request, res: Response) => {
    res.json(openApiSpec);
  });

  // Serve Swagger UI HTML
  router.get("/docs", (_req: Request, res: Response) => {
    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAHOOL Field Core API - Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
        body { margin: 0; padding: 0; }
        .swagger-ui .topbar { display: none; }
        .swagger-ui .info .title { color: #2E7D32; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        window.onload = () => {
            SwaggerUIBundle({
                url: '/api/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                persistAuthorization: true,
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 2
            });
        };
    </script>
</body>
</html>
        `);
  });

  // ReDoc alternative
  router.get("/redoc", (_req: Request, res: Response) => {
    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAHOOL Field Core API - ReDoc</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
    </style>
</head>
<body>
    <redoc spec-url='/api/openapi.json'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
</body>
</html>
        `);
  });

  return router;
}

export default openApiSpec;
