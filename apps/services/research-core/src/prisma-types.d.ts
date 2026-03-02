/**
 * Prisma type declarations for research-core service
 * This file provides types when Prisma client cannot be generated
 */

declare module "../../prisma/generated/client" {
  // Enums from schema.prisma
  export enum ExperimentStatus {
    draft = "draft",
    active = "active",
    locked = "locked",
    completed = "completed",
    archived = "archived",
  }

  export enum SampleType {
    soil = "soil",
    plant = "plant",
    water = "water",
    pest = "pest",
    other = "other",
  }

  export enum TreatmentType {
    fertilizer = "fertilizer",
    pesticide = "pesticide",
    irrigation = "irrigation",
    seed_variety = "seed_variety",
    other = "other",
  }

  export enum LogCategory {
    observation = "observation",
    measurement = "measurement",
    treatment = "treatment",
    harvest = "harvest",
    weather = "weather",
    pest = "pest",
    planting = "planting",
    germination = "germination",
    other = "other",
  }

  export enum GermplasmType {
    seed = "seed",
    cutting = "cutting",
    tissue = "tissue",
    pollen = "pollen",
    other = "other",
  }

  export enum SeedQualityGrade {
    certified = "certified",
    foundation = "foundation",
    registered = "registered",
    breeder = "breeder",
    commercial = "commercial",
    farmer_saved = "farmer_saved",
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

    export type NullableJsonInput = InputJsonValue | null;

    export const DbNull: unique symbol;
    export const JsonNull: unique symbol;

    export type TransactionClient = Omit<
      PrismaClient,
      "$connect" | "$disconnect" | "$on" | "$transaction" | "$use"
    >;
  }

  // Model delegate types
  interface ModelDelegate {
    findUnique(args: any): Promise<any>;
    findUniqueOrThrow(args: any): Promise<any>;
    findFirst(args?: any): Promise<any>;
    findFirstOrThrow(args?: any): Promise<any>;
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
    $queryRaw<T = unknown>(
      query: TemplateStringsArray,
      ...values: unknown[]
    ): Promise<T>;
    $executeRaw(
      query: TemplateStringsArray,
      ...values: unknown[]
    ): Promise<number>;
    $transaction<T>(
      fn: (prisma: Prisma.TransactionClient) => Promise<T>
    ): Promise<T>;

    // Model accessors from schema
    germplasm: ModelDelegate;
    seedLot: ModelDelegate;
    planting: ModelDelegate;
    experiment: ModelDelegate;
    researchProtocol: ModelDelegate;
    researchPlot: ModelDelegate;
    treatment: ModelDelegate;
    researchDailyLog: ModelDelegate;
    labSample: ModelDelegate;
    digitalSignature: ModelDelegate;
    experimentCollaborator: ModelDelegate;
    experimentAuditLog: ModelDelegate;
  }
}
