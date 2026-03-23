/// Wallet Parsing Tests
/// اختبارات تحليل بيانات المحفظة
///
/// Tests for compute() isolate JSON parsing in wallet
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/wallet/wallet_provider.dart';

void main() {
  group('WalletTransaction JSON parsing', () {
    test('should parse empty transaction list', () {
      final jsonStr = jsonEncode([]);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final result = data
          .map((json) =>
              WalletTransaction.fromJson(json as Map<String, dynamic>))
          .toList();

      expect(result, isEmpty);
    });

    test('should parse transaction list with valid data', () {
      final transactionsJson = [
        {
          'id': 'tx-001',
          'type': 'DEPOSIT',
          'amount': 5000.0,
          'balanceAfter': 15000.0,
          'description': 'Harvest sale',
          'descriptionAr': 'بيع المحصول',
          'createdAt': '2026-01-15T10:30:00Z',
        },
        {
          'id': 'tx-002',
          'type': 'PURCHASE',
          'amount': -150.0,
          'balanceAfter': 14850.0,
          'description': 'Seeds purchase',
          'descriptionAr': 'شراء بذور',
          'createdAt': '2026-01-16T08:00:00Z',
        },
      ];

      final jsonStr = jsonEncode(transactionsJson);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final transactions = data
          .map((json) =>
              WalletTransaction.fromJson(json as Map<String, dynamic>))
          .toList();

      expect(transactions.length, 2);
      expect(transactions[0].id, 'tx-001');
      expect(transactions[0].type, TransactionType.deposit);
      expect(transactions[0].amount, 5000.0);
      expect(transactions[0].isPositive, isTrue);
      expect(transactions[1].id, 'tx-002');
      expect(transactions[1].type, TransactionType.purchase);
      expect(transactions[1].isPositive, isFalse);
    });

    test('should handle all transaction types', () {
      final types = ['DEPOSIT', 'WITHDRAWAL', 'PURCHASE', 'SALE', 'LOAN', 'REPAYMENT', 'FEE', 'REFUND'];
      final items = types.map((type) => {
            'id': 'tx-$type',
            'type': type,
            'amount': 100.0,
            'balanceAfter': 1000.0,
            'createdAt': '2026-01-15T00:00:00Z',
          }).toList();

      final jsonStr = jsonEncode(items);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final transactions = data
          .map((json) =>
              WalletTransaction.fromJson(json as Map<String, dynamic>))
          .toList();

      expect(transactions.length, 8);
      expect(transactions[0].type, TransactionType.deposit);
      expect(transactions[1].type, TransactionType.withdrawal);
      expect(transactions[2].type, TransactionType.purchase);
      expect(transactions[3].type, TransactionType.sale);
      expect(transactions[4].type, TransactionType.loan);
      expect(transactions[5].type, TransactionType.repayment);
      expect(transactions[6].type, TransactionType.fee);
      expect(transactions[7].type, TransactionType.refund);
    });

    test('should handle large transaction list', () {
      final items = List.generate(500, (i) => {
            'id': 'tx-$i',
            'type': 'DEPOSIT',
            'amount': (i + 1) * 10.0,
            'balanceAfter': (i + 1) * 10.0,
            'createdAt': '2026-01-15T00:00:00Z',
          });

      final jsonStr = jsonEncode(items);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final transactions = data
          .map((json) =>
              WalletTransaction.fromJson(json as Map<String, dynamic>))
          .toList();

      expect(transactions.length, 500);
      expect(transactions.first.amount, 10.0);
      expect(transactions.last.amount, 5000.0);
    });
  });

  group('Loan JSON parsing', () {
    test('should parse loan list with valid data', () {
      final loansJson = [
        {
          'id': 'loan-001',
          'amount': 50000.0,
          'totalDue': 55000.0,
          'paidAmount': 20000.0,
          'termMonths': 12,
          'startDate': '2025-06-01T00:00:00Z',
          'dueDate': '2026-06-01T00:00:00Z',
          'purpose': 'Equipment Purchase',
          'status': 'ACTIVE',
        },
      ];

      final jsonStr = jsonEncode(loansJson);
      final data = jsonDecode(jsonStr) as List<dynamic>;
      final loans = data
          .map((json) => Loan.fromJson(json as Map<String, dynamic>))
          .toList();

      expect(loans.length, 1);
      expect(loans[0].id, 'loan-001');
      expect(loans[0].amount, 50000.0);
      expect(loans[0].totalDue, 55000.0);
      expect(loans[0].paidAmount, 20000.0);
      expect(loans[0].termMonths, 12);
    });
  });

  group('WalletState', () {
    test('should have default empty state', () {
      const state = WalletState();
      expect(state.wallet, isNull);
      expect(state.transactions, isEmpty);
      expect(state.loans, isEmpty);
      expect(state.isLoading, isFalse);
    });

    test('copyWith should update transactions', () {
      const state = WalletState();
      final tx = WalletTransaction(
        id: 'tx-1',
        type: TransactionType.deposit,
        amount: 100.0,
        balanceAfter: 100.0,
        createdAt: DateTime.now(),
      );

      final updated = state.copyWith(transactions: [tx]);
      expect(updated.transactions.length, 1);
      expect(updated.transactions.first.id, 'tx-1');
    });
  });
}
