/**
 * Prisma type declarations for disaster-assessment service
 * This file provides types when Prisma client cannot be generated
 */

declare module "@prisma/client" {
  // Enums from schema.prisma
  export enum DisasterType {
    flood = "flood",
    drought = "drought",
    frost = "frost",
    hail = "hail",
    storm = "storm",
    pest = "pest",
    disease = "disease",
    locust = "locust",
    wildfire = "wildfire",
  }

  export enum DisasterSeverity {
    low = "low",
    medium = "medium",
    high = "high",
    critical = "critical",
  }

  export enum DisasterStatus {
    reported = "reported",
    verified = "verified",
    active = "active",
    monitoring = "monitoring",
    resolved = "resolved",
    archived = "archived",
  }

  export enum DisasterAlertType {
    weather = "weather",
    pest = "pest",
    disease = "disease",
    flood = "flood",
    drought = "drought",
    frost = "frost",
    locust = "locust",
    general = "general",
  }

  // Prisma namespace types
  export namespace Prisma {
    export type InputJsonValue =
      | string
      | number
      | boolean
      | null
      | { [key: string]: InputJsonValue }
      | InputJsonValue[];

    export type JsonValue =
      | string
      | number
      | boolean
      | null
      | { [key: string]: JsonValue }
      | JsonValue[];
  }

  // Model delegate types
  interface ModelDelegate {
    findUnique(args: any): Promise<any>;
    findFirst(args?: any): Promise<any>;
    findMany(args?: any): Promise<any[]>;
    create(args: any): Promise<any>;
    createMany(args: any): Promise<any>;
    update(args: any): Promise<any>;
    updateMany(args: any): Promise<any>;
    delete(args: any): Promise<any>;
    deleteMany(args?: any): Promise<any>;
    count(args?: any): Promise<number>;
    aggregate(args: any): Promise<any>;
    groupBy(args: any): Promise<any[]>;
    upsert(args: any): Promise<any>;
  }

  interface PrismaClientOptions {
    log?: Array<{ level: string; emit: string }>;
    datasources?: {
      db?: { url?: string };
    };
  }

  // PrismaClient class
  export class PrismaClient {
    constructor(options?: PrismaClientOptions);
    $connect(): Promise<void>;
    $disconnect(): Promise<void>;
    $queryRaw<T = unknown>(query: TemplateStringsArray, ...values: unknown[]): Promise<T>;
    $executeRaw(query: TemplateStringsArray, ...values: unknown[]): Promise<number>;

    // Model accessors from schema
    disasterReport: ModelDelegate;
    disasterAlert: ModelDelegate;
    fieldAssessment: ModelDelegate;
    alertSubscription: ModelDelegate;
  }
}
