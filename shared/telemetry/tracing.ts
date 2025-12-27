/**
 * OpenTelemetry Distributed Tracing for SAHOOL Platform (TypeScript/NestJS)
 * ==========================================================================
 *
 * This module provides comprehensive distributed tracing instrumentation for all
 * TypeScript-based services (NestJS) in the SAHOOL agricultural platform.
 *
 * Features:
 * - Auto-instrumentation for NestJS, HTTP, Prisma, PostgreSQL
 * - OTLP exporter configuration for Jaeger/Zipkin
 * - Custom span creation helpers
 * - Context propagation
 * - Service name auto-detection
 *
 * Usage:
 *     import { initTracer, instrumentNestApp, trace } from './shared/telemetry/tracing';
 *
 *     // Initialize at application startup
 *     const sdk = initTracer({ serviceName: 'field-service' });
 *
 *     // Instrument NestJS app
 *     await instrumentNestApp(app);
 *
 *     // Use decorator for automatic tracing
 *     @Trace('processField')
 *     async processField(fieldId: string) {
 *       // ... your code
 *     }
 *
 * Author: SAHOOL Platform Team
 * Date: 2025-12-26
 */

import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { Resource } from '@opentelemetry/resources';
import {
  SEMRESATTRS_SERVICE_NAME,
  SEMRESATTRS_SERVICE_VERSION,
  SEMRESATTRS_DEPLOYMENT_ENVIRONMENT,
} from '@opentelemetry/semantic-conventions';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { ConsoleSpanExporter } from '@opentelemetry/sdk-trace-base';
import { BatchSpanProcessor, ParentBasedSampler, TraceIdRatioBasedSampler } from '@opentelemetry/sdk-trace-node';
import { trace, context, Span, SpanStatusCode } from '@opentelemetry/api';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { NestInstrumentation } from '@opentelemetry/instrumentation-nestjs-core';
import { PrismaInstrumentation } from '@prisma/instrumentation';

let tracerProvider: NodeSDK | null = null;

export interface TracingConfig {
  serviceName?: string;
  serviceVersion?: string;
  environment?: string;
  otlpEndpoint?: string;
  consoleExport?: boolean;
  samplingRatio?: number;
}

/**
 * Initialize OpenTelemetry tracing with OTLP exporter
 */
export function initTracer(config: TracingConfig = {}): NodeSDK {
  // Auto-detect service name from environment
  const serviceName =
    config.serviceName ||
    process.env.OTEL_SERVICE_NAME ||
    process.env.SERVICE_NAME ||
    'sahool-service';

  const serviceVersion = config.serviceVersion || process.env.SERVICE_VERSION || '1.0.0';
  const environment = config.environment || process.env.ENVIRONMENT || 'development';
  const otlpEndpoint = config.otlpEndpoint || process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://otel-collector:4317';
  const samplingRatio = config.samplingRatio ?? parseFloat(process.env.OTEL_TRACES_SAMPLER_ARG || '0.1');
  const consoleExport = config.consoleExport ?? process.env.OTEL_CONSOLE_EXPORT === 'true';

  // Create resource with service information
  const resource = Resource.default().merge(
    new Resource({
      [SEMRESATTRS_SERVICE_NAME]: serviceName,
      [SEMRESATTRS_SERVICE_VERSION]: serviceVersion,
      [SEMRESATTRS_DEPLOYMENT_ENVIRONMENT]: environment,
      'service.namespace': 'sahool',
      'service.instance.id': process.env.HOSTNAME || 'unknown',
    })
  );

  // Configure span processors
  const spanProcessors = [];

  // Add OTLP exporter
  try {
    const otlpExporter = new OTLPTraceExporter({
      url: otlpEndpoint,
    });
    spanProcessors.push(new BatchSpanProcessor(otlpExporter));
    console.log(`OTLP trace exporter configured: ${otlpEndpoint}`);
  } catch (error) {
    console.warn(`Failed to configure OTLP exporter:`, error);
  }

  // Add console exporter for debugging
  if (consoleExport) {
    spanProcessors.push(new BatchSpanProcessor(new ConsoleSpanExporter()));
    console.log('Console trace exporter enabled');
  }

  // Configure sampling
  const sampler = new ParentBasedSampler({
    root: new TraceIdRatioBasedSampler(samplingRatio),
  });

  // Initialize NodeSDK
  tracerProvider = new NodeSDK({
    resource,
    spanProcessors,
    sampler,
    instrumentations: [
      // Auto-instrument Node.js core modules
      getNodeAutoInstrumentations({
        '@opentelemetry/instrumentation-fs': {
          enabled: false, // Too noisy
        },
        '@opentelemetry/instrumentation-dns': {
          enabled: false, // Too noisy
        },
      }),
      // NestJS instrumentation
      new NestInstrumentation(),
      // HTTP instrumentation
      new HttpInstrumentation({
        ignoreIncomingPaths: ['/health', '/metrics', '/ready'],
      }),
      // Prisma instrumentation (if using Prisma)
      new PrismaInstrumentation(),
    ],
  });

  tracerProvider.start();

  console.log(
    `OpenTelemetry tracer initialized: service=${serviceName}, env=${environment}, sampling=${samplingRatio}`
  );

  // Graceful shutdown
  process.on('SIGTERM', () => {
    tracerProvider
      ?.shutdown()
      .then(() => console.log('Tracing terminated'))
      .catch((error) => console.error('Error terminating tracing', error))
      .finally(() => process.exit(0));
  });

  return tracerProvider;
}

/**
 * Get a tracer instance
 */
export function getTracer(name?: string) {
  return trace.getTracer(name || 'sahool-tracer');
}

/**
 * Instrument NestJS application
 */
export function instrumentNestApp(app: any): void {
  // NestJS instrumentation is handled automatically by NestInstrumentation
  console.log('NestJS instrumentation enabled');
}

/**
 * Decorator to trace a method
 */
export function Trace(spanName?: string, attributes?: Record<string, any>) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    const traceName = spanName || `${target.constructor.name}.${propertyKey}`;

    descriptor.value = async function (...args: any[]) {
      const tracer = getTracer();
      return tracer.startActiveSpan(traceName, async (span: Span) => {
        try {
          // Add custom attributes
          if (attributes) {
            Object.entries(attributes).forEach(([key, value]) => {
              span.setAttribute(key, value);
            });
          }

          // Add method metadata
          span.setAttribute('code.function', propertyKey);
          span.setAttribute('code.namespace', target.constructor.name);

          // Execute method
          const result = await originalMethod.apply(this, args);

          span.setStatus({ code: SpanStatusCode.OK });
          return result;
        } catch (error) {
          span.setStatus({
            code: SpanStatusCode.ERROR,
            message: error instanceof Error ? error.message : String(error),
          });
          span.recordException(error as Error);
          throw error;
        } finally {
          span.end();
        }
      });
    };

    return descriptor;
  };
}

/**
 * Helper to add attributes to current span
 */
export function addSpanAttributes(attributes: Record<string, any>): void {
  const span = trace.getActiveSpan();
  if (span) {
    Object.entries(attributes).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        span.setAttribute(key, value);
      }
    });
  }
}

/**
 * Helper to record exception in current span
 */
export function recordException(error: Error): void {
  const span = trace.getActiveSpan();
  if (span) {
    span.recordException(error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message,
    });
  }
}

/**
 * Get current trace ID for logging correlation
 */
export function getCurrentTraceId(): string | undefined {
  const span = trace.getActiveSpan();
  if (span) {
    const spanContext = span.spanContext();
    return spanContext.traceId;
  }
  return undefined;
}

/**
 * Get current span ID for logging correlation
 */
export function getCurrentSpanId(): string | undefined {
  const span = trace.getActiveSpan();
  if (span) {
    const spanContext = span.spanContext();
    return spanContext.spanId;
  }
  return undefined;
}

/**
 * Create a custom span
 */
export async function withSpan<T>(
  name: string,
  fn: (span: Span) => Promise<T>,
  attributes?: Record<string, any>
): Promise<T> {
  const tracer = getTracer();
  return tracer.startActiveSpan(name, async (span: Span) => {
    try {
      if (attributes) {
        Object.entries(attributes).forEach(([key, value]) => {
          span.setAttribute(key, value);
        });
      }

      const result = await fn(span);
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error instanceof Error ? error.message : String(error),
      });
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  });
}

/**
 * Service name mappings for all SAHOOL services (TypeScript)
 */
export const SAHOOL_SERVICES = {
  // Communication services
  chat_service: 'Chat Service',
  community_chat: 'Community Chat Service',
  field_chat: 'Field Chat Service',
  notification_service: 'Notification Service',

  // Business services
  billing_core: 'Billing Core Service',
  marketplace_service: 'Marketplace Service',
  inventory_service: 'Inventory Management',
  equipment_service: 'Equipment Management',
  task_service: 'Task Management Service',

  // Infrastructure
  ws_gateway: 'WebSocket Gateway',
  kong: 'API Gateway (Kong)',
} as const;

export default {
  initTracer,
  getTracer,
  instrumentNestApp,
  Trace,
  addSpanAttributes,
  recordException,
  getCurrentTraceId,
  getCurrentSpanId,
  withSpan,
  SAHOOL_SERVICES,
};
