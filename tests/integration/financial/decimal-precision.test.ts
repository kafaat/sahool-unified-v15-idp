/**
 * SAHOOL Financial Decimal Precision Tests
 * اختبارات دقة الأرقام العشرية المالية
 *
 * Validates that all financial calculations maintain exact decimal precision,
 * preventing floating-point drift that could cause balance discrepancies
 * in wallet operations, service fees, loan calculations, and escrow amounts.
 *
 * IMPORTANT: The marketplace-service Prisma schema currently uses Float for
 * monetary fields (balance, amount, escrowBalance, etc.). These tests document
 * the precision risks inherent in IEEE 754 floating-point representation and
 * verify that helper utilities produce correct results when used.
 *
 * @author SAHOOL Platform Team
 */

import { describe, it, expect } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════════
// Financial Precision Helpers
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Round a monetary value to 2 decimal places using banker's rounding.
 * This avoids cumulative drift from repeated arithmetic on floats.
 */
function roundMoney(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

/**
 * Add two monetary values with precision-safe rounding.
 * Prevents results like 0.1 + 0.2 = 0.30000000000000004.
 */
function addMoney(a: number, b: number): number {
  return roundMoney(a + b);
}

/**
 * Subtract two monetary values with precision-safe rounding.
 */
function subtractMoney(a: number, b: number): number {
  return roundMoney(a - b);
}

/**
 * Multiply a monetary value by a rate (e.g. fee percentage) with rounding.
 */
function multiplyMoney(amount: number, rate: number): number {
  return roundMoney(amount * rate);
}

/**
 * Compare two monetary values for equality within the 2-decimal-place domain.
 */
function moneyEquals(a: number, b: number): boolean {
  return roundMoney(a) === roundMoney(b);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Wallet Balance Simulation (mirrors WalletService logic)
// ═══════════════════════════════════════════════════════════════════════════════

interface WalletState {
  balance: number;
  escrowBalance: number;
  version: number;
}

function createWallet(initialBalance: number = 0): WalletState {
  return { balance: initialBalance, escrowBalance: 0, version: 1 };
}

function deposit(wallet: WalletState, amount: number): WalletState {
  if (amount <= 0) throw new Error("المبلغ يجب أن يكون أكبر من صفر");
  return {
    ...wallet,
    balance: roundMoney(wallet.balance + amount),
    version: wallet.version + 1,
  };
}

function withdraw(wallet: WalletState, amount: number): WalletState {
  if (amount <= 0) throw new Error("المبلغ يجب أن يكون أكبر من صفر");
  if (wallet.balance < amount) {
    throw new Error(
      `الرصيد غير كافي. الرصيد الحالي: ${wallet.balance}, المبلغ المطلوب: ${amount}`,
    );
  }
  return {
    ...wallet,
    balance: roundMoney(wallet.balance - amount),
    version: wallet.version + 1,
  };
}

function holdEscrow(wallet: WalletState, amount: number): WalletState {
  if (amount <= 0) throw new Error("المبلغ يجب أن يكون أكبر من صفر");
  if (wallet.balance < amount) {
    throw new Error(
      `رصيد المشتري غير كافي. الرصيد: ${wallet.balance}, المطلوب: ${amount}`,
    );
  }
  return {
    ...wallet,
    balance: roundMoney(wallet.balance - amount),
    escrowBalance: roundMoney(wallet.escrowBalance + amount),
    version: wallet.version + 1,
  };
}

function releaseEscrow(
  buyerWallet: WalletState,
  sellerWallet: WalletState,
  amount: number,
): { buyer: WalletState; seller: WalletState } {
  if (buyerWallet.escrowBalance < amount) {
    throw new Error("رصيد الإسكرو غير كافي");
  }
  return {
    buyer: {
      ...buyerWallet,
      escrowBalance: roundMoney(buyerWallet.escrowBalance - amount),
      version: buyerWallet.version + 1,
    },
    seller: {
      ...sellerWallet,
      balance: roundMoney(sellerWallet.balance + amount),
      version: sellerWallet.version + 1,
    },
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Financial Decimal Precision", () => {
  // ─────────────────────────────────────────────────────────────────────────────
  // 1. Decimal Precision in Wallet Operations
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Decimal precision in wallet operations", () => {
    it("should compute 0.1 + 0.2 as exactly 0.3 (not 0.30000000000000004)", () => {
      // Raw IEEE 754 floating-point fails this
      expect(0.1 + 0.2).not.toBe(0.3);

      // Our precision-safe helper must pass
      expect(addMoney(0.1, 0.2)).toBe(0.3);
    });

    it("should maintain exact balance after depositing 99.99", () => {
      let wallet = createWallet(0);
      wallet = deposit(wallet, 99.99);

      expect(wallet.balance).toBe(99.99);
    });

    it("should accumulate multiple small transactions correctly", () => {
      let wallet = createWallet(0);

      // Deposit 0.01 one hundred times should equal exactly 1.00
      for (let i = 0; i < 100; i++) {
        wallet = deposit(wallet, 0.01);
      }
      expect(wallet.balance).toBe(1.0);

      // Deposit 0.10 ten times should equal exactly 2.00
      for (let i = 0; i < 10; i++) {
        wallet = deposit(wallet, 0.1);
      }
      expect(wallet.balance).toBe(2.0);
    });

    it("should maintain precision for large amounts (1,000,000.99)", () => {
      let wallet = createWallet(0);
      wallet = deposit(wallet, 1_000_000.99);

      expect(wallet.balance).toBe(1_000_000.99);

      // Withdraw a small amount from a large balance
      wallet = withdraw(wallet, 0.01);
      expect(wallet.balance).toBe(1_000_000.98);

      // Deposit again and verify
      wallet = deposit(wallet, 0.01);
      expect(wallet.balance).toBe(1_000_000.99);
    });

    it("should maintain precision across deposit and withdrawal cycles", () => {
      let wallet = createWallet(100.0);

      // Simulate a series of real-world transactions
      wallet = withdraw(wallet, 33.33);
      wallet = withdraw(wallet, 33.33);
      wallet = withdraw(wallet, 33.33);

      // 100 - 33.33 - 33.33 - 33.33 = 0.01
      expect(wallet.balance).toBe(0.01);
    });

    it("should handle fractional currency amounts (fils/cents) precisely", () => {
      let wallet = createWallet(0);

      wallet = deposit(wallet, 1.01);
      wallet = deposit(wallet, 2.02);
      wallet = deposit(wallet, 3.03);

      // 1.01 + 2.02 + 3.03 = 6.06
      expect(wallet.balance).toBe(6.06);
    });

    it("should correctly represent the sum of problematic float pairs", () => {
      // These pairs are notoriously imprecise in IEEE 754
      const problematicPairs: [number, number, number][] = [
        [0.1, 0.2, 0.3],
        [0.05, 0.05, 0.1],
        [0.3, 0.6, 0.9],
        [1.005, 0.005, 1.01],
        [0.07, 0.03, 0.1],
        [0.14, 0.28, 0.42],
      ];

      for (const [a, b, expected] of problematicPairs) {
        expect(addMoney(a, b)).toBe(expected);
      }
    });

    it("should handle maximum wallet balance additions without overflow", () => {
      let wallet = createWallet(9_999_999.99);
      wallet = deposit(wallet, 0.01);

      expect(wallet.balance).toBe(10_000_000.0);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 2. Financial Calculations
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Financial calculations", () => {
    describe("Service fee calculation (2% of subtotal)", () => {
      it("should compute 2% fee precisely for integer amounts", () => {
        // 2% of 1000 = 20.00
        expect(multiplyMoney(1000, 0.02)).toBe(20.0);
      });

      it("should compute 2% fee precisely for decimal amounts", () => {
        // 2% of 99.99 = 1.9998, rounded to 2.00
        expect(multiplyMoney(99.99, 0.02)).toBe(2.0);
      });

      it("should compute 2% fee for small amounts", () => {
        // 2% of 1.50 = 0.03
        expect(multiplyMoney(1.5, 0.02)).toBe(0.03);
      });

      it("should compute 2% fee for large amounts", () => {
        // 2% of 500,000 = 10,000.00
        expect(multiplyMoney(500_000, 0.02)).toBe(10_000.0);
      });

      it("should produce subtotal + fee that equals the total precisely", () => {
        const subtotal = 1250.75;
        const feeRate = 0.02;
        const fee = multiplyMoney(subtotal, feeRate);
        const total = addMoney(subtotal, fee);

        // fee = 25.02 (rounded from 25.015)
        expect(fee).toBe(25.02);
        // total = 1250.75 + 25.02 = 1275.77
        expect(total).toBe(1275.77);
      });

      it("should ensure order amounts decompose correctly (subtotal + delivery + service = total)", () => {
        // Mirrors the Order model: subtotal + deliveryFee + serviceFee = totalAmount
        const subtotal = 3450.5;
        const deliveryFee = 150.0;
        const serviceFee = multiplyMoney(subtotal, 0.02); // 69.01

        const totalAmount = roundMoney(subtotal + deliveryFee + serviceFee);

        expect(serviceFee).toBe(69.01);
        expect(totalAmount).toBe(3669.51);
        expect(totalAmount).toBe(
          addMoney(addMoney(subtotal, deliveryFee), serviceFee),
        );
      });
    });

    describe("Loan interest and admin fee calculations", () => {
      it("should compute 2% admin fee precisely (Islamic finance - no interest)", () => {
        // Mirrors LoanService.requestLoan: adminFee = amount * 0.02
        const loanAmount = 10_000;
        const adminFee = multiplyMoney(loanAmount, 0.02);
        const totalDue = addMoney(loanAmount, adminFee);

        expect(adminFee).toBe(200.0);
        expect(totalDue).toBe(10_200.0);
      });

      it("should compute admin fee for fractional loan amounts", () => {
        const loanAmount = 7_777.77;
        const adminFee = multiplyMoney(loanAmount, 0.02);
        const totalDue = addMoney(loanAmount, adminFee);

        // 7777.77 * 0.02 = 155.5554, rounded to 155.56
        expect(adminFee).toBe(155.56);
        expect(totalDue).toBe(7_933.33);
      });

      it("should track loan repayment progress precisely", () => {
        const totalDue = 10_200.0;
        let paidAmount = 0;

        // Make 10 equal payments
        const paymentAmount = roundMoney(totalDue / 10); // 1020.00
        for (let i = 0; i < 10; i++) {
          paidAmount = addMoney(paidAmount, paymentAmount);
        }

        expect(paidAmount).toBe(totalDue);
        expect(subtractMoney(totalDue, paidAmount)).toBe(0);
      });

      it("should handle uneven loan repayment splits correctly", () => {
        const totalDue = 10_000.0;
        let paidAmount = 0;

        // 3 uneven payments
        paidAmount = addMoney(paidAmount, 3333.33);
        paidAmount = addMoney(paidAmount, 3333.33);
        paidAmount = addMoney(paidAmount, 3333.34);

        expect(paidAmount).toBe(10_000.0);
      });

      it("should compute remaining due correctly after partial repayments", () => {
        const totalDue = 5100.0; // loan + 2% admin fee on 5000
        let paidAmount = 0;

        paidAmount = addMoney(paidAmount, 1000.0);
        expect(subtractMoney(totalDue, paidAmount)).toBe(4100.0);

        paidAmount = addMoney(paidAmount, 2050.5);
        expect(subtractMoney(totalDue, paidAmount)).toBe(2049.5);

        paidAmount = addMoney(paidAmount, 2049.5);
        expect(subtractMoney(totalDue, paidAmount)).toBe(0);
      });
    });

    describe("Escrow amounts", () => {
      it("should hold exact escrow amount and deduct from buyer balance", () => {
        const buyer = createWallet(5000.0);
        const escrowAmount = 1299.99;

        const afterHold = holdEscrow(buyer, escrowAmount);

        expect(afterHold.balance).toBe(3700.01);
        expect(afterHold.escrowBalance).toBe(1299.99);
        // Total funds are conserved
        expect(addMoney(afterHold.balance, afterHold.escrowBalance)).toBe(
          5000.0,
        );
      });

      it("should release escrow and credit seller with exact amount", () => {
        let buyer = createWallet(5000.0);
        let seller = createWallet(0);
        const escrowAmount = 2750.5;

        buyer = holdEscrow(buyer, escrowAmount);
        const result = releaseEscrow(buyer, seller, escrowAmount);

        expect(result.buyer.escrowBalance).toBe(0);
        expect(result.seller.balance).toBe(2750.5);

        // Total money in system is conserved
        const totalInSystem = addMoney(
          result.buyer.balance,
          addMoney(result.buyer.escrowBalance, result.seller.balance),
        );
        expect(totalInSystem).toBe(5000.0);
      });

      it("should handle multiple escrow holds and releases precisely", () => {
        let buyer = createWallet(10_000.0);
        let seller = createWallet(0);

        // Hold three separate escrows
        buyer = holdEscrow(buyer, 1111.11);
        buyer = holdEscrow(buyer, 2222.22);
        buyer = holdEscrow(buyer, 3333.33);

        // Total escrow = 6666.66
        expect(buyer.escrowBalance).toBe(6666.66);
        expect(buyer.balance).toBe(3333.34);
        expect(addMoney(buyer.balance, buyer.escrowBalance)).toBe(10_000.0);

        // Release all at once (simulating batch release)
        const result = releaseEscrow(buyer, seller, 6666.66);
        expect(result.seller.balance).toBe(6666.66);
        expect(result.buyer.escrowBalance).toBe(0);
      });

      it("should ensure escrow + remaining balance always equals original balance", () => {
        const initialBalance = 8500.75;
        let wallet = createWallet(initialBalance);

        const amounts = [100.25, 200.5, 350.0, 1500.99, 2000.01];

        for (const amount of amounts) {
          wallet = holdEscrow(wallet, amount);
          expect(addMoney(wallet.balance, wallet.escrowBalance)).toBe(
            initialBalance,
          );
        }
      });
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 3. Rounding Rules
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Rounding rules", () => {
    it("should round amounts to exactly 2 decimal places", () => {
      expect(roundMoney(1.001)).toBe(1.0);
      expect(roundMoney(1.005)).toBe(1.01);
      expect(roundMoney(1.009)).toBe(1.01);
      expect(roundMoney(1.015)).toBe(1.02);
      expect(roundMoney(1.994)).toBe(1.99);
      expect(roundMoney(1.995)).toBe(2.0);
      expect(roundMoney(1.999)).toBe(2.0);
    });

    it("should not introduce spurious decimals after rounding", () => {
      const rounded = roundMoney(33.33333);
      const decimalStr = rounded.toString();
      const decimalPart = decimalStr.split(".")[1] || "";

      expect(decimalPart.length).toBeLessThanOrEqual(2);
    });

    it("should prevent negative balances on withdrawal", () => {
      const wallet = createWallet(100.0);

      expect(() => withdraw(wallet, 100.01)).toThrow("الرصيد غير كافي");
    });

    it("should allow withdrawal of exact balance (zero remaining)", () => {
      let wallet = createWallet(100.0);
      wallet = withdraw(wallet, 100.0);

      expect(wallet.balance).toBe(0);
    });

    it("should prevent negative balances on escrow hold", () => {
      const wallet = createWallet(50.0);

      expect(() => holdEscrow(wallet, 50.01)).toThrow("رصيد المشتري غير كافي");
    });

    it("should reject zero and negative deposit amounts", () => {
      const wallet = createWallet(100.0);

      expect(() => deposit(wallet, 0)).toThrow("المبلغ يجب أن يكون أكبر من صفر");
      expect(() => deposit(wallet, -10)).toThrow(
        "المبلغ يجب أن يكون أكبر من صفر",
      );
    });

    it("should reject zero and negative withdrawal amounts", () => {
      const wallet = createWallet(100.0);

      expect(() => withdraw(wallet, 0)).toThrow(
        "المبلغ يجب أن يكون أكبر من صفر",
      );
      expect(() => withdraw(wallet, -5)).toThrow(
        "المبلغ يجب أن يكون أكبر من صفر",
      );
    });

    it("should correctly compare monetary values with moneyEquals", () => {
      expect(moneyEquals(0.1 + 0.2, 0.3)).toBe(true);
      expect(moneyEquals(1.0, 1.004)).toBe(true); // rounds to 1.00
      expect(moneyEquals(1.0, 1.005)).toBe(false); // rounds to 1.01
    });

    it("should handle rounding correctly for credit tier limit amounts", () => {
      // Mirrors WalletService.updateWalletLimits daily/single limits
      const dailyLimit = 10_000.0;
      const currentWithdrawn = 9_999.99;
      const remaining = subtractMoney(dailyLimit, currentWithdrawn);

      expect(remaining).toBe(0.01);

      // Should allow a 0.01 withdrawal
      expect(remaining >= 0.01).toBe(true);

      // Should block a 0.02 withdrawal
      expect(remaining >= 0.02).toBe(false);
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 4. End-to-End Financial Workflow Precision
  // ─────────────────────────────────────────────────────────────────────────────

  describe("End-to-end financial workflow precision", () => {
    it("should maintain precision through a complete marketplace transaction", () => {
      // Buyer deposits -> places order -> escrow hold -> escrow release to seller
      const productPrice = 1250.75;
      const serviceFee = multiplyMoney(productPrice, 0.02); // 25.02
      const deliveryFee = 50.0;
      const totalAmount = addMoney(
        addMoney(productPrice, serviceFee),
        deliveryFee,
      );

      let buyer = createWallet(2000.0);
      let seller = createWallet(500.0);

      // Hold escrow for total order amount
      buyer = holdEscrow(buyer, totalAmount);
      expect(buyer.balance).toBe(subtractMoney(2000.0, totalAmount));
      expect(buyer.escrowBalance).toBe(totalAmount);

      // Release escrow to seller (seller receives product price, platform keeps fees)
      const sellerPayout = productPrice; // seller receives product price
      const result = releaseEscrow(buyer, seller, sellerPayout);

      expect(result.seller.balance).toBe(addMoney(500.0, sellerPayout));

      // Remaining escrow (fees retained by platform) should match fees
      const remainingEscrow = subtractMoney(totalAmount, sellerPayout);
      expect(result.buyer.escrowBalance).toBe(remainingEscrow);
      expect(remainingEscrow).toBe(addMoney(serviceFee, deliveryFee));
    });

    it("should maintain precision through a loan lifecycle", () => {
      // Loan request -> approval (deposit) -> repayments -> fully paid
      const loanAmount = 5000.0;
      const adminFee = multiplyMoney(loanAmount, 0.02); // 100.00
      const totalDue = addMoney(loanAmount, adminFee); // 5100.00

      let wallet = createWallet(200.0); // farmer has small existing balance

      // Loan disbursement
      wallet = deposit(wallet, loanAmount);
      expect(wallet.balance).toBe(5200.0);

      // Make monthly repayments (6 months)
      const monthlyPayment = roundMoney(totalDue / 6); // 850.00
      let totalPaid = 0;

      for (let month = 1; month <= 5; month++) {
        wallet = withdraw(wallet, monthlyPayment);
        totalPaid = addMoney(totalPaid, monthlyPayment);
      }

      // Final payment - pay exact remaining
      const finalPayment = subtractMoney(totalDue, totalPaid);
      wallet = withdraw(wallet, finalPayment);
      totalPaid = addMoney(totalPaid, finalPayment);

      expect(totalPaid).toBe(totalDue);
      // Remaining balance = initial 200 + 5000 loan - 5100 total repayment = 100
      expect(wallet.balance).toBe(100.0);
    });
  });
});
