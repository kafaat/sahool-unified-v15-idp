/**
 * SAHOOL Partner OAuth 2.0 / OIDC Authorization Server v16.0.0
 * خادم مصادقة الشركاء — OAuth 2.0 / OIDC
 *
 * Features (implemented in this scaffold):
 *   • Authorization Code grant (POST /partner/v1/oauth/token)
 *   • Refresh Token grant with rotation + reuse detection
 *   • OIDC Discovery (GET /.well-known/openid-configuration)
 *   • JWKS (GET /.well-known/jwks.json)
 *   • id_token (RS256) issuance
 *   • Health/readiness endpoints
 *
 * Planned (next branch):
 *   • Full consent screen at /authorize
 *   • Token revocation (RFC 7009)
 *   • Token introspection (RFC 7662)
 *   • UserInfo endpoint
 *   • Admin UI for partner registration
 *   • Kong route registration
 *
 * Maps 1:1 to FieldView's /api/oauth/token semantics so partners
 * already integrated with Climate FieldView can port with minimal work.
 */

import "reflect-metadata";

import { NestFactory } from "@nestjs/core";
import { ValidationPipe, Logger } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import helmet from "helmet";
import { AppModule } from "./app.module";
import { PartnerErrorFilter } from "./utils/partner-error.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

const PORT = Number(process.env.PORT ?? 3030);
const SERVICE_NAME = "partner-auth-service";
const SERVICE_VERSION = "16.0.0";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const logger = new Logger("Bootstrap");

  // Security headers — OAuth servers MUST set X-Frame-Options to prevent
  // consent-screen clickjacking (OWASP ASVS 4.0, V14.4).
  app.use(
    helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'"],
          frameAncestors: ["'none'"],
        },
      },
    }),
  );

  // FieldView-style error envelope: {error: {code, id, message}}
  app.useGlobalFilters(new PartnerErrorFilter());

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidNonWhitelisted: false,
    }),
  );

  app.useGlobalInterceptors(new RequestLoggingInterceptor(SERVICE_NAME));

  // CORS — OAuth endpoints must NOT be called from browsers cross-origin
  // (except discovery/JWKS which are public). Tight origin policy.
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(",") ?? [
    "https://sahool.com",
    "https://app.sahool.com",
    "https://dev.sahool.app",
    "https://sandbox.sahool.app",
  ];
  app.enableCors({
    origin: allowedOrigins,
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: [
      "Content-Type",
      "Authorization",
      "X-Request-Id",
      "X-Sahool-Partner-Key",
    ],
    credentials: false, // Bearer-token auth, no cookies
  });

  // Controllers declare their own absolute paths. No global prefix — this
  // service serves THREE path families that Kong routes to us:
  //   • /partner/v1/*           — OAuth + OIDC partner-facing endpoints
  //   • /api/v1/admin/partner-auth/*  — SAHOOL admin UI endpoints
  //   • /.well-known/*          — OIDC discovery + JWKS (unversioned by spec)
  //   • /healthz, /readyz, /health, /metrics — K8s + Prometheus

  if (process.env.NODE_ENV !== "production") {
    const cfg = new DocumentBuilder()
      .setTitle("SAHOOL Partner Auth Service")
      .setDescription(
        "OAuth 2.0 / OIDC authorization server for SAHOOL partner integrations. FieldView-compatible.",
      )
      .setVersion(SERVICE_VERSION)
      .addOAuth2({
        type: "oauth2",
        flows: {
          authorizationCode: {
            authorizationUrl: "/partner/v1/oauth/authorize",
            tokenUrl: "/partner/v1/oauth/token",
            scopes: {},
          },
        },
      })
      .build();
    const doc = SwaggerModule.createDocument(app, cfg);
    SwaggerModule.setup("partner/v1/docs", app, doc);
  }

  await app.listen(PORT);
  logger.log(`${SERVICE_NAME} v${SERVICE_VERSION} listening on :${PORT}`);
  logger.log(
    `OIDC discovery: http://localhost:${PORT}/.well-known/openid-configuration`,
  );

  // Graceful shutdown (same pattern as user-service)
  let shuttingDown = false;
  async function shutdown(signal: string) {
    if (shuttingDown) return;
    shuttingDown = true;
    logger.log(`${signal} received, shutting down…`);
    try {
      await app.close();
      process.exit(0);
    } catch (err) {
      logger.error(`Shutdown error: ${err instanceof Error ? err.message : err}`);
      process.exit(1);
    }
  }
  process.on("SIGTERM", () => shutdown("SIGTERM"));
  process.on("SIGINT", () => shutdown("SIGINT"));
}

bootstrap();
