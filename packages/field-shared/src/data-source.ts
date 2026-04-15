import 'reflect-metadata';
import { DataSource } from 'typeorm';
import { Field } from './entity/Field';
import { FieldBoundaryHistory } from './entity/FieldBoundaryHistory';
import { SyncStatus } from './entity/SyncStatus';
import { PestIncident } from './entity/PestIncident';
import { PestTreatment } from './entity/PestTreatment';

/**
 * SAHOOL Field Core - Database Configuration
 * PostGIS-enabled PostgreSQL connection for geospatial operations
 *
 * Environment Variables (supports two modes):
 *
 * Mode 1 - Connection URL (preferred):
 * - DATABASE_URL: Full PostgreSQL connection string
 *   Example: postgresql://user:pass@host:5432/dbname
 *
 * Mode 2 - Individual variables:
 * - DB_HOST: PostgreSQL host (default: localhost)
 * - DB_PORT: PostgreSQL port (default: 5432)
 * - DB_USER: Database user (default: sahool)
 * - DB_PASSWORD: Database password (required, no default)
 * - DB_NAME: Database name (default: sahool)
 */

interface DbConfig {
  host: string;
  port: number;
  username: string;
  password: string;
  database: string;
}

// Parse DATABASE_URL if provided
function getConnectionConfig(): DbConfig {
  const databaseUrl = process.env.DATABASE_URL;

  if (databaseUrl) {
    try {
      const url = new URL(databaseUrl);
      return {
        host: url.hostname,
        port: parseInt(url.port || '5432'),
        username: url.username || 'sahool',
        password: url.password || '',
        database: url.pathname.slice(1) || 'sahool', // Remove leading '/'
      };
    } catch {
      console.warn('Invalid DATABASE_URL format, falling back to individual env vars');
    }
  }

  // Fallback to individual environment variables
  if (!process.env.DB_PASSWORD) {
    console.warn(
      'WARNING: DB_PASSWORD environment variable is not set. Database connection may fail.'
    );
  }
  return {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    username: process.env.DB_USER || 'sahool',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'sahool',
  };
}

const dbConfig = getConnectionConfig();

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: dbConfig.host,
  port: dbConfig.port,
  username: dbConfig.username,
  password: dbConfig.password,
  database: dbConfig.database,

  // In production, set synchronize to false and use migrations
  synchronize: process.env.NODE_ENV !== 'production',
  logging: process.env.NODE_ENV !== 'production',

  entities: [Field, FieldBoundaryHistory, SyncStatus, PestIncident, PestTreatment],
  migrations: ['dist/migrations/*.js'],
  subscribers: [],

  // Connection pool settings
  extra: {
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
  },
});
