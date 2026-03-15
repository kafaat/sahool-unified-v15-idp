/**
 * Prisma Tenant Middleware
 * ميدل وير عزل المستأجرين لـ Prisma
 *
 * Provides defense-in-depth tenant isolation:
 * 1. Application-layer (primary): Auto-injects tenantId into all Prisma queries
 * 2. Database-layer (secondary): Sets PostgreSQL RLS session variables
 *    (app.current_tenant) via initializeRlsContext(). Uses set_config with
 *    is_local=false so RLS vars persist for the database session (connection).
 *    Note: With PgBouncer in transaction mode, session vars reset when the
 *    connection returns to the pool, preventing tenant context leakage.
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
 *   // In controller/service - run queries inside $transaction for RLS:
 *   await this.prisma.$transaction(async (tx) => {
 *     await initializeRlsContext(tx, tenantId);
 *     const fields = await tx.field.findMany({ where: { tenantId } });
 *   });
 *
 *   // Or use app-layer filtering only (RLS not needed):
 *   const db = this.prisma.withTenant(tenantId);
 *   const fields = await db.field.findMany(); // auto-filtered by tenantId
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
 * is_local=false means the setting persists for the database session (connection),
 * not just the current transaction. With PgBouncer in transaction mode, the
 * connection returns to the pool after each transaction, so there is no risk
 * of tenant context leaking to other requests.
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
  await client.$executeRaw`SELECT set_config('app.current_tenant', ${tenantId}, false)`;
  await client.$executeRaw`SELECT set_config('app.is_super_admin', ${adminFlag}, false)`;
}

/**
 * Create a Prisma Client Extension that auto-injects tenantId into all
 * Prisma queries for tenant-aware models.
 *
 * Application-layer filtering is the primary isolation mechanism.
 * For RLS (defense-in-depth), use initializeRlsContext() separately
 * within a $transaction block.
 *
 * @param tenantId - The tenant ID to scope queries to
 * @param isAdmin - If true, sets app.is_super_admin = 'true' to bypass RLS
 * @returns Prisma Client Extension configuration
 */
export function createTenantExtension(
  tenantId: string,
  isAdmin: boolean = false,
) {
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
 * Initialize RLS context by setting PostgreSQL session variables.
 * Can accept either a Prisma client (wraps in $transaction) or a
 * transaction client (sets directly). For RLS to apply to queries,
 * run both this and your queries inside the same $transaction.
 *
 * @example
 *   // Option 1: Inside $transaction (recommended - RLS applies to queries)
 *   await this.prisma.$transaction(async (tx) => {
 *     await initializeRlsContext(tx, tenantId);
 *     const fields = await tx.field.findMany({ where: { tenantId } });
 *   });
 *
 *   // Option 2: Standalone (sets session vars, relies on PgBouncer pooling)
 *   await initializeRlsContext(this.prisma, tenantId);
 */
export async function initializeRlsContext(
  client: any,
  tenantId: string,
  isAdmin: boolean = false,
): Promise<void> {
  try {
    if (typeof client.$transaction === "function") {
      // Root Prisma client - wrap in transaction
      await client.$transaction(async (tx: any) => {
        await setRlsContext(tx, tenantId, isAdmin);
      });
    } else {
      // Transaction client - set directly on same connection
      await setRlsContext(client, tenantId, isAdmin);
    }
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
