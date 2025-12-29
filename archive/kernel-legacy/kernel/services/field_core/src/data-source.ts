import "reflect-metadata";
import { DataSource } from "typeorm";
import { Field } from "./entity/Field";
import { FieldBoundaryHistory } from "./entity/FieldBoundaryHistory";
import { SyncStatus } from "./entity/SyncStatus";

/**
 * SAHOOL Field Core - Database Configuration
 * PostGIS-enabled PostgreSQL connection for geospatial operations
 *
 * Environment Variables (REQUIRED):
 * - DB_HOST: PostgreSQL host (default: postgres for docker-compose)
 * - DB_PORT: PostgreSQL port (default: 5432)
 * - DB_USER: Database user (default: sahool)
 * - DB_PASSWORD: Database password (REQUIRED - must be set via environment variable)
 * - DB_NAME: Database name (default: sahool)
 *
 * Security:
 * - DB_PASSWORD must be set via environment variable in production
 * - Never use hardcoded passwords
 */

// Validate required environment variables at startup
if (process.env.NODE_ENV === 'production' && !process.env.DB_PASSWORD) {
    throw new Error(
        'SECURITY ERROR: DB_PASSWORD environment variable must be set in production. ' +
        'Never use hardcoded passwords. Please set DB_PASSWORD in your .env file or environment.'
    );
}

export const AppDataSource = new DataSource({
    type: "postgres",
    host: process.env.DB_HOST || "postgres",
    port: parseInt(process.env.DB_PORT || "5432"),
    username: process.env.DB_USER || "sahool",
    password: process.env.DB_PASSWORD || (() => {
        if (process.env.NODE_ENV === 'production') {
            throw new Error('DB_PASSWORD must be set in production');
        }
        console.warn('WARNING: Using development mode without DB_PASSWORD set. This is insecure for production!');
        return undefined;
    })(),
    database: process.env.DB_NAME || "sahool",

    // In production, set synchronize to false and use migrations
    synchronize: process.env.NODE_ENV !== "production",
    logging: process.env.NODE_ENV !== "production",

    entities: [Field, FieldBoundaryHistory, SyncStatus],
    migrations: ["dist/migrations/*.js"],
    subscribers: [],

    // Connection pool settings
    extra: {
        max: 10,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
    }
});
