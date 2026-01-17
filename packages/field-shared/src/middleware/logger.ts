/**
 * SAHOOL Structured Logger
 * Provides JSON structured logging for production environments
 */

import { Request, Response, NextFunction } from "express";

export enum LogLevel {
  DEBUG = "debug",
  INFO = "info",
  WARN = "warn",
  ERROR = "error",
  FATAL = "fatal",
}

interface LogContext {
  requestId?: string;
  tenantId?: string;
  userId?: string;
  traceId?: string;
  spanId?: string;
  [key: string]: any;
}

interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  service: string;
  version: string;
  context?: LogContext;
  error?: {
    name: string;
    message: string;
    stack?: string;
  };
  http?: {
    method: string;
    url: string;
    statusCode?: number;
    duration?: number;
    userAgent?: string;
    ip?: string;
  };
  [key: string]: any;
}

class Logger {
  private service: string;
  private version: string;
  private defaultContext: LogContext;

  constructor(service: string = "field-core", version: string = "15.3.0") {
    this.service = service;
    this.version = version;
    this.defaultContext = {};
  }

  private formatEntry(
    level: LogLevel,
    message: string,
    context?: LogContext,
    extra?: Record<string, any>,
  ): LogEntry {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      service: this.service,
      version: this.version,
      context: { ...this.defaultContext, ...context },
      ...extra,
    };
  }

  private output(entry: LogEntry): void {
    const json = JSON.stringify(entry);

    if (entry.level === LogLevel.ERROR || entry.level === LogLevel.FATAL) {
      console.error(json);
    } else if (entry.level === LogLevel.WARN) {
      console.warn(json);
    } else {
      console.log(json);
    }
  }

  debug(
    message: string,
    context?: LogContext,
    extra?: Record<string, any>,
  ): void {
    if (process.env.LOG_LEVEL === "debug") {
      this.output(this.formatEntry(LogLevel.DEBUG, message, context, extra));
    }
  }

  info(
    message: string,
    context?: LogContext,
    extra?: Record<string, any>,
  ): void {
    this.output(this.formatEntry(LogLevel.INFO, message, context, extra));
  }

  warn(
    message: string,
    context?: LogContext,
    extra?: Record<string, any>,
  ): void {
    this.output(this.formatEntry(LogLevel.WARN, message, context, extra));
  }

  error(
    message: string,
    error?: Error,
    context?: LogContext,
    extra?: Record<string, any>,
  ): void {
    const entry = this.formatEntry(LogLevel.ERROR, message, context, extra);
    if (error) {
      entry.error = {
        name: error.name,
        message: error.message,
        stack: process.env.NODE_ENV !== "production" ? error.stack : undefined,
      };
    }
    this.output(entry);
  }

  fatal(
    message: string,
    error?: Error,
    context?: LogContext,
    extra?: Record<string, any>,
  ): void {
    const entry = this.formatEntry(LogLevel.FATAL, message, context, extra);
    if (error) {
      entry.error = {
        name: error.name,
        message: error.message,
        stack: error.stack,
      };
    }
    this.output(entry);
  }

  http(
    method: string,
    url: string,
    statusCode: number,
    duration: number,
    context?: LogContext,
    extra?: Record<string, any>,
  ): void {
    const level =
      statusCode >= 500
        ? LogLevel.ERROR
        : statusCode >= 400
          ? LogLevel.WARN
          : LogLevel.INFO;

    const entry = this.formatEntry(
      level,
      `${method} ${url} ${statusCode}`,
      context,
      extra,
    );
    entry.http = {
      method,
      url,
      statusCode,
      duration,
    };
    this.output(entry);
  }

  child(context: LogContext): Logger {
    const childLogger = new Logger(this.service, this.version);
    childLogger.defaultContext = { ...this.defaultContext, ...context };
    return childLogger;
  }
}

// Global logger instance
export const logger = new Logger(
  process.env.SERVICE_NAME || "field-core",
  process.env.SERVICE_VERSION || "15.3.0",
);

// Generate unique request ID
function generateRequestId(): string {
  return `req_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 9)}`;
}

// Express middleware for request logging
export function requestLogger(
  req: Request,
  res: Response,
  next: NextFunction,
): void {
  const startTime = Date.now();

  // Generate or use existing request ID
  const requestId =
    (req.headers["x-request-id"] as string) || generateRequestId();
  const tenantId = req.headers["x-tenant-id"] as string;
  const traceId = req.headers["x-trace-id"] as string;

  // Add to request for downstream use
  (req as any).requestId = requestId;
  (req as any).logger = logger.child({ requestId, tenantId, traceId });

  // Set response header
  res.setHeader("X-Request-ID", requestId);

  // Log request start
  logger.debug(
    "Request started",
    { requestId, tenantId },
    {
      http: {
        method: req.method,
        url: req.originalUrl,
        userAgent: req.headers["user-agent"],
        ip: req.ip || req.socket.remoteAddress,
      },
    },
  );

  // Log response on finish
  res.on("finish", () => {
    const duration = Date.now() - startTime;

    logger.http(
      req.method,
      req.originalUrl,
      res.statusCode,
      duration,
      { requestId, tenantId },
      {
        http: {
          method: req.method,
          url: req.originalUrl,
          statusCode: res.statusCode,
          duration,
          userAgent: req.headers["user-agent"],
          ip: req.ip || req.socket.remoteAddress,
        },
      },
    );
  });

  next();
}

// Error logging middleware
export function errorLogger(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction,
): void {
  const requestId = (req as any).requestId;
  const tenantId = req.headers["x-tenant-id"] as string;

  logger.error(
    `Request failed: ${err.message}`,
    err,
    { requestId, tenantId },
    {
      http: {
        method: req.method,
        url: req.originalUrl,
      },
    },
  );

  next(err);
}

export default logger;
