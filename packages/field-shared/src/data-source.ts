import "reflect-metadata";
import { DataSource } from "typeorm";
import { Field } from "./entity/Field";
import { FieldBoundaryHistory } from "./entity/FieldBoundaryHistory";
import { SyncStatus } from "./entity/SyncStatus";
import { PestIncident } from "./entity/PestIncident";
import { PestTreatment } from "./entity/PestTreatment";

/**
 * SAHOOL Field Core - Database Configuration
 * PostGIS-enabled PostgreSQL connection for geospatial operations
 *
 * Environment Variables:
 * - DB_HOST: PostgreSQL host (default: postgres for docker-compose)
 * - DB_PORT: PostgreSQL port (default: 5432)
 * - DB_USER: Database user (default: sahool)
 * - DB_PASSWORD: Database password (default: sahool - MUST match POSTGRES_PASSWORD in .env)
 * - DB_NAME: Database name (default: sahool)
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

    entities: [Field, FieldBoundaryHistory, SyncStatus, PestIncident, PestTreatment],
    migrations: ["dist/migrations/*.js"],
    subscribers: [],

    // Connection pool settings
    extra: {
        max: 10,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
    }
});
