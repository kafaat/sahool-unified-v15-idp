/// مزود خدمة المدفوعات
/// Payment Provider with Riverpod

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'data/payment_models.dart';
import 'data/tharwatt_service.dart';
import '../../core/network/api_result.dart';

/// تكوين Tharwatt
final tharwattConfigProvider = Provider<TharwattConfig>((ref) {
  // استخدام وضع الاختبار افتراضياً
  return TharwattConfig.test();
});

/// خدمة Tharwatt
final tharwattServiceProvider = Provider<TharwattPaymentService>((ref) {
  final config = ref.watch(tharwattConfigProvider);
  return TharwattPaymentService(config: config);
});

/// حالة المدفوعات
class PaymentState {
  final bool isLoading;
  final String? error;
  final PaymentTransaction? currentTransaction;
  final List<PaymentTransaction> transactions;
  final double? balance;

  const PaymentState({
    this.isLoading = false,
    this.error,
    this.currentTransaction,
    this.transactions = const [],
    this.balance,
  });

  PaymentState copyWith({
    bool? isLoading,
    String? error,
    PaymentTransaction? currentTransaction,
    List<PaymentTransaction>? transactions,
    double? balance,
    bool clearError = false,
    bool clearTransaction = false,
  }) {
    return PaymentState(
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      currentTransaction:
          clearTransaction ? null : (currentTransaction ?? this.currentTransaction),
      transactions: transactions ?? this.transactions,
      balance: balance ?? this.balance,
    );
  }
}

/// مدير حالة المدفوعات
class PaymentNotifier extends StateNotifier<PaymentState> {
  final TharwattPaymentService _service;
  final String walletId;

  PaymentNotifier({
    required TharwattPaymentService service,
    required this.walletId,
  })  : _service = service,
        super(const PaymentState());

  /// إيداع في المحفظة
  Future<bool> deposit({
    required double amount,
    required String phoneNumber,
    String? description,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _service.initiateDeposit(
      walletId: walletId,
      amount: amount,
      phoneNumber: phoneNumber,
      description: description,
    );

    return result.when(
      success: (response) {
        if (response.isSuccess) {
          state = state.copyWith(
            isLoading: false,
            currentTransaction: PaymentTransaction(
              id: response.transactionId,
              externalId: response.reference,
              walletId: walletId,
              amount: amount,
              status: PaymentStatus.completed,
              type: PaymentType.deposit,
              method: PaymentMethod.tharwatt,
              description: description,
              createdAt: DateTime.now(),
              completedAt: DateTime.now(),
            ),
          );
          // تحديث الرصيد
          _refreshBalance();
          return true;
        } else {
          state = state.copyWith(
            isLoading: false,
            error: response.message ?? 'فشلت عملية الإيداع',
          );
          return false;
        }
      },
      failure: (error, _) {
        state = state.copyWith(
          isLoading: false,
          error: error,
        );
        return false;
      },
    );
  }

  /// سحب من المحفظة
  Future<bool> withdraw({
    required double amount,
    required String phoneNumber,
    String? accountNumber,
    String? description,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _service.initiateWithdraw(
      walletId: walletId,
      amount: amount,
      phoneNumber: phoneNumber,
      accountNumber: accountNumber,
      description: description,
    );

    return result.when(
      success: (response) {
        if (response.isSuccess) {
          state = state.copyWith(
            isLoading: false,
            currentTransaction: PaymentTransaction(
              id: response.transactionId,
              externalId: response.reference,
              walletId: walletId,
              amount: amount,
              status: PaymentStatus.completed,
              type: PaymentType.withdraw,
              method: PaymentMethod.tharwatt,
              description: description,
              createdAt: DateTime.now(),
              completedAt: DateTime.now(),
            ),
          );
          _refreshBalance();
          return true;
        } else {
          state = state.copyWith(
            isLoading: false,
            error: response.message ?? 'فشلت عملية السحب',
          );
          return false;
        }
      },
      failure: (error, _) {
        state = state.copyWith(
          isLoading: false,
          error: error,
        );
        return false;
      },
    );
  }

  /// تحويل إلى رقم آخر
  Future<bool> transfer({
    required String toPhoneNumber,
    required double amount,
    String? description,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _service.initiateTransfer(
      fromWalletId: walletId,
      toPhoneNumber: toPhoneNumber,
      amount: amount,
      description: description,
    );

    return result.when(
      success: (response) {
        if (response.isSuccess) {
          state = state.copyWith(
            isLoading: false,
            currentTransaction: PaymentTransaction(
              id: response.transactionId,
              externalId: response.reference,
              walletId: walletId,
              amount: amount,
              status: PaymentStatus.completed,
              type: PaymentType.transfer,
              method: PaymentMethod.tharwatt,
              description: description ?? 'تحويل إلى $toPhoneNumber',
              createdAt: DateTime.now(),
              completedAt: DateTime.now(),
            ),
          );
          _refreshBalance();
          return true;
        } else {
          state = state.copyWith(
            isLoading: false,
            error: response.message ?? 'فشلت عملية التحويل',
          );
          return false;
        }
      },
      failure: (error, _) {
        state = state.copyWith(
          isLoading: false,
          error: error,
        );
        return false;
      },
    );
  }

  /// شحن رصيد موبايل
  Future<bool> topupMobile({
    required String mobileNumber,
    required double amount,
    required String operator,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _service.topupMobile(
      walletId: walletId,
      mobileNumber: mobileNumber,
      amount: amount,
      operator: operator,
    );

    return result.when(
      success: (response) {
        if (response.isSuccess) {
          state = state.copyWith(
            isLoading: false,
            currentTransaction: PaymentTransaction(
              id: response.transactionId,
              externalId: response.reference,
              walletId: walletId,
              amount: amount,
              status: PaymentStatus.completed,
              type: PaymentType.topup,
              method: PaymentMethod.tharwatt,
              description: 'شحن رصيد $mobileNumber',
              createdAt: DateTime.now(),
              completedAt: DateTime.now(),
            ),
          );
          _refreshBalance();
          return true;
        } else {
          state = state.copyWith(
            isLoading: false,
            error: response.message ?? 'فشلت عملية الشحن',
          );
          return false;
        }
      },
      failure: (error, _) {
        state = state.copyWith(
          isLoading: false,
          error: error,
        );
        return false;
      },
    );
  }

  /// تحديث الرصيد
  Future<void> _refreshBalance() async {
    final result = await _service.checkBalance(walletId);
    result.when(
      success: (balance) {
        state = state.copyWith(balance: balance);
      },
      failure: (_, __) {
        // تجاهل الخطأ - الرصيد سيتم تحديثه لاحقاً
      },
    );
  }

  /// تحميل سجل المعاملات
  Future<void> loadTransactions({int page = 1}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _service.getTransactionHistory(
      walletId: walletId,
      page: page,
    );

    result.when(
      success: (transactions) {
        state = state.copyWith(
          isLoading: false,
          transactions: transactions,
        );
      },
      failure: (error, _) {
        state = state.copyWith(
          isLoading: false,
          error: error,
        );
      },
    );
  }

  /// التحقق من حالة معاملة
  Future<PaymentTransaction?> checkTransactionStatus(String transactionId) async {
    final result = await _service.checkTransactionStatus(transactionId);
    return result.when(
      success: (transaction) {
        state = state.copyWith(currentTransaction: transaction);
        return transaction;
      },
      failure: (_, __) => null,
    );
  }

  /// إلغاء معاملة
  Future<bool> cancelTransaction(String transactionId) async {
    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _service.cancelTransaction(transactionId);

    return result.when(
      success: (_) {
        state = state.copyWith(
          isLoading: false,
          clearTransaction: true,
        );
        loadTransactions();
        return true;
      },
      failure: (error, _) {
        state = state.copyWith(
          isLoading: false,
          error: error,
        );
        return false;
      },
    );
  }

  /// مسح الخطأ الحالي
  void clearError() {
    state = state.copyWith(clearError: true);
  }

  /// مسح المعاملة الحالية
  void clearCurrentTransaction() {
    state = state.copyWith(clearTransaction: true);
  }
}

/// مزود حالة المدفوعات
final paymentProvider =
    StateNotifierProvider.family<PaymentNotifier, PaymentState, String>(
  (ref, walletId) {
    final service = ref.watch(tharwattServiceProvider);
    return PaymentNotifier(
      service: service,
      walletId: walletId,
    );
  },
);

/// مزود المشغلين
final mobileOperatorsProvider = FutureProvider<List<MobileOperator>>((ref) async {
  final service = ref.watch(tharwattServiceProvider);
  final result = await service.getSupportedOperators();

  return result.when(
    success: (operators) => operators,
    failure: (_, __) => MobileOperator.defaultOperators,
  );
});

/// مزود التحقق من رقم الهاتف
final validatePhoneProvider =
    FutureProvider.family<bool, String>((ref, phoneNumber) async {
  final service = ref.watch(tharwattServiceProvider);
  final result = await service.validatePhoneNumber(phoneNumber);

  return result.when(
    success: (isValid) => isValid,
    failure: (_, __) => false,
  );
});
