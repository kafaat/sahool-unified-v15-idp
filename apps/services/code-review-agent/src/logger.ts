/**
 * Minimal structured logger.
 *
 * Emits JSON lines when LOG_FORMAT=json (suitable for Docker/K8s log ingestion)
 * and pretty human-readable strings otherwise. No external dependencies.
 */

export type LogLevel = "info" | "warn" | "error";

const LEVEL_ORDER: Record<LogLevel, number> = {
  info: 0,
  warn: 1,
  error: 2,
};

export interface LoggerOptions {
  format?: "json" | "pretty";
  minLevel?: LogLevel;
}

function resolveFormat(opts?: LoggerOptions): "json" | "pretty" {
  if (opts?.format) return opts.format;
  return process.env.LOG_FORMAT === "json" ? "json" : "pretty";
}

function resolveMinLevel(opts?: LoggerOptions): LogLevel {
  if (opts?.minLevel) return opts.minLevel;
  const envLevel = (process.env.LOG_LEVEL || "").toLowerCase();
  if (envLevel === "info" || envLevel === "warn" || envLevel === "error") {
    return envLevel;
  }
  return "info";
}

function formatMessage(
  level: LogLevel,
  msg: string,
  meta: Record<string, unknown> | undefined,
  format: "json" | "pretty",
): string {
  const timestamp = new Date().toISOString();
  if (format === "json") {
    return JSON.stringify({ ts: timestamp, level, msg, ...(meta || {}) });
  }
  const metaStr =
    meta && Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : "";
  return `[${timestamp}] ${level.toUpperCase()} ${msg}${metaStr}`;
}

export interface Logger {
  info(msg: string, meta?: Record<string, unknown>): void;
  warn(msg: string, meta?: Record<string, unknown>): void;
  error(msg: string, meta?: Record<string, unknown>): void;
}

export function createLogger(opts?: LoggerOptions): Logger {
  const format = resolveFormat(opts);
  const minLevel = resolveMinLevel(opts);
  const minRank = LEVEL_ORDER[minLevel];

  function emit(
    level: LogLevel,
    msg: string,
    meta?: Record<string, unknown>,
  ): void {
    if (LEVEL_ORDER[level] < minRank) return;
    const line = formatMessage(level, msg, meta, format);
    // stderr for warn/error, stdout for info — keeps reports on stdout clean.
    if (level === "info") {
      // eslint-disable-next-line no-console
      console.log(line);
    } else {
      // eslint-disable-next-line no-console
      console.error(line);
    }
  }

  return {
    info: (msg, meta) => emit("info", msg, meta),
    warn: (msg, meta) => emit("warn", msg, meta),
    error: (msg, meta) => emit("error", msg, meta),
  };
}

/** Default shared logger instance. */
export const logger: Logger = createLogger();
