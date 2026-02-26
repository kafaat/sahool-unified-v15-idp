/**
 * Prisma Tenant Middleware
 * Auto-injects tenant_id into all Prisma queries for multi-tenant isolation.
 *
 * Usage in a NestJS service module:
 *
 *   import { createTenantExtension } from '@sahool/nestjs-auth';
 *
 *   @Injectable()
 *   export class PrismaService extends PrismaClient implements OnModuleInit {
 *     async onModuleInit() {
 *       await this.$connect();
 *     }
 *
 *     withTenant(tenantId: string) {
 *       return this.$extends(createTenantExtension(tenantId));
 *     }
 *   }
 *
 *   // In controller/service:
 *   const db = this.prisma.withTenant(tenantId);
 *   const fields = await db.field.findMany(); // auto-filtered by tenant
 */

/**
 * Models that have tenant_id field and need automatic filtering.
 * Add new models here as they are onboarded to multi-tenancy.
 */
const TENANT_MODELS = new Set([
  "field",
  "farm",
  "task",
  "ndviReading",
  "fieldBoundaryHistory",
  "syncStatus",
  "product",
  "order",
  "orderItem",
  "wallet",
  "transaction",
  "loan",
  "creditEvent",
  "escrow",
  "scheduledPayment",
  "walletAuditLog",
  "sellerProfile",
  "buyerProfile",
  "productReview",
  "reviewResponse",
  "message",
  "channel",
  "channelMember",
  "device",
  "deviceReading",
  "assessment",
  "hazard",
  "researchTrial",
  "experiment",
  "dataPoint",
  "cropModel",
  "growthStage",
  "yieldPrediction",
  "laiReading",
]);

/**
 * Create a Prisma Client Extension that auto-injects tenantId
 * into all queries for tenant-aware models.
 *
 * @param tenantId - The tenant ID to scope queries to
 * @returns Prisma Client Extension configuration
 */
export function createTenantExtension(tenantId: string) {
  return {
    name: "tenant-isolation",
    query: {
      $allModels: {
        async findMany({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
        async findFirst({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
        async findUnique({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            // findUnique doesn't support arbitrary where, so wrap in findFirst
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
        async create({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.data = { ...args.data, tenantId };
          }
          return query(args);
        },
        async createMany({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            if (Array.isArray(args.data)) {
              args.data = args.data.map((d: any) => ({ ...d, tenantId }));
            } else {
              args.data = { ...args.data, tenantId };
            }
          }
          return query(args);
        },
        async update({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
        async updateMany({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
        async delete({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
        async deleteMany({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
        async count({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
        async aggregate({ args, query, model }: any) {
          if (TENANT_MODELS.has(lowerFirst(model))) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        },
      },
    },
  };
}

/**
 * Convert PascalCase model name to camelCase for matching.
 */
function lowerFirst(str: string): string {
  return str.charAt(0).toLowerCase() + str.slice(1);
}
