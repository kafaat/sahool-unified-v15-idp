/**
 * SAHOOL Shared Pino Logger Configuration for NestJS Services
 * ===========================================================
 *
 * Provides standardized JSON structured logging for all SAHOOL NestJS services.
 *
 * Features:
 * - JSON structured logging with Pino (high performance)
 * - Correlation ID tracking (traceId)
 * - Automatic service name, timestamp, level
 * - Request/response logging
 * - Pretty printing in development, JSON in production
 *
 * Usage:
 *
 * In main.ts:
 * ```typescript
 * import { createPinoLoggerConfig } from '../shared/logging/pino-logger.config';
 * import { Logger } from 'nestjs-pino';
 *
 * const app = await NestFactory.create(AppModule, {
 *   logger: false, // Disable default logger
 * });
 * app.useLogger(app.get(Logger));
 * ```
 *
 * In app.module.ts:
 * ```typescript
 * import { LoggerModule } from 'nestjs-pino';
 * import { createPinoLoggerConfig } from '../shared/logging/pino-logger.config';
 *
 * @Module({
 *   imports: [
 *     LoggerModule.forRoot(createPinoLoggerConfig('my-service')),
 *   ],
 * })
 * export class AppModule {}
 * ```
 */

import { Params } from 'nestjs-pino';
import { randomUUID } from 'crypto';

/**
 * Create Pino logger configuration for a service
 *
 * @param serviceName - Name of the service (e.g., 'chat-service', 'user-service')
 * @returns Pino logger configuration for NestJS
 */
export function createPinoLoggerConfig(serviceName: string): Params {
  const isDevelopment =
    process.env.NODE_ENV !== 'production' && process.env.ENVIRONMENT !== 'production';
  const logLevel = process.env.LOG_LEVEL || 'info';

  return {
    pinoHttp: {
      // Use pretty printing in development, JSON in production
      transport: isDevelopment
        ? {
            target: 'pino-pretty',
            options: {
              colorize: true,
              translateTime: 'SYS:standard',
              ignore: 'pid,hostname',
              singleLine: false,
              messageFormat: '{service} [{levelLabel}] {msg}',
            },
          }
        : undefined,

      // Log level
      level: logLevel,

      // Custom serializers
      serializers: {
        req: (req: any) => ({
          id: req.id,
          method: req.method,
          url: req.url,
          query: req.query,
          params: req.params,
          remoteAddress: req.remoteAddress,
          remotePort: req.remotePort,
          headers: {
            host: req.headers.host,
            'user-agent': req.headers['user-agent'],
            'content-type': req.headers['content-type'],
            'x-correlation-id': req.headers['x-correlation-id'],
            'x-request-id': req.headers['x-request-id'],
            'x-tenant-id': req.headers['x-tenant-id'],
            'x-user-id': req.headers['x-user-id'],
          },
        }),
        res: (res: any) => ({
          statusCode: res.statusCode,
          headers: {
            'content-type': res.headers?.['content-type'],
            'x-correlation-id': res.headers?.['x-correlation-id'],
          },
        }),
        err: (err: any) => ({
          type: err.type || err.constructor.name,
          message: err.message,
          stack: err.stack,
          code: err.code,
          statusCode: err.statusCode,
        }),
      },

      // Custom request ID generation and correlation tracking
      genReqId: (req: any, res: any) => {
        // Use existing correlation ID from headers, or generate new one
        const correlationId =
          req.headers['x-correlation-id'] ||
          req.headers['x-request-id'] ||
          randomUUID();

        // Set correlation ID in response header
        res.setHeader('X-Correlation-ID', correlationId);
        res.setHeader('X-Request-ID', correlationId);

        return correlationId;
      },

      // Base logger configuration
      base: {
        service: serviceName,
        environment: process.env.ENVIRONMENT || process.env.NODE_ENV || 'development',
      },

      // Custom log message formatter
      customSuccessMessage: (req: any, res: any) => {
        return `${req.method} ${req.url} ${res.statusCode}`;
      },

      customErrorMessage: (req: any, res: any, err: any) => {
        return `${req.method} ${req.url} ${res.statusCode} - ${err.message}`;
      },

      // Auto-logging configuration
      autoLogging: {
        ignore: (req: any) => {
          // Don't log health check endpoints
          const healthPaths = [
            '/health',
            '/healthz',
            '/health/live',
            '/health/ready',
            '/readyz',
            '/livez',
            '/metrics',
          ];
          return healthPaths.some((path) => req.url?.startsWith(path));
        },
      },

      // Custom attributes for each log
      customAttributeKeys: {
        req: 'request',
        res: 'response',
        err: 'error',
        responseTime: 'duration_ms',
      },

      // Custom props added to each log
      customProps: (req: any, res: any) => {
        return {
          correlationId: req.id,
          traceId: req.id, // Alias for OpenTelemetry compatibility
          tenantId: req.headers['x-tenant-id'],
          userId: req.headers['x-user-id'],
        };
      },

      // Redact sensitive information
      redact: {
        paths: [
          'request.headers.authorization',
          'request.headers.cookie',
          'request.headers["x-api-key"]',
          'request.headers["x-auth-token"]',
          'request.body.password',
          'request.body.token',
          'request.body.secret',
          'response.headers["set-cookie"]',
        ],
        remove: true,
      },
    },
  };
}

/**
 * Create a Pino logger instance for use outside of HTTP context
 *
 * @param serviceName - Name of the service
 * @returns Pino logger instance
 */
export function createPinoLogger(serviceName: string) {
  const pino = require('pino');
  const isDevelopment =
    process.env.NODE_ENV !== 'production' && process.env.ENVIRONMENT !== 'production';
  const logLevel = process.env.LOG_LEVEL || 'info';

  return pino({
    level: logLevel,
    base: {
      service: serviceName,
      environment: process.env.ENVIRONMENT || process.env.NODE_ENV || 'development',
    },
    transport: isDevelopment
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname',
          },
        }
      : undefined,
    formatters: {
      level: (label: string) => {
        return { level: label };
      },
    },
    timestamp: () => `,"timestamp":"${new Date().toISOString()}"`,
  });
}

/**
 * Middleware to extract and propagate correlation IDs
 * Use this if not using nestjs-pino's built-in middleware
 */
export function correlationIdMiddleware(req: any, res: any, next: any) {
  const correlationId =
    req.headers['x-correlation-id'] ||
    req.headers['x-request-id'] ||
    randomUUID();

  req.correlationId = correlationId;
  req.id = correlationId;

  res.setHeader('X-Correlation-ID', correlationId);
  res.setHeader('X-Request-ID', correlationId);

  next();
}
