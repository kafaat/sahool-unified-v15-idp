/**
 * SAHOOL Idempotency Service Unit Tests
 * اختبارات وحدة خدمة منع التكرار
 *
 * Covers:
 *  - Idempotency replay returns the cached response body + status code.
 *  - Idempotency conflict (different payload, same key) throws 422.
 *  - Currency allow-list validation rejects unknown currency codes.
 *
 * The underlying PostgreSQL store is stubbed via a minimal in-memory
 * fake PrismaService so the tests do not need a live database. The fake
 * intentionally mirrors just enough of the `idempotency_keys` contract
 * to exercise IdempotencyService's control flow.
 */

import { UnprocessableEntityException } from "@nestjs/common";
import { Test, TestingModule } from "@nestjs/testing";
import { validate } from "class-validator";
import { plainToInstance } from "class-transformer";
import { IdempotencyService } from "../fintech/idempotency.service";
import { PrismaService } from "../prisma/prisma.service";
import { WalletTransactionDto } from "../dto/market.dto";

/**
 * Minimal in-memory PrismaService stub.
 *
 * Only the `$queryRaw` and `$executeRaw` tagged-template methods used by
 * IdempotencyService are implemented. The fake inspects the SQL text
 * (passed as a Prisma.Sql template) to decide which operation to perform.
 */
interface FakeRow {
  key: string;
  tenant_id: string;
  user_id: string;
  operation: string;
  request_hash: string;
  response_body: unknown;
  status_code: number | null;
}

function createFakePrisma() {
  const store = new Map<string, FakeRow>();

  // When Prisma's `$queryRaw` / `$executeRaw` are invoked as tagged
  // template literals they receive (TemplateStringsArray, ...values).
  // We join the strings back together so we can pattern-match the SQL
  // to decide which store operation to perform.
  const normaliseCall = (
    args: unknown[],
  ): { sql: string; values: unknown[] } => {
    const first = args[0] as any;
    if (Array.isArray(first)) {
      // Tagged template literal — first arg is TemplateStringsArray.
      return {
        sql: first.join("?"),
        values: args.slice(1),
      };
    }
    // Fallback: Prisma.Sql object (`.strings` / `.values`).
    if (first && Array.isArray(first.strings)) {
      return {
        sql: first.strings.join("?"),
        values: Array.isArray(first.values) ? first.values : [],
      };
    }
    return { sql: String(first ?? ""), values: args.slice(1) };
  };

  const $queryRaw = jest.fn(async (...args: unknown[]): Promise<FakeRow[]> => {
    const { sql, values: vals } = normaliseCall(args);
    if (sql.includes("SELECT key, tenant_id, user_id, operation")) {
      // SELECT ... WHERE key = $1 AND operation = $2
      const [key, operation] = vals as [string, string];
      const mapKey = `${key}::${operation}`;
      const row = store.get(mapKey);
      return row ? [row] : [];
    }
    return [];
  });

  const $executeRaw = jest.fn(async (...args: unknown[]): Promise<number> => {
    const { sql, values: vals } = normaliseCall(args);

    if (sql.includes("INSERT INTO idempotency_keys")) {
      const [key, tenantId, userId, operation, requestHash] = vals as [
        string,
        string,
        string,
        string,
        string,
      ];
      const mapKey = `${key}::${operation}`;
      if (store.has(mapKey)) return 0; // ON CONFLICT DO NOTHING
      store.set(mapKey, {
        key,
        tenant_id: tenantId,
        user_id: userId,
        operation,
        request_hash: requestHash,
        response_body: null,
        status_code: null,
      });
      return 1;
    }

    if (sql.includes("UPDATE idempotency_keys")) {
      // UPDATE ... SET response_body = $1, status_code = $2
      //   WHERE key = $3 AND operation = $4
      const [responseJson, statusCode, key, operation] = vals as [
        string,
        number,
        string,
        string,
      ];
      const mapKey = `${key}::${operation}`;
      const row = store.get(mapKey);
      if (!row) return 0;
      row.response_body = JSON.parse(responseJson);
      row.status_code = statusCode;
      return 1;
    }

    if (sql.includes("DELETE FROM idempotency_keys")) {
      // DELETE ... WHERE key = $1 AND operation = $2 AND response_body IS NULL
      const [key, operation] = vals as [string, string];
      const mapKey = `${key}::${operation}`;
      const row = store.get(mapKey);
      if (row && row.response_body === null) {
        store.delete(mapKey);
        return 1;
      }
      return 0;
    }

    return 0;
  });

  return { $queryRaw, $executeRaw, _store: store };
}

describe("IdempotencyService", () => {
  let service: IdempotencyService;
  let fakePrisma: ReturnType<typeof createFakePrisma>;

  beforeEach(async () => {
    fakePrisma = createFakePrisma();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        IdempotencyService,
        {
          provide: PrismaService,
          useValue: fakePrisma,
        },
      ],
    }).compile();

    service = module.get<IdempotencyService>(IdempotencyService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("passes through when no idempotency key is provided", async () => {
    const work = jest.fn(async () => ({ id: "order-1", total: 100 }));

    const result = await service.executeIdempotent(
      undefined,
      "tenant-1",
      "user-1",
      "market.createOrder",
      { a: 1 },
      work,
    );

    expect(work).toHaveBeenCalledTimes(1);
    expect(result.replayed).toBe(false);
    expect(result.value).toEqual({ id: "order-1", total: 100 });
    expect(fakePrisma.$queryRaw).not.toHaveBeenCalled();
  });

  it("replays the cached response on the second call with matching payload", async () => {
    const payload = { walletId: "w-1", amount: 500 };
    const work = jest
      .fn()
      .mockResolvedValueOnce({ txId: "tx-1", balanceAfter: 500 });

    // First call — executes.
    const first = await service.executeIdempotent(
      "abc-123",
      "11111111-1111-1111-1111-111111111111",
      "22222222-2222-2222-2222-222222222222",
      "wallet.deposit",
      payload,
      work,
    );
    expect(first.replayed).toBe(false);
    expect(work).toHaveBeenCalledTimes(1);

    // Second call with the SAME key and payload — must NOT re-run.
    const second = await service.executeIdempotent(
      "abc-123",
      "11111111-1111-1111-1111-111111111111",
      "22222222-2222-2222-2222-222222222222",
      "wallet.deposit",
      payload,
      work,
    );
    expect(work).toHaveBeenCalledTimes(1); // still once — replay path
    expect(second.replayed).toBe(true);
    expect(second.statusCode).toBe(200);
    expect(second.value).toEqual({ txId: "tx-1", balanceAfter: 500 });
  });

  it("throws UnprocessableEntityException on key collision with different payload", async () => {
    const work = jest.fn().mockResolvedValue({ ok: true });

    await service.executeIdempotent(
      "collision-key",
      "11111111-1111-1111-1111-111111111111",
      "22222222-2222-2222-2222-222222222222",
      "wallet.withdraw",
      { amount: 100 },
      work,
    );

    // Second call with the SAME key but a DIFFERENT payload.
    await expect(
      service.executeIdempotent(
        "collision-key",
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
        "wallet.withdraw",
        { amount: 999 }, // <-- different amount
        work,
      ),
    ).rejects.toThrow(UnprocessableEntityException);
  });

  it("canonicalises object key order so {a,b} and {b,a} hash equal", () => {
    const h1 = service.hashRequest({ a: 1, b: 2 });
    const h2 = service.hashRequest({ b: 2, a: 1 });
    expect(h1).toEqual(h2);
  });

  it("deletes the in-progress row when the work function throws", async () => {
    const failing = jest.fn().mockRejectedValue(new Error("db exploded"));

    await expect(
      service.executeIdempotent(
        "retry-me",
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
        "wallet.deposit",
        { amount: 1 },
        failing,
      ),
    ).rejects.toThrow("db exploded");

    // After a failure the client should be able to retry with the same
    // key — meaning the in-progress row must have been cleaned up.
    const recovering = jest.fn().mockResolvedValue({ ok: true });
    const second = await service.executeIdempotent(
      "retry-me",
      "11111111-1111-1111-1111-111111111111",
      "22222222-2222-2222-2222-222222222222",
      "wallet.deposit",
      { amount: 1 },
      recovering,
    );
    expect(second.replayed).toBe(false);
    expect(recovering).toHaveBeenCalledTimes(1);
  });
});

describe("WalletTransactionDto currency allow-list", () => {
  const runValidation = async (body: Record<string, unknown>) => {
    const instance = plainToInstance(WalletTransactionDto, body);
    return validate(instance);
  };

  it("accepts SAR as a valid currency", async () => {
    const errors = await runValidation({
      amount: 100,
      description: "Test",
      currency: "SAR",
    });
    const currencyErrors = errors.filter((e) => e.property === "currency");
    expect(currencyErrors).toHaveLength(0);
  });

  it("accepts YER as a valid currency", async () => {
    const errors = await runValidation({ amount: 100, currency: "YER" });
    const currencyErrors = errors.filter((e) => e.property === "currency");
    expect(currencyErrors).toHaveLength(0);
  });

  it("rejects JPY as an unknown currency", async () => {
    const errors = await runValidation({ amount: 100, currency: "JPY" });
    const currencyErrors = errors.filter((e) => e.property === "currency");
    expect(currencyErrors.length).toBeGreaterThan(0);
    // class-validator reports the `isIn` constraint when @IsIn fires.
    expect(
      currencyErrors.some((e) =>
        Object.keys(e.constraints ?? {}).some((k) => k === "isIn"),
      ),
    ).toBe(true);
  });

  it("allows omitting currency (optional field)", async () => {
    const errors = await runValidation({ amount: 100 });
    const currencyErrors = errors.filter((e) => e.property === "currency");
    expect(currencyErrors).toHaveLength(0);
  });
});
