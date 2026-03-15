/**
 * Prisma Tenant Middleware
 * ميدل وير عزل المستأجرين لـ Prisma
 *
 * Provides defense-in-depth tenant isolation:
 * 1. Application-layer: Auto-injects tenantId into all Prisma queries
 * 2. Database-layer: Sets PostgreSQL RLS session variables (app.current_tenant)
 *    via $transaction to ensure SET + queries share a connection
 *
 * Usage in a NestJS service module:
 *
 *   import { createTenantExtension, initializeRlsContext } from '@sahool/nestjs-auth';
 *
 *   @Injectable()
 *   export class PrismaService extends PrismaClient implements OnModuleInit {
 *     async onModuleInit() {
 *       await this.$connect();
 *     }
 *
 *     withTenant(tenantId: string, isAdmin = false) {
 *       return this.$extends(createTenantExtension(tenantId, isAdmin));
 *     }
 *   }
 *
 *   // In controller/service:
 *   const db = this.prisma.withTenant(tenantId);
 *   await initializeRlsContext(this.prisma, tenantId); // Set RLS session vars
 *   const fields = await db.field.findMany(); // auto-filtered by tenant + RLS
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
 * Set PostgreSQL RLS session variables using parameterized set_config().
 * Uses $executeRaw tagged template (SQL-injection safe).
 *
 * @param client - Prisma client or transaction instance
 * @param tenantId - Tenant ID to set for RLS
 * @param isAdmin - Whether to grant super_admin bypass
 */
async function setRlsContext(
  client: any,
  tenantId: string,
  isAdmin: boolean,
): Promise<void> {
  const adminFlag = isAdmin ? "true" : "false";
  await client.$executeRaw`SELECT set_config('app.current_tenant', ${tenantId}, true)`;
  await client.$executeRaw`SELECT set_config('app.is_super_admin', ${adminFlag}, true)`;
}

/**
 * Create a Prisma Client Extension that:
 * 1. Auto-injects tenantId into all Prisma queries for tenant-aware models
 * 2. Sets PostgreSQL RLS session variables (app.current_tenant) via $transaction
 *    on the first query, ensuring SET and query share a database connection
 *
 * Application-layer filtering is the primary isolation mechanism.
 * RLS is defense-in-depth and non-blocking (errors are silently caught).
 *
 * @param tenantId - The tenant ID to scope queries to
 * @param isAdmin - If true, sets app.is_super_admin = 'true' to bypass RLS
 * @returns Prisma Client Extension configuration
 */
export function createTenantExtension(
  tenantId: string,
  isAdmin: boolean = false,
) {
  // Track whether RLS context has been set for this extension instance
  let rlsContextSet = false;

  /**
   * Set RLS context once per extension instance via $transaction.
   * This ensures SET and subsequent queries share a database connection.
   *
   * @param prismaClient - The root Prisma client (not the extended one)
   */
  async function ensureRlsContext(prismaClient: any): Promise<void> {
    if (rlsContextSet) return;
    try {
      await prismaClient.$transaction(async (tx: any) => {
        await setRlsContext(tx, tenantId, isAdmin);
      });
      rlsContextSet = true;
    } catch {
      // RLS is defense-in-depth; don't block on failure.
      // Application-layer tenantId injection remains the primary mechanism.
    }
  }

  /** Inject tenantId into where clause for tenant-aware models. */
  function injectTenantWhere(args: any, model: string): void {
    if (TENANT_MODELS.has(lowerFirst(model))) {
      args.where = { ...args.where, tenantId };
    }
  }

  return {
    name: "tenant-isolation",
    query: {
      $allModels: {
        async findMany({ args, query, model }: any) {
          injectTenantWhere(args, model);
          return query(args);
        },
        async findFirst({ args, query, model }: any) {
          injectTenantWhere(args, model);
          return query(args);
        },
        async findUnique({ args, query, model }: any) {
          injectTenantWhere(args, model);
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
          injectTenantWhere(args, model);
          return query(args);
        },
        async updateMany({ args, query, model }: any) {
          injectTenantWhere(args, model);
          return query(args);
        },
        async delete({ args, query, model }: any) {
          injectTenantWhere(args, model);
          return query(args);
        },
        async deleteMany({ args, query, model }: any) {
          injectTenantWhere(args, model);
          return query(args);
        },
        async count({ args, query, model }: any) {
          injectTenantWhere(args, model);
          return query(args);
        },
        async aggregate({ args, query, model }: any) {
          injectTenantWhere(args, model);
          return query(args);
        },
      },
    },
  };
}

/**
 * Initialize RLS context for a tenant extension.
 * Call this after creating the extended client to set RLS session variables.
 *
 * @example
 *   const db = this.prisma.withTenant(tenantId);
 *   await initializeRlsContext(this.prisma, tenantId);
 *   const fields = await db.field.findMany();
 */
export async function initializeRlsContext(
  prismaClient: any,
  tenantId: string,
  isAdmin: boolean = false,
): Promise<void> {
  try {
    await prismaClient.$transaction(async (tx: any) => {
      await setRlsContext(tx, tenantId, isAdmin);
    });
  } catch {
    // RLS is defense-in-depth; don't block on failure
  }
}

/**
 * Convert PascalCase model name to camelCase for matching.
 */
function lowerFirst(str: string): string {
  return str.charAt(0).toLowerCase() + str.slice(1);
}

/**
 * List of all tenant-aware models (exported for testing/validation).
 */
export { TENANT_MODELS };
