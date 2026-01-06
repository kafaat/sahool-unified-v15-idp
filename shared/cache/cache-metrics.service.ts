/**
 * Cache Metrics Service
 * ====================
 *
 * Provides detailed cache performance metrics and monitoring
 *
 * @author SAHOOL Platform Team
 */

import { Injectable, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';

export interface DetailedCacheMetrics {
  // Hit/Miss metrics
  hits: number;
  misses: number;
  hitRate: number;

  // Operation metrics
  sets: number;
  deletes: number;
  errors: number;

  // Performance metrics
  stampedePreventions: number;
  averageGetLatency: number;
  averageSetLatency: number;

  // Memory metrics
  memoryUsage?: number;
  keyCount?: number;
  evictions?: number;

  // Time window
  windowStart: number;
  windowEnd: number;
}

export interface CacheHealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  hitRate: number;
  errorRate: number;
  issues: string[];
  recommendations: string[];
}

@Injectable()
export class CacheMetricsService {
  private readonly logger = new Logger(CacheMetricsService.name);

  private metrics: DetailedCacheMetrics;
  private latencies: {
    get: number[];
    set: number[];
  };

  constructor() {
    this.resetMetrics();
    this.latencies = {
      get: [],
      set: [],
    };
  }

  /**
   * Record a cache hit
   */
  recordHit(): void {
    this.metrics.hits++;
  }

  /**
   * Record a cache miss
   */
  recordMiss(): void {
    this.metrics.misses++;
  }

  /**
   * Record a cache set operation
   */
  recordSet(latencyMs?: number): void {
    this.metrics.sets++;
    if (latencyMs !== undefined) {
      this.recordSetLatency(latencyMs);
    }
  }

  /**
   * Record a cache delete operation
   */
  recordDelete(): void {
    this.metrics.deletes++;
  }

  /**
   * Record a cache error
   */
  recordError(): void {
    this.metrics.errors++;
  }

  /**
   * Record stampede prevention
   */
  recordStampedePrevention(): void {
    this.metrics.stampedePreventions++;
  }

  /**
   * Record GET operation latency
   */
  recordGetLatency(ms: number): void {
    this.latencies.get.push(ms);

    // Keep only last 1000 measurements
    if (this.latencies.get.length > 1000) {
      this.latencies.get.shift();
    }
  }

  /**
   * Record SET operation latency
   */
  recordSetLatency(ms: number): void {
    this.latencies.set.push(ms);

    // Keep only last 1000 measurements
    if (this.latencies.set.length > 1000) {
      this.latencies.set.shift();
    }
  }

  /**
   * Get current metrics
   */
  getMetrics(): DetailedCacheMetrics {
    const total = this.metrics.hits + this.metrics.misses;
    this.metrics.hitRate = total > 0 ? this.metrics.hits / total : 0;
    this.metrics.averageGetLatency = this.calculateAverage(this.latencies.get);
    this.metrics.averageSetLatency = this.calculateAverage(this.latencies.set);
    this.metrics.windowEnd = Date.now();

    return { ...this.metrics };
  }

  /**
   * Get cache health status with recommendations
   */
  getHealthStatus(): CacheHealthStatus {
    const metrics = this.getMetrics();
    const total = metrics.hits + metrics.misses;
    const errorRate = total > 0 ? metrics.errors / (total + metrics.errors) : 0;

    const issues: string[] = [];
    const recommendations: string[] = [];
    let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';

    // Check hit rate
    if (metrics.hitRate < 0.5) {
      issues.push(`Low hit rate: ${(metrics.hitRate * 100).toFixed(1)}%`);
      recommendations.push('Consider increasing TTL or implementing cache warming');
      status = 'degraded';
    } else if (metrics.hitRate < 0.3) {
      status = 'unhealthy';
    }

    // Check error rate
    if (errorRate > 0.05) {
      issues.push(`High error rate: ${(errorRate * 100).toFixed(1)}%`);
      recommendations.push('Check Redis connection and error logs');
      status = 'degraded';
    } else if (errorRate > 0.1) {
      status = 'unhealthy';
    }

    // Check latency
    if (metrics.averageGetLatency > 10) {
      issues.push(`High GET latency: ${metrics.averageGetLatency.toFixed(2)}ms`);
      recommendations.push('Consider Redis optimization or scaling');
      status = status === 'unhealthy' ? 'unhealthy' : 'degraded';
    }

    if (metrics.averageSetLatency > 20) {
      issues.push(`High SET latency: ${metrics.averageSetLatency.toFixed(2)}ms`);
      recommendations.push('Check Redis write performance');
      status = status === 'unhealthy' ? 'unhealthy' : 'degraded';
    }

    // Check stampede prevention effectiveness
    const stampedeRate = total > 0 ? metrics.stampedePreventions / total : 0;
    if (stampedeRate > 0.1) {
      issues.push(`High stampede prevention rate: ${(stampedeRate * 100).toFixed(1)}%`);
      recommendations.push('Consider increasing cache TTL or implementing predictive warming');
    }

    return {
      status,
      hitRate: metrics.hitRate,
      errorRate,
      issues,
      recommendations,
    };
  }

  /**
   * Get percentile latency
   */
  getLatencyPercentile(operation: 'get' | 'set', percentile: number): number {
    const latencies = this.latencies[operation];
    if (latencies.length === 0) return 0;

    const sorted = [...latencies].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index] || 0;
  }

  /**
   * Get detailed latency statistics
   */
  getLatencyStats(operation: 'get' | 'set') {
    return {
      average: this.calculateAverage(this.latencies[operation]),
      p50: this.getLatencyPercentile(operation, 50),
      p95: this.getLatencyPercentile(operation, 95),
      p99: this.getLatencyPercentile(operation, 99),
      count: this.latencies[operation].length,
    };
  }

  /**
   * Reset all metrics
   */
  resetMetrics(): void {
    this.metrics = {
      hits: 0,
      misses: 0,
      hitRate: 0,
      sets: 0,
      deletes: 0,
      errors: 0,
      stampedePreventions: 0,
      averageGetLatency: 0,
      averageSetLatency: 0,
      windowStart: Date.now(),
      windowEnd: Date.now(),
    };
    this.latencies = {
      get: [],
      set: [],
    };
  }

  /**
   * Log metrics summary (runs every 5 minutes)
   */
  @Cron(CronExpression.EVERY_5_MINUTES)
  logMetricsSummary(): void {
    const metrics = this.getMetrics();
    const health = this.getHealthStatus();

    this.logger.log(`
╔═══════════════════════════════════════════════════════════╗
║             CACHE METRICS SUMMARY                         ║
╠═══════════════════════════════════════════════════════════╣
║ Hit Rate:        ${(metrics.hitRate * 100).toFixed(1)}%                               ║
║ Total Requests:  ${(metrics.hits + metrics.misses).toLocaleString()}                                 ║
║ Cache Hits:      ${metrics.hits.toLocaleString()}                                 ║
║ Cache Misses:    ${metrics.misses.toLocaleString()}                                 ║
║ Sets:            ${metrics.sets.toLocaleString()}                                 ║
║ Deletes:         ${metrics.deletes.toLocaleString()}                                 ║
║ Errors:          ${metrics.errors.toLocaleString()}                                 ║
║ Stampede Prev:   ${metrics.stampedePreventions.toLocaleString()}                                 ║
╠═══════════════════════════════════════════════════════════╣
║ GET Latency:     ${metrics.averageGetLatency.toFixed(2)}ms (avg)                      ║
║ SET Latency:     ${metrics.averageSetLatency.toFixed(2)}ms (avg)                      ║
╠═══════════════════════════════════════════════════════════╣
║ Health Status:   ${health.status.toUpperCase()}                              ║
${health.issues.length > 0 ? '║ Issues:                                               ║\n' + health.issues.map(i => `║   - ${i.padEnd(52)}║`).join('\n') : ''}
${health.recommendations.length > 0 ? '║ Recommendations:                                      ║\n' + health.recommendations.map(r => `║   - ${r.padEnd(52)}║`).join('\n') : ''}
╚═══════════════════════════════════════════════════════════╝
    `.trim());

    // Reset metrics after logging (rolling window)
    // Comment out if you want cumulative metrics
    // this.resetMetrics();
  }

  /**
   * Calculate average of an array
   */
  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    const sum = values.reduce((a, b) => a + b, 0);
    return sum / values.length;
  }
}
