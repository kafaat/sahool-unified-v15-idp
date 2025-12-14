import "reflect-metadata";
import { DataSource } from "typeorm";
import { Field } from "./entity/Field";

/**
 * SAHOOL Field Core - Database Configuration
 * PostGIS-enabled PostgreSQL connection for geospatial operations
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

    entities: [Field],
    migrations: ["dist/migrations/*.js"],
    subscribers: [],

    // Connection pool settings
    extra: {
        max: 10,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
    }
});
