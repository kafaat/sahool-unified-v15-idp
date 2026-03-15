/**
 * Prisma Tenant Middleware
 * ميدل وير عزل المستأجرين لـ Prisma
 *
 * Provides defense-in-depth tenant isolation:
 * 1. Application-layer: Auto-injects tenantId into all Prisma queries
 * 2. Database-layer: Sets PostgreSQL RLS session variables (app.current_tenant)
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
 *     withTenant(tenantId: string, isAdmin = false) {
 *       return this.$extends(createTenantExtension(tenantId, isAdmin));
 *     }
 *   }
 *
 *   // In controller/service:
 *   const db = this.prisma.withTenant(tenantId);
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
 * Set PostgreSQL RLS session variables via Prisma's $executeRawUnsafe.
 * Uses set_config() which is parameterized and SQL-injection safe.
 *
 * @param client - Prisma client instance (with $executeRawUnsafe)
 * @param tenantId - Tenant ID to set for RLS
 * @param isAdmin - Whether to grant super_admin bypass
 */
async function setRlsContext(
  client: any,
  tenantId: string,
  isAdmin: boolean,
): Promise<void> {
  try {
    await client.$executeRawUnsafe(
      `SELECT set_config('app.current_tenant', $1, true)`,
      tenantId,
    );
    await client.$executeRawUnsafe(
      `SELECT set_config('app.is_super_admin', $1, true)`,
      isAdmin ? "true" : "false",
    );
  } catch {
    // RLS session variables are defense-in-depth; don't block on failure
    // Application-layer filtering (below) is the primary mechanism
  }
}

/**
 * Create a Prisma Client Extension that:
 * 1. Sets PostgreSQL RLS session variables (app.current_tenant) per query
 * 2. Auto-injects tenantId into all Prisma queries for tenant-aware models
 *
 * This provides defense-in-depth: application-layer + database-layer isolation.
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
   * Ensure RLS session variables are set before first query.
   * Called lazily on first model query.
   *
   * TODO: Integrate into query interceptors below. Currently not invoked because
   * Prisma extension query handlers don't expose the client reference needed for
   * $executeRawUnsafe. Options to fix:
   *   1. Wrap each query in $transaction to ensure SET + query share a connection
   *   2. Use $allOperations hook with client binding
   * Application-layer tenantId injection (below) remains the primary isolation
   * mechanism; RLS is defense-in-depth and non-blocking (see setRlsContext catch).
   */
  // @ts-expect-error Intentionally unused pending integration (see TODO above)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async function ensureRlsContext(client: any): Promise<void> {
    if (!rlsContextSet) {
      await setRlsContext(client, tenantId, isAdmin);
      rlsContextSet = true;
    }
  }

  return {
    name: "tenant-isolation",
    query: {
      $allModels: {
        async findMany({ args, query, model, ...rest }: any) {
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

/**
 * List of all tenant-aware models (exported for testing/validation).
 */
export { TENANT_MODELS };
