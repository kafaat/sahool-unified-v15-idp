/// SAHOOL Wallet Provider
/// مزود المحفظة الرقمية - إدارة الرصيد والتصنيف الائتماني
///
/// Features:
/// - Wallet balance management
/// - Credit score display
/// - Transaction history
/// - Loan information

import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../core/config/env_config.dart';

// =============================================================================
// Models
// =============================================================================

/// التصنيف الائتماني
enum CreditTier {
  bronze,
  silver,
  gold,
  platinum,
}

/// المحفظة
class Wallet {
  final String id;
  final String userId;
  final String userType;
  final double balance;
  final String currency;
  final int creditScore;
  final CreditTier creditTier;
  final String creditTierAr;
  final double loanLimit;
  final double currentLoan;
  final double availableCredit;
  final bool isVerified;

  const Wallet({
    required this.id,
    required this.userId,
    required this.userType,
    required this.balance,
    required this.currency,
    required this.creditScore,
    required this.creditTier,
    required this.creditTierAr,
    required this.loanLimit,
    required this.currentLoan,
    required this.availableCredit,
    required this.isVerified,
  });

  factory Wallet.fromJson(Map<String, dynamic> json) {
    return Wallet(
      id: json['id'] as String,
      userId: json['userId'] as String,
      userType: json['userType'] as String? ?? 'farmer',
      balance: (json['balance'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'YER',
      creditScore: json['creditScore'] as int? ?? 300,
      creditTier: _parseCreditTier(json['creditTier'] as String?),
      creditTierAr: json['creditTierAr'] as String? ?? 'برونزي',
      loanLimit: (json['loanLimit'] as num?)?.toDouble() ?? 0,
      currentLoan: (json['currentLoan'] as num?)?.toDouble() ?? 0,
      availableCredit: (json['availableCredit'] as num?)?.toDouble() ?? 0,
      isVerified: json['isVerified'] as bool? ?? false,
    );
  }

  static CreditTier _parseCreditTier(String? tier) {
    switch (tier?.toUpperCase()) {
      case 'PLATINUM':
        return CreditTier.platinum;
      case 'GOLD':
        return CreditTier.gold;
      case 'SILVER':
        return CreditTier.silver;
      default:
        return CreditTier.bronze;
    }
  }

  /// الحصول على لون التصنيف
  String get tierColor {
    switch (creditTier) {
      case CreditTier.platinum:
        return '#E5E4E2';
      case CreditTier.gold:
        return '#FFD700';
      case CreditTier.silver:
        return '#C0C0C0';
      case CreditTier.bronze:
        return '#CD7F32';
    }
  }

  /// نسبة التصنيف (للرسم البياني)
  double get creditScorePercentage => (creditScore - 300) / 550;
}

/// نوع المعاملة
enum TransactionType {
  deposit,
  withdrawal,
  purchase,
  sale,
  loan,
  repayment,
  fee,
  refund,
}

/// المعاملة المالية
class WalletTransaction {
  final String id;
  final TransactionType type;
  final double amount;
  final double balanceAfter;
  final String? description;
  final String? descriptionAr;
  final DateTime createdAt;

  const WalletTransaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.balanceAfter,
    this.description,
    this.descriptionAr,
    required this.createdAt,
  });

  factory WalletTransaction.fromJson(Map<String, dynamic> json) {
    return WalletTransaction(
      id: json['id'] as String,
      type: _parseTransactionType(json['type'] as String),
      amount: (json['amount'] as num).toDouble(),
      balanceAfter: (json['balanceAfter'] as num).toDouble(),
      description: json['description'] as String?,
      descriptionAr: json['descriptionAr'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );
  }

  static TransactionType _parseTransactionType(String type) {
    switch (type.toUpperCase()) {
      case 'DEPOSIT':
        return TransactionType.deposit;
      case 'WITHDRAWAL':
        return TransactionType.withdrawal;
      case 'PURCHASE':
        return TransactionType.purchase;
      case 'SALE':
        return TransactionType.sale;
      case 'LOAN':
        return TransactionType.loan;
      case 'REPAYMENT':
        return TransactionType.repayment;
      case 'FEE':
        return TransactionType.fee;
      case 'REFUND':
        return TransactionType.refund;
      default:
        return TransactionType.deposit;
    }
  }

  /// الحصول على أيقونة المعاملة
  String get icon {
    switch (type) {
      case TransactionType.deposit:
        return '📥';
      case TransactionType.withdrawal:
        return '📤';
      case TransactionType.purchase:
        return '🛒';
      case TransactionType.sale:
        return '💰';
      case TransactionType.loan:
        return '🏦';
      case TransactionType.repayment:
        return '✅';
      case TransactionType.fee:
        return '📋';
      case TransactionType.refund:
        return '↩️';
    }
  }

  /// هل المعاملة إيجابية؟
  bool get isPositive => amount > 0;
}

/// القرض
class Loan {
  final String id;
  final double amount;
  final double totalDue;
  final double paidAmount;
  final int termMonths;
  final DateTime startDate;
  final DateTime dueDate;
  final String purpose;
  final String status;

  const Loan({
    required this.id,
    required this.amount,
    required this.totalDue,
    required this.paidAmount,
    required this.termMonths,
    required this.startDate,
    required this.dueDate,
    required this.purpose,
    required this.status,
  });

  factory Loan.fromJson(Map<String, dynamic> json) {
    return Loan(
      id: json['id'] as String,
      amount: (json['amount'] as num).toDouble(),
      totalDue: (json['totalDue'] as num).toDouble(),
      paidAmount: (json['paidAmount'] as num?)?.toDouble() ?? 0,
      termMonths: json['termMonths'] as int,
      startDate: DateTime.parse(json['startDate'] as String),
      dueDate: DateTime.parse(json['dueDate'] as String),
      purpose: json['purpose'] as String,
      status: json['status'] as String,
    );
  }

  /// المبلغ المتبقي
  double get remainingAmount => totalDue - paidAmount;

  /// نسبة السداد
  double get paymentProgress => paidAmount / totalDue;
}

// =============================================================================
// State
// =============================================================================

/// حالة المحفظة
class WalletState {
  final Wallet? wallet;
  final List<WalletTransaction> transactions;
  final List<Loan> loans;
  final bool isLoading;
  final String? error;

  const WalletState({
    this.wallet,
    this.transactions = const [],
    this.loans = const [],
    this.isLoading = false,
    this.error,
  });

  WalletState copyWith({
    Wallet? wallet,
    List<WalletTransaction>? transactions,
    List<Loan>? loans,
    bool? isLoading,
    String? error,
  }) {
    return WalletState(
      wallet: wallet ?? this.wallet,
      transactions: transactions ?? this.transactions,
      loans: loans ?? this.loans,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// =============================================================================
// Provider
// =============================================================================

/// مزود المحفظة
class WalletNotifier extends StateNotifier<WalletState> {
  final String _baseUrl;
  final String _userId;

  WalletNotifier({
    required String baseUrl,
    required String userId,
  })  : _baseUrl = baseUrl,
        _userId = userId,
        super(const WalletState()) {
    loadWallet();
  }

  /// تحميل المحفظة
  Future<void> loadWallet() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/v1/fintech/wallet/$_userId'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final wallet = Wallet.fromJson(data);

        state = state.copyWith(
          wallet: wallet,
          isLoading: false,
        );

        // تحميل المعاملات والقروض
        await Future.wait([
          loadTransactions(),
          loadLoans(),
        ]);
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'فشل في تحميل المحفظة',
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'خطأ في الاتصال: ${e.toString()}',
      );
    }
  }

  /// تحميل المعاملات
  Future<void> loadTransactions() async {
    if (state.wallet == null) return;

    try {
      final response = await http.get(
        Uri.parse(
          '$_baseUrl/api/v1/fintech/wallet/${state.wallet!.id}/transactions',
        ),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as List<dynamic>;
        final transactions = data
            .map((json) =>
                WalletTransaction.fromJson(json as Map<String, dynamic>))
            .toList();

        state = state.copyWith(transactions: transactions);
      }
    } catch (_) {
      // صمت
    }
  }

  /// تحميل القروض
  Future<void> loadLoans() async {
    if (state.wallet == null) return;

    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/v1/fintech/loans/${state.wallet!.id}'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as List<dynamic>;
        final loans = data
            .map((json) => Loan.fromJson(json as Map<String, dynamic>))
            .toList();

        state = state.copyWith(loans: loans);
      }
    } catch (_) {
      // صمت
    }
  }

  /// إيداع
  Future<bool> deposit(double amount, {String? description}) async {
    if (state.wallet == null) return false;

    try {
      final response = await http.post(
        Uri.parse(
          '$_baseUrl/api/v1/fintech/wallet/${state.wallet!.id}/deposit',
        ),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'amount': amount,
          'description': description,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        await loadWallet();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  /// سحب
  Future<bool> withdraw(double amount, {String? description}) async {
    if (state.wallet == null) return false;

    try {
      final response = await http.post(
        Uri.parse(
          '$_baseUrl/api/v1/fintech/wallet/${state.wallet!.id}/withdraw',
        ),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'amount': amount,
          'description': description,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        await loadWallet();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  /// طلب قرض
  Future<Map<String, dynamic>?> requestLoan({
    required double amount,
    required int termMonths,
    required String purpose,
    String? purposeDetails,
  }) async {
    if (state.wallet == null) return null;

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/v1/fintech/loans'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'walletId': state.wallet!.id,
          'amount': amount,
          'termMonths': termMonths,
          'purpose': purpose,
          'purposeDetails': purposeDetails,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        await loadLoans();
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  /// حساب التصنيف الائتماني
  Future<Map<String, dynamic>?> calculateCreditScore({
    required double totalArea,
    required int activeSeasons,
    required int fieldCount,
    required String diseaseRisk,
    required String irrigationType,
    required double avgYieldScore,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/v1/fintech/calculate-score'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'userId': _userId,
          'farmData': {
            'totalArea': totalArea,
            'activeSeasons': activeSeasons,
            'fieldCount': fieldCount,
            'diseaseRisk': diseaseRisk,
            'irrigationType': irrigationType,
            'avgYieldScore': avgYieldScore,
            'onTimePayments': 0,
            'latePayments': 0,
          },
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        await loadWallet();
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
      return null;
    } catch (_) {
      return null;
    }
  }
}

// =============================================================================
// Riverpod Providers
// =============================================================================

/// مزود معرف المستخدم
final userIdProvider = StateProvider<String>((ref) => '');

/// مزود رابط API - Marketplace API URL Provider
/// Uses EnvConfig for environment-specific URLs
final marketplaceApiUrlProvider = Provider<String>((ref) {
  return EnvConfig.marketplaceUrl;
});

/// مزود المحفظة الرئيسي
final walletProvider =
    StateNotifierProvider<WalletNotifier, WalletState>((ref) {
  final baseUrl = ref.watch(marketplaceApiUrlProvider);
  final userId = ref.watch(userIdProvider);

  return WalletNotifier(
    baseUrl: baseUrl,
    userId: userId,
  );
});

/// الرصيد الحالي
final balanceProvider = Provider<double>((ref) {
  return ref.watch(walletProvider).wallet?.balance ?? 0;
});

/// التصنيف الائتماني
final creditScoreProvider = Provider<int>((ref) {
  return ref.watch(walletProvider).wallet?.creditScore ?? 300;
});

/// الرصيد المتاح للتمويل
final availableCreditProvider = Provider<double>((ref) {
  return ref.watch(walletProvider).wallet?.availableCredit ?? 0;
});
