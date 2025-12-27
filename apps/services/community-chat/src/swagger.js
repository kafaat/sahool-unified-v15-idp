/**
 * Swagger/OpenAPI Configuration
 * إعدادات توثيق OpenAPI
 */

const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

/**
 * Load OpenAPI YAML specification
 * تحميل ملف OpenAPI YAML
 */
function loadOpenAPISpec() {
  try {
    const yamlPath = path.join(__dirname, '../openapi.yaml');
    const fileContents = fs.readFileSync(yamlPath, 'utf8');
    return yaml.load(fileContents);
  } catch (error) {
    console.error('❌ Error loading OpenAPI specification:', error.message);
    return null;
  }
}

/**
 * Swagger JSDoc Options
 * خيارات توثيق Swagger
 */
const swaggerOptions = {
  definition: {
    openapi: '3.0.3',
    info: {
      title: 'Sahool Community Chat Service API',
      version: '1.0.0',
      description: `
# خدمة الدردشة الحية لمجتمع سهول الزراعي
Sahool Real-time Chat Service - Communication between farmers and agricultural experts

## Features
- Real-time messaging using Socket.io
- Expert-Farmer consultation sessions
- Support request management
- Message history and persistence
- Typing indicators
- Online presence tracking

## Authentication
Authentication is performed via JWT tokens for Socket.io connections.
REST API endpoints are currently open for internal microservices communication.

## WebSocket Connection Example
\`\`\`javascript
const io = require('socket.io-client');
const socket = io('http://localhost:8097', {
  auth: { token: 'your-jwt-token' }
});

// Register user
socket.emit('register_user', {
  userId: '12345',
  userName: 'محمد أحمد',
  userType: 'farmer',
  governorate: 'القاهرة'
});

// Listen for confirmation
socket.on('registration_confirmed', (data) => {
  console.log('Registered:', data);
});
\`\`\`

## Environment Variables
- \`PORT\`: Service port (default: 8097)
- \`JWT_SECRET_KEY\`: Secret key for JWT verification
- \`CHAT_REQUIRE_AUTH\`: Enable/disable authentication (default: true)
- \`CORS_ORIGINS\`: Comma-separated list of allowed origins
      `,
      contact: {
        name: 'Sahool Platform',
        url: 'https://sahool.io',
      },
      license: {
        name: 'Proprietary',
      },
    },
    servers: [
      {
        url: 'http://localhost:8097',
        description: 'Local Development',
      },
      {
        url: 'https://chat.sahool.io',
        description: 'Production',
      },
    ],
    tags: [
      {
        name: 'Health',
        description: 'Service health and status endpoints',
      },
      {
        name: 'Rooms',
        description: 'Chat room management and history',
      },
      {
        name: 'Experts',
        description: 'Expert availability and management',
      },
      {
        name: 'Support Requests',
        description: 'Support ticket and request management',
      },
      {
        name: 'Statistics',
        description: 'Service metrics and analytics',
      },
      {
        name: 'WebSocket Events',
        description: 'Real-time Socket.io events documentation',
      },
    ],
  },
  apis: ['./src/index.js', './src/**/*.js'], // Path to API files with JSDoc annotations
};

/**
 * Generate Swagger specification
 * توليد مواصفات Swagger
 */
function generateSwaggerSpec() {
  // Try to load from YAML file first
  const yamlSpec = loadOpenAPISpec();
  if (yamlSpec) {
    console.log('✅ Loaded OpenAPI specification from openapi.yaml');
    return yamlSpec;
  }

  // Fallback to JSDoc generation
  console.log('⚠️ Generating OpenAPI specification from JSDoc comments');
  return swaggerJsdoc(swaggerOptions);
}

/**
 * Swagger UI Options
 * خيارات واجهة Swagger UI
 */
const swaggerUiOptions = {
  explorer: true,
  customCss: `
    .swagger-ui .topbar { display: none }
    .swagger-ui .info { margin: 20px 0 }
    .swagger-ui .info .title { font-size: 2em; color: #2e7d32 }
    .swagger-ui .scheme-container { background: #f5f5f5; padding: 15px }
  `,
  customSiteTitle: 'Sahool Chat API Documentation',
  customfavIcon: 'https://sahool.io/favicon.ico',
  swaggerOptions: {
    persistAuthorization: true,
    displayRequestDuration: true,
    filter: true,
    tryItOutEnabled: true,
    syntaxHighlight: {
      activate: true,
      theme: 'monokai',
    },
  },
};

/**
 * Setup Swagger documentation endpoint
 * إعداد نقطة نهاية توثيق Swagger
 *
 * @param {import('express').Application} app - Express application
 */
function setupSwagger(app) {
  const swaggerSpec = generateSwaggerSpec();

  if (!swaggerSpec) {
    console.error('❌ Failed to generate Swagger specification');
    return;
  }

  // Serve Swagger JSON
  app.get('/api-docs.json', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.json(swaggerSpec);
  });

  // Serve Swagger UI
  app.use(
    '/api-docs',
    swaggerUi.serve,
    swaggerUi.setup(swaggerSpec, swaggerUiOptions)
  );

  // Serve Redoc (alternative documentation UI)
  app.get('/redoc', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html dir="rtl" lang="ar">
  <head>
    <title>Sahool Chat API - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc spec-url='/api-docs.json'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
    `);
  });

  console.log('📚 Swagger documentation available at:');
  console.log('   • Swagger UI: http://localhost:8097/api-docs');
  console.log('   • OpenAPI JSON: http://localhost:8097/api-docs.json');
  console.log('   • ReDoc: http://localhost:8097/redoc');
}

/**
 * JSDoc annotations for existing endpoints
 * هذه التعليقات التوضيحية يمكن إضافتها مباشرة في index.js
 */

/**
 * @swagger
 * /healthz:
 *   get:
 *     summary: Health Check
 *     description: Check service health and get current status
 *     tags:
 *       - Health
 *     responses:
 *       200:
 *         description: Service is healthy
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: healthy
 *                 service:
 *                   type: string
 *                   example: community-chat
 *                 version:
 *                   type: string
 *                   example: 1.0.0
 *                 activeConnections:
 *                   type: integer
 *                   example: 42
 *                 onlineExperts:
 *                   type: integer
 *                   example: 5
 *                 activeRooms:
 *                   type: integer
 *                   example: 12
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 */

/**
 * @swagger
 * /v1/requests:
 *   get:
 *     summary: Get Support Requests
 *     description: Retrieve all active support requests, optionally filtered by status
 *     tags:
 *       - Support Requests
 *     parameters:
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *           enum: [pending, active, resolved, closed]
 *         description: Filter by request status
 *     responses:
 *       200:
 *         description: List of support requests
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 */

/**
 * @swagger
 * /v1/rooms/{roomId}/messages:
 *   get:
 *     summary: Get Room Messages
 *     description: Retrieve message history for a specific chat room
 *     tags:
 *       - Rooms
 *     parameters:
 *       - in: path
 *         name: roomId
 *         required: true
 *         schema:
 *           type: string
 *         description: Unique room identifier
 *     responses:
 *       200:
 *         description: List of messages in the room
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 */

/**
 * @swagger
 * /v1/experts/online:
 *   get:
 *     summary: Get Online Experts
 *     description: Get the count of currently online experts
 *     tags:
 *       - Experts
 *     responses:
 *       200:
 *         description: Online experts information
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 count:
 *                   type: integer
 *                   example: 5
 *                 available:
 *                   type: boolean
 *                   example: true
 */

/**
 * @swagger
 * /v1/stats:
 *   get:
 *     summary: Get Service Statistics
 *     description: Get comprehensive statistics about the chat service
 *     tags:
 *       - Statistics
 *     responses:
 *       200:
 *         description: Service statistics
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 totalConnections:
 *                   type: integer
 *                 onlineExperts:
 *                   type: integer
 *                 activeRooms:
 *                   type: integer
 *                 totalMessages:
 *                   type: integer
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 */

module.exports = {
  setupSwagger,
  swaggerOptions,
  swaggerUiOptions,
  generateSwaggerSpec,
};
