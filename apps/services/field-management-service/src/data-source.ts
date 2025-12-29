import "reflect-metadata";
import { DataSource } from "typeorm";
import { Field } from "./entity/Field";
import { FieldBoundaryHistory } from "./entity/FieldBoundaryHistory";
import { SyncStatus } from "./entity/SyncStatus";

/**
 * SAHOOL Field Management Service - Database Configuration
 * PostGIS-enabled PostgreSQL connection for geospatial operations
 *
 * Environment Variables:
 * - DB_HOST: PostgreSQL host (default: postgres for docker-compose, use pgbouncer for production)
 * - DB_PORT: PostgreSQL port (default: 5432, use 6432 for PgBouncer)
 * - DB_USER: Database user (default: sahool)
 * - DB_PASSWORD: Database password (default: sahool - MUST match POSTGRES_PASSWORD in .env)
 * - DB_NAME: Database name (default: sahool)
 * - DB_POOL_SIZE: Maximum pool size (default: 50)
 *
 * Connection Pool Best Practices:
 * - With PgBouncer: Set pool size lower (10-20) as PgBouncer manages pooling
 * - Without PgBouncer: Use larger pool (50) to handle 39+ services
 * - For production: Always use PgBouncer for better connection management
 */
export const AppDataSource = new DataSource({
    type: "postgres",
    host: process.env.DB_HOST || "postgres",
    port: parseInt(process.env.DB_PORT || "5432"),
    username: process.env.DB_USER || "sahool",
    password: process.env.DB_PASSWORD || "sahool",
    database: process.env.DB_NAME || "sahool",

    // In production, set synchronize to false and use migrations
    synchronize: process.env.NODE_ENV !== "production",
    logging: process.env.NODE_ENV !== "production",

    entities: [Field, FieldBoundaryHistory, SyncStatus],
    migrations: ["dist/migrations/*.js"],
    subscribers: [],

    // Connection pool settings - optimized for high-service environment
    extra: {
        // Maximum number of clients in the pool
        max: parseInt(process.env.DB_POOL_SIZE || "50"),

        // Minimum number of clients to keep alive
        min: 5,

        // Maximum time (ms) a client can be idle before being closed (5 minutes)
        idleTimeoutMillis: 300000,

        // Maximum time (ms) to wait for a connection from the pool (10 seconds)
        connectionTimeoutMillis: 10000,

        // Maximum time (ms) to wait for query execution (2 minutes)
        statement_timeout: 120000,

        // Application name for monitoring
        application_name: "field-management-service",

        // Keep-alive settings for long-lived connections
        keepAlive: true,
        keepAliveInitialDelayMillis: 10000,
    }
});

/**
 * Health check function for connection pool
 * Returns pool statistics for monitoring
 */
export async function getPoolHealth() {
    try {
        const result = await AppDataSource.query('SELECT 1');
        return {
            healthy: true,
            totalConnections: AppDataSource.driver.master?.pool?.totalCount || 0,
            idleConnections: AppDataSource.driver.master?.pool?.idleCount || 0,
            waitingConnections: AppDataSource.driver.master?.pool?.waitingCount || 0,
        };
    } catch (error) {
        return {
            healthy: false,
            error: error instanceof Error ? error.message : String(error),
        };
    }
}
