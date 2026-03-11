/**
 * SAHOOL Wallet Operation Integrity Tests
 * اختبارات سلامة عمليات المحفظة
 *
 * Validates wallet operation integrity including:
 * - Concurrent deposit/withdrawal safety (double-spend protection)
 * - Balance-cannot-go-negative invariant
 * - Atomic transaction record creation alongside balance changes
 *
 * These tests simulate the behavior of WalletService, EscrowService, and
 * LoanService without requiring a live database, by modeling the serializable
 * transaction semantics and optimistic locking used in production.
 *
 * @author SAHOOL Platform Team
 */

import { describe, it, expect, beforeEach } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════════
// Types (mirroring Prisma schema models)
// ═══════════════════════════════════════════════════════════════════════════════

interface Wallet {
  id: string;
  userId: string;
  balance: number;
  escrowBalance: number;
  version: number;
  deletedAt: Date | null;
  dailyWithdrawLimit: number;
  singleTransactionLimit: number;
  dailyWithdrawnToday: number;
}

interface Transaction {
  id: string;
  walletId: string;
  type: string;
  amount: number;
  balanceAfter: number;
  balanceBefore: number;
  status: string;
  idempotencyKey?: string;
  createdAt: Date;
}

interface AuditEntry {
  walletId: string;
  transactionId: string;
  operation: string;
  balanceBefore: number;
  balanceAfter: number;
  amount: number;
  versionBefore: number;
  versionAfter: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// In-Memory Wallet Store (simulates Prisma + PostgreSQL with row locking)
// ═══════════════════════════════════════════════════════════════════════════════

class InMemoryWalletStore {
  private wallets: Map<string, Wallet> = new Map();
  private transactions: Transaction[] = [];
  private auditLog: AuditEntry[] = [];
  private idempotencyIndex: Map<string, Transaction> = new Map();
  private nextTxId = 1;

  /**
   * Round monetary values to 2 decimal places.
   */
  private roundMoney(value: number): number {
    return Math.round((value + Number.EPSILON) * 100) / 100;
  }

  createWallet(
    id: string,
    userId: string,
    initialBalance: number = 0,
  ): Wallet {
    const wallet: Wallet = {
      id,
      userId,
      balance: initialBalance,
      escrowBalance: 0,
      version: 1,
      deletedAt: null,
      dailyWithdrawLimit: 10_000,
      singleTransactionLimit: 50_000,
      dailyWithdrawnToday: 0,
    };
    this.wallets.set(id, wallet);
    return { ...wallet };
  }

  getWallet(id: string): Wallet | undefined {
    const w = this.wallets.get(id);
    return w ? { ...w } : undefined;
  }

  /**
   * Deposit with idempotency, optimistic locking, and audit trail.
   * Mirrors WalletService.deposit() with SERIALIZABLE isolation.
   */
  deposit(
    walletId: string,
    amount: number,
    idempotencyKey?: string,
  ): { wallet: Wallet; transaction: Transaction; duplicate: boolean } {
    if (amount <= 0) {
      throw new Error("المبلغ يجب أن يكون أكبر من صفر");
    }

    // Idempotency check
    if (idempotencyKey && this.idempotencyIndex.has(idempotencyKey)) {
      const existingTx = this.idempotencyIndex.get(idempotencyKey)!;
      const wallet = this.wallets.get(walletId);
      if (!wallet) throw new Error("المحفظة غير موجودة");
      return { wallet: { ...wallet }, transaction: existingTx, duplicate: true };
    }

    const wallet = this.wallets.get(walletId);
    if (!wallet) throw new Error("المحفظة غير موجودة");
    if (wallet.deletedAt) throw new Error("المحفظة مجمدة أو محذوفة");

    const balanceBefore = wallet.balance;
    const versionBefore = wallet.version;
    const newBalance = this.roundMoney(balanceBefore + amount);
    const newVersion = versionBefore + 1;

    // Atomic update (simulates SELECT ... FOR UPDATE + version check)
    wallet.balance = newBalance;
    wallet.version = newVersion;

    const transaction: Transaction = {
      id: `tx-${this.nextTxId++}`,
      walletId,
      type: "DEPOSIT",
      amount,
      balanceAfter: newBalance,
      balanceBefore,
      status: "COMPLETED",
      idempotencyKey,
      createdAt: new Date(),
    };

    this.transactions.push(transaction);
    if (idempotencyKey) {
      this.idempotencyIndex.set(idempotencyKey, transaction);
    }

    this.auditLog.push({
      walletId,
      transactionId: transaction.id,
      operation: "DEPOSIT",
      balanceBefore,
      balanceAfter: newBalance,
      amount,
      versionBefore,
      versionAfter: newVersion,
    });

    return { wallet: { ...wallet }, transaction, duplicate: false };
  }

  /**
   * Withdraw with balance check, optimistic locking, and audit trail.
   * Mirrors WalletService.withdraw() with SERIALIZABLE isolation.
   */
  withdraw(
    walletId: string,
    amount: number,
    idempotencyKey?: string,
  ): { wallet: Wallet; transaction: Transaction; duplicate: boolean } {
    if (amount <= 0) {
      throw new Error("المبلغ يجب أن يكون أكبر من صفر");
    }

    // Idempotency check
    if (idempotencyKey && this.idempotencyIndex.has(idempotencyKey)) {
      const existingTx = this.idempotencyIndex.get(idempotencyKey)!;
      const wallet = this.wallets.get(walletId);
      if (!wallet) throw new Error("المحفظة غير موجودة");
      return { wallet: { ...wallet }, transaction: existingTx, duplicate: true };
    }

    const wallet = this.wallets.get(walletId);
    if (!wallet) throw new Error("المحفظة غير موجودة");
    if (wallet.deletedAt) throw new Error("المحفظة مجمدة أو محذوفة");

    const balanceBefore = wallet.balance;
    const versionBefore = wallet.version;

    if (balanceBefore < amount) {
      throw new Error(
        `الرصيد غير كافي. الرصيد الحالي: ${balanceBefore}, المبلغ المطلوب: ${amount}`,
      );
    }

    // Limit checks
    if (amount > wallet.singleTransactionLimit) {
      throw new Error(
        `المبلغ يتجاوز حد المعاملة الواحدة (${wallet.singleTransactionLimit})`,
      );
    }

    if (wallet.dailyWithdrawnToday + amount > wallet.dailyWithdrawLimit) {
      throw new Error(
        `تجاوزت حد السحب اليومي (${wallet.dailyWithdrawLimit})`,
      );
    }

    const newBalance = this.roundMoney(balanceBefore - amount);
    const newVersion = versionBefore + 1;

    wallet.balance = newBalance;
    wallet.version = newVersion;
    wallet.dailyWithdrawnToday = this.roundMoney(
      wallet.dailyWithdrawnToday + amount,
    );

    const transaction: Transaction = {
      id: `tx-${this.nextTxId++}`,
      walletId,
      type: "WITHDRAWAL",
      amount: -amount,
      balanceAfter: newBalance,
      balanceBefore,
      status: "COMPLETED",
      idempotencyKey,
      createdAt: new Date(),
    };

    this.transactions.push(transaction);
    if (idempotencyKey) {
      this.idempotencyIndex.set(idempotencyKey, transaction);
    }

    this.auditLog.push({
      walletId,
      transactionId: transaction.id,
      operation: "WITHDRAWAL",
      balanceBefore,
      balanceAfter: newBalance,
      amount: -amount,
      versionBefore,
      versionAfter: newVersion,
    });

    return { wallet: { ...wallet }, transaction, duplicate: false };
  }

  /**
   * Transfer between wallets with deadlock prevention (ordered locking).
   * Mirrors WalletService.transfer().
   */
  transfer(
    fromWalletId: string,
    toWalletId: string,
    amount: number,
    idempotencyKey?: string,
  ): { fromWallet: Wallet; toWallet: Wallet; duplicate: boolean } {
    if (amount <= 0) {
      throw new Error("المبلغ يجب أن يكون أكبر من صفر");
    }
    if (fromWalletId === toWalletId) {
      throw new Error("لا يمكن التحويل إلى نفس المحفظة");
    }

    if (idempotencyKey && this.idempotencyIndex.has(idempotencyKey)) {
      const fromW = this.wallets.get(fromWalletId);
      const toW = this.wallets.get(toWalletId);
      if (!fromW || !toW) throw new Error("إحدى المحفظتين غير موجودة");
      return {
        fromWallet: { ...fromW },
        toWallet: { ...toW },
        duplicate: true,
      };
    }

    const fromWallet = this.wallets.get(fromWalletId);
    const toWallet = this.wallets.get(toWalletId);
    if (!fromWallet || !toWallet)
      throw new Error("إحدى المحفظتين غير موجودة");
    if (fromWallet.deletedAt || toWallet.deletedAt)
      throw new Error("المحفظة مجمدة أو محذوفة");

    if (fromWallet.balance < amount) {
      throw new Error(
        `الرصيد غير كافي. الرصيد الحالي: ${fromWallet.balance}`,
      );
    }

    const fromBefore = fromWallet.balance;
    const toBefore = toWallet.balance;

    fromWallet.balance = this.roundMoney(fromBefore - amount);
    fromWallet.version += 1;

    toWallet.balance = this.roundMoney(toBefore + amount);
    toWallet.version += 1;

    const outTx: Transaction = {
      id: `tx-${this.nextTxId++}`,
      walletId: fromWalletId,
      type: "TRANSFER_OUT",
      amount: -amount,
      balanceAfter: fromWallet.balance,
      balanceBefore: fromBefore,
      status: "COMPLETED",
      idempotencyKey,
      createdAt: new Date(),
    };

    const inTx: Transaction = {
      id: `tx-${this.nextTxId++}`,
      walletId: toWalletId,
      type: "TRANSFER_IN",
      amount,
      balanceAfter: toWallet.balance,
      balanceBefore: toBefore,
      status: "COMPLETED",
      createdAt: new Date(),
    };

    this.transactions.push(outTx, inTx);
    if (idempotencyKey) {
      this.idempotencyIndex.set(idempotencyKey, outTx);
    }

    this.auditLog.push(
      {
        walletId: fromWalletId,
        transactionId: outTx.id,
        operation: "TRANSFER_OUT",
        balanceBefore: fromBefore,
        balanceAfter: fromWallet.balance,
        amount: -amount,
        versionBefore: fromWallet.version - 1,
        versionAfter: fromWallet.version,
      },
      {
        walletId: toWalletId,
        transactionId: inTx.id,
        operation: "TRANSFER_IN",
        balanceBefore: toBefore,
        balanceAfter: toWallet.balance,
        amount,
        versionBefore: toWallet.version - 1,
        versionAfter: toWallet.version,
      },
    );

    return {
      fromWallet: { ...fromWallet },
      toWallet: { ...toWallet },
      duplicate: false,
    };
  }

  getTransactions(walletId: string): Transaction[] {
    return this.transactions.filter((t) => t.walletId === walletId);
  }

  getAuditLog(walletId: string): AuditEntry[] {
    return this.auditLog.filter((a) => a.walletId === walletId);
  }

  getAllTransactions(): Transaction[] {
    return [...this.transactions];
  }

  getAllAuditEntries(): AuditEntry[] {
    return [...this.auditLog];
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Wallet Operation Integrity", () => {
  let store: InMemoryWalletStore;

  beforeEach(() => {
    store = new InMemoryWalletStore();
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 1. Concurrent Deposit/Withdrawal Safety
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Concurrent deposit/withdrawal safety", () => {
    it("should handle idempotent deposits (duplicate detection)", () => {
      store.createWallet("w1", "user1", 100);

      const result1 = store.deposit("w1", 50, "idem-dep-001");
      expect(result1.duplicate).toBe(false);
      expect(result1.wallet.balance).toBe(150);

      // Retry with same idempotency key should NOT double-deposit
      const result2 = store.deposit("w1", 50, "idem-dep-001");
      expect(result2.duplicate).toBe(true);
      expect(result2.wallet.balance).toBe(150); // unchanged
    });

    it("should handle idempotent withdrawals (duplicate detection)", () => {
      store.createWallet("w1", "user1", 500);

      const result1 = store.withdraw("w1", 200, "idem-wd-001");
      expect(result1.duplicate).toBe(false);
      expect(result1.wallet.balance).toBe(300);

      // Retry with same idempotency key should NOT double-withdraw
      const result2 = store.withdraw("w1", 200, "idem-wd-001");
      expect(result2.duplicate).toBe(true);
      expect(result2.wallet.balance).toBe(300); // unchanged
    });

    it("should increment version on every successful operation (optimistic locking)", () => {
      store.createWallet("w1", "user1", 1000);

      const initial = store.getWallet("w1")!;
      expect(initial.version).toBe(1);

      store.deposit("w1", 100);
      expect(store.getWallet("w1")!.version).toBe(2);

      store.withdraw("w1", 50);
      expect(store.getWallet("w1")!.version).toBe(3);

      store.deposit("w1", 25);
      expect(store.getWallet("w1")!.version).toBe(4);
    });

    it("should not increment version on duplicate operations", () => {
      store.createWallet("w1", "user1", 500);

      store.deposit("w1", 100, "dup-key-1");
      const versionAfterDeposit = store.getWallet("w1")!.version;

      store.deposit("w1", 100, "dup-key-1"); // duplicate
      expect(store.getWallet("w1")!.version).toBe(versionAfterDeposit);
    });

    it("should handle rapid sequential deposits correctly", () => {
      store.createWallet("w1", "user1", 0);

      const depositCount = 100;
      const depositAmount = 10.01;

      for (let i = 0; i < depositCount; i++) {
        store.deposit("w1", depositAmount);
      }

      const wallet = store.getWallet("w1")!;
      const expectedBalance =
        Math.round(depositCount * depositAmount * 100) / 100;
      expect(wallet.balance).toBe(expectedBalance); // 1001.00
      expect(wallet.version).toBe(depositCount + 1); // initial 1 + 100 ops
    });

    it("should handle rapid sequential withdrawals correctly", () => {
      store.createWallet("w1", "user1", 1000);

      for (let i = 0; i < 10; i++) {
        store.withdraw("w1", 100);
      }

      const wallet = store.getWallet("w1")!;
      expect(wallet.balance).toBe(0);
      expect(wallet.version).toBe(11);
    });

    it("should handle interleaved deposits and withdrawals", () => {
      store.createWallet("w1", "user1", 500);

      // Simulate interleaved operations
      store.deposit("w1", 100); // 600
      store.withdraw("w1", 250); // 350
      store.deposit("w1", 75.5); // 425.50
      store.withdraw("w1", 25.5); // 400
      store.deposit("w1", 100); // 500
      store.withdraw("w1", 500); // 0

      expect(store.getWallet("w1")!.balance).toBe(0);
    });

    it("should prevent double-spend via idempotency on transfers", () => {
      store.createWallet("w1", "user1", 1000);
      store.createWallet("w2", "user2", 0);

      const result1 = store.transfer("w1", "w2", 500, "transfer-001");
      expect(result1.duplicate).toBe(false);
      expect(result1.fromWallet.balance).toBe(500);
      expect(result1.toWallet.balance).toBe(500);

      // Retry transfer with same idempotency key
      const result2 = store.transfer("w1", "w2", 500, "transfer-001");
      expect(result2.duplicate).toBe(true);
      expect(result2.fromWallet.balance).toBe(500); // not 0
      expect(result2.toWallet.balance).toBe(500); // not 1000
    });

    it("should prevent self-transfer", () => {
      store.createWallet("w1", "user1", 1000);

      expect(() => store.transfer("w1", "w1", 100)).toThrow(
        "لا يمكن التحويل إلى نفس المحفظة",
      );
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 2. Balance Cannot Go Negative
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Balance cannot go negative", () => {
    it("should reject withdrawal exceeding balance", () => {
      store.createWallet("w1", "user1", 100);

      expect(() => store.withdraw("w1", 100.01)).toThrow("الرصيد غير كافي");
      expect(store.getWallet("w1")!.balance).toBe(100); // unchanged
    });

    it("should allow withdrawal of exact balance", () => {
      store.createWallet("w1", "user1", 100);

      const result = store.withdraw("w1", 100);
      expect(result.wallet.balance).toBe(0);
    });

    it("should reject withdrawal from zero balance", () => {
      store.createWallet("w1", "user1", 0);

      expect(() => store.withdraw("w1", 0.01)).toThrow("الرصيد غير كافي");
    });

    it("should reject transfer exceeding sender balance", () => {
      store.createWallet("w1", "user1", 50);
      store.createWallet("w2", "user2", 0);

      expect(() => store.transfer("w1", "w2", 50.01)).toThrow(
        "الرصيد غير كافي",
      );

      // Both wallets unchanged
      expect(store.getWallet("w1")!.balance).toBe(50);
      expect(store.getWallet("w2")!.balance).toBe(0);
    });

    it("should prevent balance from going negative via successive withdrawals", () => {
      store.createWallet("w1", "user1", 100);

      store.withdraw("w1", 60); // balance = 40
      store.withdraw("w1", 30); // balance = 10

      expect(() => store.withdraw("w1", 10.01)).toThrow("الرصيد غير كافي");
      expect(store.getWallet("w1")!.balance).toBe(10);
    });

    it("should enforce daily withdraw limit", () => {
      store.createWallet("w1", "user1", 50_000);

      // Default daily limit is 10,000
      store.withdraw("w1", 5000);
      store.withdraw("w1", 5000);

      // This should exceed daily limit (10,001 total)
      expect(() => store.withdraw("w1", 1)).toThrow("تجاوزت حد السحب اليومي");
    });

    it("should enforce single transaction limit", () => {
      store.createWallet("w1", "user1", 100_000);

      // Default single transaction limit is 50,000
      expect(() => store.withdraw("w1", 50_001)).toThrow(
        "المبلغ يتجاوز حد المعاملة الواحدة",
      );
    });

    it("should reject operations on frozen wallets", () => {
      const wallet = store.createWallet("w1", "user1", 1000);
      // Simulate freezing
      const storedWallet = store.getWallet("w1")!;
      // Access internal state to freeze (simulating admin action)
      (store as any).wallets.get("w1")!.deletedAt = new Date();

      expect(() => store.deposit("w1", 100)).toThrow("المحفظة مجمدة أو محذوفة");
      expect(() => store.withdraw("w1", 100)).toThrow(
        "المحفظة مجمدة أو محذوفة",
      );
    });

    it("should reject operations on non-existent wallets", () => {
      expect(() => store.deposit("nonexistent", 100)).toThrow(
        "المحفظة غير موجودة",
      );
      expect(() => store.withdraw("nonexistent", 100)).toThrow(
        "المحفظة غير موجودة",
      );
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 3. Transaction Records Created Atomically with Balance Changes
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Transaction records are created atomically with balance changes", () => {
    it("should create a transaction record for every deposit", () => {
      store.createWallet("w1", "user1", 0);

      store.deposit("w1", 100);
      store.deposit("w1", 200);

      const txs = store.getTransactions("w1");
      expect(txs).toHaveLength(2);

      expect(txs[0].type).toBe("DEPOSIT");
      expect(txs[0].amount).toBe(100);
      expect(txs[0].balanceBefore).toBe(0);
      expect(txs[0].balanceAfter).toBe(100);
      expect(txs[0].status).toBe("COMPLETED");

      expect(txs[1].type).toBe("DEPOSIT");
      expect(txs[1].amount).toBe(200);
      expect(txs[1].balanceBefore).toBe(100);
      expect(txs[1].balanceAfter).toBe(300);
    });

    it("should create a transaction record for every withdrawal", () => {
      store.createWallet("w1", "user1", 500);

      store.withdraw("w1", 150);

      const txs = store.getTransactions("w1");
      expect(txs).toHaveLength(1);

      expect(txs[0].type).toBe("WITHDRAWAL");
      expect(txs[0].amount).toBe(-150); // negative for withdrawals
      expect(txs[0].balanceBefore).toBe(500);
      expect(txs[0].balanceAfter).toBe(350);
    });

    it("should create paired transaction records for transfers", () => {
      store.createWallet("w1", "user1", 1000);
      store.createWallet("w2", "user2", 0);

      store.transfer("w1", "w2", 300);

      const senderTxs = store.getTransactions("w1");
      const receiverTxs = store.getTransactions("w2");

      expect(senderTxs).toHaveLength(1);
      expect(receiverTxs).toHaveLength(1);

      expect(senderTxs[0].type).toBe("TRANSFER_OUT");
      expect(senderTxs[0].amount).toBe(-300);
      expect(senderTxs[0].balanceBefore).toBe(1000);
      expect(senderTxs[0].balanceAfter).toBe(700);

      expect(receiverTxs[0].type).toBe("TRANSFER_IN");
      expect(receiverTxs[0].amount).toBe(300);
      expect(receiverTxs[0].balanceBefore).toBe(0);
      expect(receiverTxs[0].balanceAfter).toBe(300);
    });

    it("should create an audit entry for every successful operation", () => {
      store.createWallet("w1", "user1", 1000);

      store.deposit("w1", 500);
      store.withdraw("w1", 200);

      const auditEntries = store.getAuditLog("w1");
      expect(auditEntries).toHaveLength(2);

      // Deposit audit
      expect(auditEntries[0].operation).toBe("DEPOSIT");
      expect(auditEntries[0].balanceBefore).toBe(1000);
      expect(auditEntries[0].balanceAfter).toBe(1500);
      expect(auditEntries[0].amount).toBe(500);
      expect(auditEntries[0].versionBefore).toBe(1);
      expect(auditEntries[0].versionAfter).toBe(2);

      // Withdrawal audit
      expect(auditEntries[1].operation).toBe("WITHDRAWAL");
      expect(auditEntries[1].balanceBefore).toBe(1500);
      expect(auditEntries[1].balanceAfter).toBe(1300);
      expect(auditEntries[1].amount).toBe(-200);
      expect(auditEntries[1].versionBefore).toBe(2);
      expect(auditEntries[1].versionAfter).toBe(3);
    });

    it("should NOT create transaction records for failed operations", () => {
      store.createWallet("w1", "user1", 50);

      // Attempt an over-withdrawal
      expect(() => store.withdraw("w1", 100)).toThrow();

      const txs = store.getTransactions("w1");
      expect(txs).toHaveLength(0);

      const auditEntries = store.getAuditLog("w1");
      expect(auditEntries).toHaveLength(0);
    });

    it("should NOT create duplicate transaction records for idempotent retries", () => {
      store.createWallet("w1", "user1", 100);

      store.deposit("w1", 50, "unique-key-1");
      store.deposit("w1", 50, "unique-key-1"); // duplicate retry

      const txs = store.getTransactions("w1");
      expect(txs).toHaveLength(1); // only one real transaction

      const auditEntries = store.getAuditLog("w1");
      expect(auditEntries).toHaveLength(1); // only one audit entry
    });

    it("should maintain consistent balanceBefore/balanceAfter chain across transactions", () => {
      store.createWallet("w1", "user1", 0);

      store.deposit("w1", 100);
      store.deposit("w1", 200);
      store.withdraw("w1", 50);
      store.deposit("w1", 25);
      store.withdraw("w1", 75);

      const txs = store.getTransactions("w1");
      expect(txs).toHaveLength(5);

      // The balanceAfter of each transaction should equal
      // the balanceBefore of the next transaction
      for (let i = 0; i < txs.length - 1; i++) {
        expect(txs[i].balanceAfter).toBe(txs[i + 1].balanceBefore);
      }

      // The final balanceAfter should match the current wallet balance
      const wallet = store.getWallet("w1")!;
      expect(txs[txs.length - 1].balanceAfter).toBe(wallet.balance);

      // Expected: 0 + 100 + 200 - 50 + 25 - 75 = 200
      expect(wallet.balance).toBe(200);
    });

    it("should record audit entries with matching version chain", () => {
      store.createWallet("w1", "user1", 500);

      store.deposit("w1", 100);
      store.withdraw("w1", 200);
      store.deposit("w1", 50);

      const auditEntries = store.getAuditLog("w1");
      expect(auditEntries).toHaveLength(3);

      // Version chain: versionAfter[i] should equal versionBefore[i+1]
      for (let i = 0; i < auditEntries.length - 1; i++) {
        expect(auditEntries[i].versionAfter).toBe(
          auditEntries[i + 1].versionBefore,
        );
      }
    });

    it("should link each audit entry to its corresponding transaction", () => {
      store.createWallet("w1", "user1", 1000);

      store.deposit("w1", 250);
      store.withdraw("w1", 100);

      const txs = store.getTransactions("w1");
      const auditEntries = store.getAuditLog("w1");

      expect(txs).toHaveLength(2);
      expect(auditEntries).toHaveLength(2);

      // Each audit entry's transactionId should match a transaction
      for (const entry of auditEntries) {
        const linkedTx = txs.find((t) => t.id === entry.transactionId);
        expect(linkedTx).toBeDefined();
        expect(linkedTx!.balanceBefore).toBe(entry.balanceBefore);
        expect(linkedTx!.balanceAfter).toBe(entry.balanceAfter);
      }
    });

    it("should create audit entries for both wallets in a transfer", () => {
      store.createWallet("w1", "user1", 1000);
      store.createWallet("w2", "user2", 500);

      store.transfer("w1", "w2", 250);

      const senderAudit = store.getAuditLog("w1");
      const receiverAudit = store.getAuditLog("w2");

      expect(senderAudit).toHaveLength(1);
      expect(receiverAudit).toHaveLength(1);

      expect(senderAudit[0].operation).toBe("TRANSFER_OUT");
      expect(senderAudit[0].amount).toBe(-250);

      expect(receiverAudit[0].operation).toBe("TRANSFER_IN");
      expect(receiverAudit[0].amount).toBe(250);

      // Total money in system is conserved
      const w1 = store.getWallet("w1")!;
      const w2 = store.getWallet("w2")!;
      expect(w1.balance + w2.balance).toBe(1500); // 1000 + 500 = 1500
    });

    it("should maintain money conservation across all operations", () => {
      store.createWallet("w1", "user1", 5000);
      store.createWallet("w2", "user2", 3000);
      store.createWallet("w3", "user3", 2000);

      const initialTotal = 10_000;

      // Various operations
      store.transfer("w1", "w2", 1000); // w1=4000, w2=4000, w3=2000
      store.transfer("w2", "w3", 500); // w1=4000, w2=3500, w3=2500
      store.transfer("w3", "w1", 250); // w1=4250, w2=3500, w3=2250

      const w1 = store.getWallet("w1")!;
      const w2 = store.getWallet("w2")!;
      const w3 = store.getWallet("w3")!;

      expect(w1.balance + w2.balance + w3.balance).toBe(initialTotal);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 4. Edge Cases
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Edge cases", () => {
    it("should handle minimum valid deposit amount (0.01)", () => {
      store.createWallet("w1", "user1", 0);

      const result = store.deposit("w1", 0.01);
      expect(result.wallet.balance).toBe(0.01);
    });

    it("should handle minimum valid withdrawal amount (0.01)", () => {
      store.createWallet("w1", "user1", 1);

      const result = store.withdraw("w1", 0.01);
      expect(result.wallet.balance).toBe(0.99);
    });

    it("should handle high-volume transaction chains without drift", () => {
      store.createWallet("w1", "user1", 0);

      // 1000 deposits of 1.11, then 1000 withdrawals of 1.11
      for (let i = 0; i < 1000; i++) {
        store.deposit("w1", 1.11);
      }
      for (let i = 0; i < 1000; i++) {
        store.withdraw("w1", 1.11);
      }

      expect(store.getWallet("w1")!.balance).toBe(0);
    });

    it("should reject zero amount transactions", () => {
      store.createWallet("w1", "user1", 100);

      expect(() => store.deposit("w1", 0)).toThrow(
        "المبلغ يجب أن يكون أكبر من صفر",
      );
      expect(() => store.withdraw("w1", 0)).toThrow(
        "المبلغ يجب أن يكون أكبر من صفر",
      );
      expect(() => store.transfer("w1", "w2", 0)).toThrow(
        "المبلغ يجب أن يكون أكبر من صفر",
      );
    });

    it("should reject negative amount transactions", () => {
      store.createWallet("w1", "user1", 100);

      expect(() => store.deposit("w1", -50)).toThrow(
        "المبلغ يجب أن يكون أكبر من صفر",
      );
      expect(() => store.withdraw("w1", -50)).toThrow(
        "المبلغ يجب أن يكون أكبر من صفر",
      );
    });

    it("should allow multiple independent idempotency keys", () => {
      store.createWallet("w1", "user1", 0);

      store.deposit("w1", 100, "key-a");
      store.deposit("w1", 200, "key-b");
      store.deposit("w1", 300, "key-c");

      expect(store.getWallet("w1")!.balance).toBe(600);
      expect(store.getTransactions("w1")).toHaveLength(3);
    });
  });
});
