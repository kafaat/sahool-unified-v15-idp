/**
 * Cache Warming Service
 * =====================
 *
 * Implements proactive cache warming strategies to reduce cold start latency
 *
 * @author SAHOOL Platform Team
 */

import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { CacheManager, CacheTTL } from './cache-manager';

export interface WarmingStrategy {
  /** Strategy name */
  name: string;
  /** Keys to warm */
  getKeys: () => Promise<string[]>;
  /** Data fetcher */
  fetcher: (key: string) => Promise<any>;
  /** TTL for warmed data */
  ttl: number;
  /** Enable this strategy */
  enabled: boolean;
}

@Injectable()
export class CacheWarmingService implements OnModuleInit {
  private readonly logger = new Logger(CacheWarmingService.name);
  private strategies: WarmingStrategy[] = [];
  private isWarming = false;

  constructor(private readonly cacheManager: CacheManager) {}

  /**
   * Initialize and warm cache on application startup
   */
  async onModuleInit() {
    this.logger.log('🔥 Initializing cache warming...');
    await this.warmOnStartup();
  }

  /**
   * Register a warming strategy
   */
  registerStrategy(strategy: WarmingStrategy): void {
    this.strategies.push(strategy);
    this.logger.log(`Registered warming strategy: ${strategy.name}`);
  }

  /**
   * Warm cache on application startup
   */
  private async warmOnStartup(): Promise<void> {
    if (this.isWarming) {
      this.logger.warn('Warming already in progress, skipping...');
      return;
    }

    this.isWarming = true;

    try {
      const enabledStrategies = this.strategies.filter((s) => s.enabled);

      if (enabledStrategies.length === 0) {
        this.logger.log('No warming strategies enabled');
        return;
      }

      this.logger.log(`Warming cache with ${enabledStrategies.length} strategies...`);

      for (const strategy of enabledStrategies) {
        try {
          await this.executeStrategy(strategy);
        } catch (error) {
          this.logger.error(
            `Failed to execute warming strategy ${strategy.name}: ${error.message}`,
          );
        }
      }

      this.logger.log('✅ Cache warming completed');
    } finally {
      this.isWarming = false;
    }
  }

  /**
   * Execute a single warming strategy
   */
  private async executeStrategy(strategy: WarmingStrategy): Promise<void> {
    const startTime = Date.now();
    this.logger.log(`Executing warming strategy: ${strategy.name}`);

    try {
      const keys = await strategy.getKeys();

      if (keys.length === 0) {
        this.logger.log(`No keys to warm for strategy: ${strategy.name}`);
        return;
      }

      await this.cacheManager.warm({
        keys,
        fetcher: strategy.fetcher,
        ttl: strategy.ttl,
      });

      const duration = Date.now() - startTime;
      this.logger.log(
        `Strategy ${strategy.name} completed: ${keys.length} keys warmed in ${duration}ms`,
      );
    } catch (error) {
      this.logger.error(`Strategy ${strategy.name} failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Periodic cache warming (every 5 minutes)
   * Refreshes critical cache entries before they expire
   */
  @Cron(CronExpression.EVERY_5_MINUTES)
  async periodicWarming(): Promise<void> {
    if (this.isWarming) {
      this.logger.debug('Warming already in progress, skipping periodic warming');
      return;
    }

    this.logger.debug('Running periodic cache warming...');
    await this.warmOnStartup();
  }

  /**
   * Predictive warming based on usage patterns
   * Warms cache during off-peak hours (2 AM - 6 AM)
   */
  @Cron('0 2-6 * * *') // Every hour between 2 AM and 6 AM
  async predictiveWarming(): Promise<void> {
    this.logger.log('Running predictive cache warming for off-peak hours...');

    // Warm high-traffic data during off-peak hours
    const predictiveStrategies = this.strategies.filter(
      (s) => s.enabled && s.name.includes('predictive'),
    );

    for (const strategy of predictiveStrategies) {
      try {
        await this.executeStrategy(strategy);
      } catch (error) {
        this.logger.error(
          `Predictive warming failed for ${strategy.name}: ${error.message}`,
        );
      }
    }
  }

  /**
   * Manual cache warming trigger
   */
  async warmNow(strategyName?: string): Promise<void> {
    if (strategyName) {
      const strategy = this.strategies.find((s) => s.name === strategyName);
      if (!strategy) {
        throw new Error(`Strategy not found: ${strategyName}`);
      }
      await this.executeStrategy(strategy);
    } else {
      await this.warmOnStartup();
    }
  }

  /**
   * Get warming statistics
   */
  getStats() {
    return {
      totalStrategies: this.strategies.length,
      enabledStrategies: this.strategies.filter((s) => s.enabled).length,
      isWarming: this.isWarming,
      strategies: this.strategies.map((s) => ({
        name: s.name,
        enabled: s.enabled,
        ttl: s.ttl,
      })),
    };
  }
}

// =============================================================================
// Predefined Warming Strategies
// =============================================================================

/**
 * Example: Warm frequently accessed user data
 */
export function createUserWarmingStrategy(
  getTopUserIds: () => Promise<string[]>,
  fetchUserData: (userId: string) => Promise<any>,
): WarmingStrategy {
  return {
    name: 'user-validation-warming',
    getKeys: async () => {
      const userIds = await getTopUserIds();
      return userIds.map((id) => `user_auth:${id}`);
    },
    fetcher: fetchUserData,
    ttl: CacheTTL.USER_VALIDATION,
    enabled: true,
  };
}

/**
 * Example: Warm field data for active fields
 */
export function createFieldWarmingStrategy(
  getActiveFieldIds: () => Promise<string[]>,
  fetchFieldData: (fieldId: string) => Promise<any>,
): WarmingStrategy {
  return {
    name: 'field-data-warming',
    getKeys: async () => {
      const fieldIds = await getActiveFieldIds();
      return fieldIds.map((id) => `field:${id}`);
    },
    fetcher: fetchFieldData,
    ttl: CacheTTL.FIELD_DATA,
    enabled: true,
  };
}

/**
 * Example: Predictive warming for daytime hours
 */
export function createPredictiveWarmingStrategy(
  getPopularItems: () => Promise<Array<{ type: string; id: string }>>,
  fetchItem: (type: string, id: string) => Promise<any>,
): WarmingStrategy {
  return {
    name: 'predictive-daytime-warming',
    getKeys: async () => {
      const items = await getPopularItems();
      return items.map((item) => `${item.type}:${item.id}`);
    },
    fetcher: async (key: string) => {
      const [type, id] = key.split(':');
      return fetchItem(type, id);
    },
    ttl: CacheTTL.FIELD_DATA,
    enabled: true,
  };
}
