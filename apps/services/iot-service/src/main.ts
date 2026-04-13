/**
 * SAHOOL IoT Service - Main Entry Point
 * خدمة إنترنت الأشياء - نقطة البداية
 *
 * Features:
 * - MQTT broker connection
 * - Sensor data ingestion
 * - Actuator control (pumps, valves)
 * - Real-time data streaming
 */

import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { ValidationPipe, RequestMethod } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import helmet from "helmet";
import { initializeNatsClient, NatsClient } from "@sahool/shared-events";
import { AppModule } from "./app.module";
import { HttpExceptionFilter } from "./utils/http-exception.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

async function bootstrap() {
  // Initialize NATS BEFORE Nest app starts so the IoT service can publish
  // sensor alerts to notification-service via @sahool/shared-events. Without
  // this call, publishNotificationSend() throws "NATS connection is not
  // available" — the .catch() in iot.service.ts swallows it silently and
  // sensor alerts disappear in production. Failure is non-fatal: the
  // service still starts and serves HTTP / MQTT.
  try {
    await initializeNatsClient({
      servers: process.env.NATS_URL || "nats://nats:4222",
      name: "iot-service",
    });
    console.log("[NATS] Connected — sensor alerts will publish to event bus");
  } catch (err) {
    console.warn(
      `[NATS] Connection failed (degraded mode, sensor alerts will be dropped): ${
        err instanceof Error ? err.message : String(err)
      }`,
    );
  }

  const app = await NestFactory.create(AppModule);

  // Security headers
  app.use(helmet());

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  // Global request logging interceptor (BUG-006 fix)
  app.useGlobalInterceptors(new RequestLoggingInterceptor("iot-service", false, false));

  // CORS configuration - restrict to allowed origins
  const allowedOrigins = process.env.CORS_ORIGINS
    ? process.env.CORS_ORIGINS.split(",")
    : [
        "https://sahool.io",
        "https://app.sahool.io",
        "https://admin.sahool.io",
        "http://localhost:3000",
        "http://localhost:3001",
      ];

  app.enableCors({
    origin: allowedOrigins,
    methods: ["GET", "POST", "PUT", "DELETE"],
    credentials: true,
  });

  // Validation
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  // API prefix - exclude health endpoints for K8s probes
  app.setGlobalPrefix("api/v1", {
    exclude: [
      { path: "healthz", method: RequestMethod.GET },
      { path: "readyz", method: RequestMethod.GET },
      { path: "health", method: RequestMethod.GET },
    ],
  });

  // Swagger documentation (non-production only)
  if (process.env.NODE_ENV !== "production") {
    const config = new DocumentBuilder()
      .setTitle("SAHOOL IoT Service")
      .setDescription("Smart Irrigation & Sensor Management API")
      .setVersion("16.0.0")
      .addTag("sensors", "Sensor data endpoints")
      .addTag("actuators", "Pump & valve control")
      .addTag("devices", "Device management")
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup("docs", app, document);
  }

  const port = process.env.PORT || 8117;
  await app.listen(port);

  console.log(`
╔═══════════════════════════════════════════════════════════╗
║             SAHOOL IoT Service Started                   ║
╠═══════════════════════════════════════════════════════════╣
║  📡 Service: http://localhost:${port}                       ║
║  📚 Swagger: http://localhost:${port}/docs                  ║
║  🔌 MQTT: Connected to broker                            ║
╚═══════════════════════════════════════════════════════════╝
  `);

  // Graceful shutdown
  let isShuttingDown = false;
  async function gracefulShutdown(signal: string) {
    if (isShuttingDown) return;
    isShuttingDown = true;
    console.log(`\nReceived ${signal}, starting graceful shutdown...`);
    try {
      await app.close();
      // Drain pending NATS publishes before exiting so in-flight sensor
      // alerts aren't lost.
      try {
        const nats = NatsClient.getInstance();
        if (nats.isConnected()) {
          await nats.disconnect();
        }
      } catch (err) {
        console.warn(
          `[NATS] Drain failed: ${err instanceof Error ? err.message : String(err)}`,
        );
      }
      console.log('Service shutdown complete');
      process.exit(0);
    } catch (error) {
      console.error('Error during graceful shutdown:', error);
      process.exit(1);
    }
  }

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));
}

bootstrap();
