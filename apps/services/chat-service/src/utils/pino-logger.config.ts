/**
 * Pino Logger Configuration for Chat Service
 * إعدادات مسجل Pino لخدمة المحادثات
 */

import { randomUUID } from 'crypto';

interface PinoHttpOptions {
  transport?: any;
  level?: string;
  serializers?: Record<string, (data: any) => any>;
  genReqId?: (req: any, res: any) => string;
  base?: Record<string, any>;
  customSuccessMessage?: (req: any, res: any) => string;
  customErrorMessage?: (req: any, res: any, err: any) => string;
  autoLogging?: { ignore?: (req: any) => boolean };
  customAttributeKeys?: Record<string, string>;
  customProps?: (req: any, res: any) => Record<string, any>;
  redact?: { paths: string[]; remove?: boolean };
}

interface Params {
  pinoHttp?: PinoHttpOptions;
}

/**
 * Create Pino logger configuration for a service
 */
export function createPinoLoggerConfig(serviceName: string): Params {
  const isDevelopment =
    process.env.NODE_ENV !== 'production' && process.env.ENVIRONMENT !== 'production';
  const logLevel = process.env.LOG_LEVEL || 'info';

  return {
    pinoHttp: {
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

      level: logLevel,

      serializers: {
        req: (req: any) => ({
          id: req.id,
          method: req.method,
          url: req.url,
          query: req.query,
          headers: {
            host: req.headers?.host,
            'user-agent': req.headers?.['user-agent'],
            'x-correlation-id': req.headers?.['x-correlation-id'],
            'x-tenant-id': req.headers?.['x-tenant-id'],
          },
        }),
        res: (res: any) => ({
          statusCode: res.statusCode,
        }),
        err: (err: any) => ({
          type: err.type || err.constructor?.name,
          message: err.message,
          stack: err.stack,
        }),
      },

      genReqId: (req: any, res: any) => {
        const correlationId =
          req.headers['x-correlation-id'] ||
          req.headers['x-request-id'] ||
          randomUUID();

        res.setHeader('X-Correlation-ID', correlationId);
        return correlationId;
      },

      base: {
        service: serviceName,
        environment: process.env.ENVIRONMENT || process.env.NODE_ENV || 'development',
      },

      customSuccessMessage: (req: any, res: any) => {
        return `${req.method} ${req.url} ${res.statusCode}`;
      },

      customErrorMessage: (req: any, res: any, err: any) => {
        return `${req.method} ${req.url} ${res.statusCode} - ${err.message}`;
      },

      autoLogging: {
        ignore: (req: any) => {
          const healthPaths = ['/health', '/healthz', '/readyz', '/livez', '/metrics'];
          return healthPaths.some((path) => req.url?.startsWith(path));
        },
      },

      customAttributeKeys: {
        req: 'request',
        res: 'response',
        err: 'error',
        responseTime: 'duration_ms',
      },

      customProps: (req: any) => {
        return {
          correlationId: req.id,
          tenantId: req.headers?.['x-tenant-id'],
          userId: req.headers?.['x-user-id'],
        };
      },

      redact: {
        paths: [
          'request.headers.authorization',
          'request.headers.cookie',
          'request.body.password',
          'request.body.token',
        ],
        remove: true,
      },
    },
  };
}
