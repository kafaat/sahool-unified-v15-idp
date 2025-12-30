import '../../../../core/http/api_client.dart';

/// Billing API - Payment and subscription management
/// خدمة الفوترة - إدارة المدفوعات والاشتراكات
class BillingApi {
  final ApiClient _client;

  BillingApi(this._client);

  // ═══════════════════════════════════════════════════════════════════════════
  // Wallet Operations - عمليات المحفظة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get wallet balance
  /// الحصول على رصيد المحفظة
  Future<WalletBalance> getWalletBalance() async {
    final response = await _client.get(
      '/api/v1/billing/wallet',
      queryParameters: {'tenant_id': _client.tenantId},
    );

    if (response is Map<String, dynamic>) {
      return WalletBalance.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل رصيد المحفظة',
    );
  }

  /// Deposit funds to wallet
  /// إيداع أموال في المحفظة
  Future<PaymentResult> deposit({
    required double amount,
    required PaymentMethod method,
    String? phoneNumber, // For Tharwatt/mobile money
    String? stripeToken, // For credit card
    // TODO: SECURITY - Implement proper Stripe SDK flow instead of passing tokens directly
    // The current implementation exposes the token. Should use Stripe Elements/SDK on client
    // and only pass payment intent IDs to the backend
  }) async {
    final response = await _client.post(
      '/api/v1/billing/deposit',
      {
        'tenant_id': _client.tenantId,
        'amount': amount,
        'method': method.value,
        'phone_number': phoneNumber,
        'stripe_token': stripeToken,
      },
    );

    if (response is Map<String, dynamic>) {
      return PaymentResult.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في معالجة الإيداع',
    );
  }

  /// Withdraw funds from wallet
  /// سحب أموال من المحفظة
  Future<PaymentResult> withdraw({
    required double amount,
    required String phoneNumber,
  }) async {
    final response = await _client.post(
      '/api/v1/billing/withdraw',
      {
        'tenant_id': _client.tenantId,
        'amount': amount,
        'phone_number': phoneNumber,
      },
    );

    if (response is Map<String, dynamic>) {
      return PaymentResult.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في معالجة السحب',
    );
  }

  /// Transfer funds between users
  /// تحويل أموال بين المستخدمين
  Future<PaymentResult> transfer({
    required double amount,
    required String recipientId,
    String? note,
  }) async {
    final response = await _client.post(
      '/api/v1/billing/transfer',
      {
        'tenant_id': _client.tenantId,
        'amount': amount,
        'recipient_id': recipientId,
        'note': note,
      },
    );

    if (response is Map<String, dynamic>) {
      return PaymentResult.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في معالجة التحويل',
    );
  }

  /// Get wallet transactions history
  /// الحصول على سجل معاملات المحفظة
  Future<List<WalletTransaction>> getTransactions({
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _client.get(
      '/api/v1/billing/transactions',
      queryParameters: {
        'tenant_id': _client.tenantId,
        'limit': limit,
        'offset': offset,
      },
    );

    if (response is Map && response['transactions'] is List) {
      return (response['transactions'] as List)
          .cast<Map<String, dynamic>>()
          .map((json) => WalletTransaction.fromJson(json))
          .toList();
    }

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => WalletTransaction.fromJson(json))
          .toList();
    }

    return [];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Subscription Operations - عمليات الاشتراك
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get current subscription
  /// الحصول على الاشتراك الحالي
  Future<Subscription?> getCurrentSubscription() async {
    final response = await _client.get(
      '/api/v1/billing/tenants/${_client.tenantId}/subscription',
    );

    if (response is Map<String, dynamic>) {
      return Subscription.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل بيانات الاشتراك',
    );
  }

  /// Get available plans
  /// الحصول على الخطط المتاحة
  Future<List<Plan>> getAvailablePlans() async {
    final response = await _client.get('/api/v1/billing/plans');

    if (response is Map && response['plans'] is List) {
      return (response['plans'] as List)
          .cast<Map<String, dynamic>>()
          .map((json) => Plan.fromJson(json))
          .toList();
    }

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => Plan.fromJson(json))
          .toList();
    }

    return [];
  }

  /// Upgrade/change subscription plan
  /// ترقية/تغيير خطة الاشتراك
  Future<Subscription> changePlan({
    required String planId,
    String billingCycle = 'monthly',
  }) async {
    final response = await _client.post(
      '/api/v1/billing/tenants/${_client.tenantId}/subscription',
      {
        'plan_id': planId,
        'billing_cycle': billingCycle,
      },
    );

    if (response is Map<String, dynamic>) {
      return Subscription.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تغيير الخطة',
    );
  }

  /// Cancel subscription
  /// إلغاء الاشتراك
  Future<void> cancelSubscription({String? reason}) async {
    await _client.delete(
      '/api/v1/billing/tenants/${_client.tenantId}/subscription',
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Invoice Operations - عمليات الفواتير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get invoices
  /// الحصول على الفواتير
  Future<List<Invoice>> getInvoices({
    int limit = 20,
    String? status,
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
    };

    if (status != null) {
      queryParams['status'] = status;
    }

    final response = await _client.get(
      '/api/v1/billing/tenants/${_client.tenantId}/invoices',
      queryParameters: queryParams,
    );

    if (response is Map && response['invoices'] is List) {
      return (response['invoices'] as List)
          .cast<Map<String, dynamic>>()
          .map((json) => Invoice.fromJson(json))
          .toList();
    }

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => Invoice.fromJson(json))
          .toList();
    }

    return [];
  }

  /// Pay invoice
  /// دفع فاتورة
  Future<PaymentResult> payInvoice({
    required String invoiceId,
    required PaymentMethod method,
    String? phoneNumber,
    String? stripeToken,
  }) async {
    final response = await _client.post(
      '/api/v1/billing/payments',
      {
        'invoice_id': invoiceId,
        'method': method.value,
        'phone_number': phoneNumber,
        'stripe_token': stripeToken,
      },
    );

    if (response is Map<String, dynamic>) {
      return PaymentResult.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في معالجة الدفع',
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Usage Tracking - تتبع الاستخدام
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get usage statistics
  /// الحصول على إحصائيات الاستخدام
  Future<UsageStats> getUsageStats() async {
    final response = await _client.get(
      '/api/v1/billing/tenants/${_client.tenantId}/usage',
    );

    if (response is Map<String, dynamic>) {
      return UsageStats.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل الاستخدام',
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Data Models - نماذج البيانات
// ═══════════════════════════════════════════════════════════════════════════════

/// Payment methods
enum PaymentMethod {
  creditCard('credit_card'),
  bankTransfer('bank_transfer'),
  mobileMoney('mobile_money'),
  cash('cash'),
  tharwatt('tharwatt');

  final String value;
  const PaymentMethod(this.value);

  static PaymentMethod fromString(String value) {
    return PaymentMethod.values.firstWhere(
      (m) => m.value == value,
      orElse: () => PaymentMethod.cash,
    );
  }
}

/// Wallet balance
class WalletBalance {
  final double balance;
  final String currency;
  final double pendingBalance;
  final DateTime lastUpdated;

  WalletBalance({
    required this.balance,
    required this.currency,
    required this.pendingBalance,
    required this.lastUpdated,
  });

  factory WalletBalance.fromJson(Map<String, dynamic> json) {
    return WalletBalance(
      balance: (json['balance'] ?? 0).toDouble(),
      currency: json['currency'] ?? 'YER',
      pendingBalance: (json['pending_balance'] ?? 0).toDouble(),
      lastUpdated: DateTime.tryParse(json['last_updated'] ?? '') ?? DateTime.now(),
    );
  }
}

/// Payment result
class PaymentResult {
  final bool success;
  final String? paymentId;
  final String status;
  final String? message;
  final String? messageAr;
  final Map<String, dynamic>? tharwattResponse;
  final Map<String, dynamic>? stripeResponse;

  PaymentResult({
    required this.success,
    this.paymentId,
    required this.status,
    this.message,
    this.messageAr,
    this.tharwattResponse,
    this.stripeResponse,
  });

  factory PaymentResult.fromJson(Map<String, dynamic> json) {
    final payment = json['payment'] as Map<String, dynamic>?;
    return PaymentResult(
      success: json['success'] ?? false,
      paymentId: payment?['payment_id'] ?? json['payment_id'],
      status: payment?['status'] ?? json['status'] ?? 'unknown',
      message: json['message'],
      messageAr: json['message_ar'],
      tharwattResponse: json['tharwatt_response'],
      stripeResponse: json['stripe_response'],
    );
  }
}

/// Wallet transaction
class WalletTransaction {
  final String id;
  final String type; // deposit, withdraw, transfer, payment
  final double amount;
  final String currency;
  final String status;
  final String? description;
  final DateTime createdAt;

  WalletTransaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.currency,
    required this.status,
    this.description,
    required this.createdAt,
  });

  factory WalletTransaction.fromJson(Map<String, dynamic> json) {
    return WalletTransaction(
      id: json['id'] ?? json['transaction_id'] ?? '',
      type: json['type'] ?? 'unknown',
      amount: (json['amount'] ?? 0).toDouble(),
      currency: json['currency'] ?? 'YER',
      status: json['status'] ?? 'pending',
      description: json['description'],
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}

/// Subscription plan
class Plan {
  final String id;
  final String name;
  final String nameAr;
  final String tier;
  final double priceMonthly;
  final double priceYearly;
  final String currency;
  final Map<String, int> limits;
  final List<String> features;

  Plan({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.tier,
    required this.priceMonthly,
    required this.priceYearly,
    required this.currency,
    required this.limits,
    required this.features,
  });

  factory Plan.fromJson(Map<String, dynamic> json) {
    return Plan(
      id: json['plan_id'] ?? json['id'] ?? '',
      name: json['name'] ?? '',
      nameAr: json['name_ar'] ?? json['name'] ?? '',
      tier: json['tier'] ?? 'starter',
      priceMonthly: (json['price_monthly'] ?? 0).toDouble(),
      priceYearly: (json['price_yearly'] ?? 0).toDouble(),
      currency: json['currency'] ?? 'USD',
      limits: Map<String, int>.from(json['limits'] ?? {}),
      features: (json['features'] as List?)?.cast<String>() ?? [],
    );
  }
}

/// Subscription
class Subscription {
  final String id;
  final String planId;
  final String status;
  final String billingCycle;
  final DateTime startDate;
  final DateTime? endDate;
  final DateTime? nextBillingDate;
  final Plan? plan;

  Subscription({
    required this.id,
    required this.planId,
    required this.status,
    required this.billingCycle,
    required this.startDate,
    this.endDate,
    this.nextBillingDate,
    this.plan,
  });

  factory Subscription.fromJson(Map<String, dynamic> json) {
    return Subscription(
      id: json['subscription_id'] ?? json['id'] ?? '',
      planId: json['plan_id'] ?? '',
      status: json['status'] ?? 'active',
      billingCycle: json['billing_cycle'] ?? 'monthly',
      startDate: DateTime.tryParse(json['start_date'] ?? '') ?? DateTime.now(),
      endDate: json['end_date'] != null ? DateTime.tryParse(json['end_date']) : null,
      nextBillingDate: json['next_billing_date'] != null
          ? DateTime.tryParse(json['next_billing_date'])
          : null,
      plan: json['plan'] != null ? Plan.fromJson(json['plan']) : null,
    );
  }
}

/// Invoice
class Invoice {
  final String id;
  final String invoiceNumber;
  final String status;
  final double total;
  final double amountPaid;
  final double amountDue;
  final String currency;
  final DateTime issueDate;
  final DateTime dueDate;
  final DateTime? paidDate;

  Invoice({
    required this.id,
    required this.invoiceNumber,
    required this.status,
    required this.total,
    required this.amountPaid,
    required this.amountDue,
    required this.currency,
    required this.issueDate,
    required this.dueDate,
    this.paidDate,
  });

  factory Invoice.fromJson(Map<String, dynamic> json) {
    return Invoice(
      id: json['invoice_id'] ?? json['id'] ?? '',
      invoiceNumber: json['invoice_number'] ?? '',
      status: json['status'] ?? 'pending',
      total: (json['total'] ?? 0).toDouble(),
      amountPaid: (json['amount_paid'] ?? 0).toDouble(),
      amountDue: (json['amount_due'] ?? 0).toDouble(),
      currency: json['currency'] ?? 'USD',
      issueDate: DateTime.tryParse(json['issue_date'] ?? '') ?? DateTime.now(),
      dueDate: DateTime.tryParse(json['due_date'] ?? '') ?? DateTime.now(),
      paidDate: json['paid_date'] != null ? DateTime.tryParse(json['paid_date']) : null,
    );
  }
}

/// Usage statistics
class UsageStats {
  final int fieldsUsed;
  final int fieldsLimit;
  final int usersUsed;
  final int usersLimit;
  final int storageUsedMb;
  final int storageLimitMb;
  final int apiCallsUsed;
  final int apiCallsLimit;

  UsageStats({
    required this.fieldsUsed,
    required this.fieldsLimit,
    required this.usersUsed,
    required this.usersLimit,
    required this.storageUsedMb,
    required this.storageLimitMb,
    required this.apiCallsUsed,
    required this.apiCallsLimit,
  });

  factory UsageStats.fromJson(Map<String, dynamic> json) {
    final usage = json['usage'] ?? json;
    return UsageStats(
      fieldsUsed: usage['fields_used'] ?? 0,
      fieldsLimit: usage['fields_limit'] ?? 0,
      usersUsed: usage['users_used'] ?? 0,
      usersLimit: usage['users_limit'] ?? 0,
      storageUsedMb: usage['storage_used_mb'] ?? 0,
      storageLimitMb: usage['storage_limit_mb'] ?? 0,
      apiCallsUsed: usage['api_calls_used'] ?? 0,
      apiCallsLimit: usage['api_calls_limit'] ?? 0,
    );
  }

  double get fieldsPercentage => fieldsLimit > 0 ? fieldsUsed / fieldsLimit : 0;
  double get usersPercentage => usersLimit > 0 ? usersUsed / usersLimit : 0;
  double get storagePercentage => storageLimitMb > 0 ? storageUsedMb / storageLimitMb : 0;
  double get apiPercentage => apiCallsLimit > 0 ? apiCallsUsed / apiCallsLimit : 0;
}

/// Exception class
class ApiException implements Exception {
  final String code;
  final String message;

  ApiException({required this.code, required this.message});
}
