import '../../../../core/http/api_client.dart';

/// Billing API - Payment and subscription management
/// خدمة الفوترة - إدارة المدفوعات والاشتراكات
///
/// ## Stripe Payment Flow (Secure)
/// الدفع الآمن عبر Stripe:
///
/// 1. Client calls [createPaymentIntent] to get a PaymentIntent from backend
/// 2. Backend creates PaymentIntent with Stripe and returns client_secret
/// 3. Client uses flutter_stripe SDK to confirm payment with client_secret
/// 4. Client calls [confirmPaymentIntent] with PaymentIntent ID
/// 5. Backend verifies payment status directly with Stripe
///
/// This flow ensures sensitive payment data never passes through our servers.
class BillingApi {
  final ApiClient _client;

  BillingApi(this._client);

  // ═══════════════════════════════════════════════════════════════════════════
  // Stripe Payment Intent Operations - عمليات نية الدفع
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create a Stripe PaymentIntent for one-time payment
  /// إنشاء نية دفع لعملية دفع واحدة
  ///
  /// Returns a [StripePaymentIntent] containing the client_secret
  /// needed by the Stripe SDK to confirm the payment.
  ///
  /// Usage:
  /// ```dart
  /// final intent = await billingApi.createPaymentIntent(
  ///   amount: 100.0,
  ///   currency: 'usd',
  /// );
  /// // Use flutter_stripe SDK to confirm payment
  /// await Stripe.instance.confirmPayment(
  ///   paymentIntentClientSecret: intent.clientSecret,
  ///   data: PaymentMethodParams.card(...),
  /// );
  /// // Verify with backend
  /// await billingApi.confirmPaymentIntent(paymentIntentId: intent.id);
  /// ```
  Future<StripePaymentIntent> createPaymentIntent({
    required double amount,
    String currency = 'usd',
    String? description,
    Map<String, String>? metadata,
  }) async {
    final response = await _client.post(
      '/api/v1/billing/stripe/payment-intents',
      {
        'tenant_id': _client.tenantId,
        'amount': amount,
        'currency': currency,
        if (description != null) 'description': description,
        if (metadata != null) 'metadata': metadata,
      },
    );

    if (response is Map<String, dynamic>) {
      return StripePaymentIntent.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في إنشاء نية الدفع',
    );
  }

  /// Confirm a PaymentIntent after Stripe SDK confirmation
  /// تأكيد نية الدفع بعد تأكيد SDK
  ///
  /// Call this after the Stripe SDK successfully confirms the payment.
  /// Backend will verify the payment status directly with Stripe.
  Future<PaymentResult> confirmPaymentIntent({
    required String paymentIntentId,
  }) async {
    final response = await _client.post(
      '/api/v1/billing/stripe/payment-intents/$paymentIntentId/confirm',
      {
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return PaymentResult.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تأكيد الدفع',
    );
  }

  /// Create a Stripe SetupIntent for saving payment method
  /// إنشاء نية إعداد لحفظ طريقة الدفع
  ///
  /// Use this to save a card for future payments without charging.
  Future<StripeSetupIntent> createSetupIntent({
    String? customerId,
    Map<String, String>? metadata,
  }) async {
    final response = await _client.post(
      '/api/v1/billing/stripe/setup-intents',
      {
        'tenant_id': _client.tenantId,
        if (customerId != null) 'customer_id': customerId,
        if (metadata != null) 'metadata': metadata,
      },
    );

    if (response is Map<String, dynamic>) {
      return StripeSetupIntent.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في إنشاء نية الإعداد',
    );
  }

  /// Confirm a SetupIntent after Stripe SDK confirmation
  /// تأكيد نية الإعداد بعد تأكيد SDK
  Future<SetupIntentResult> confirmSetupIntent({
    required String setupIntentId,
  }) async {
    final response = await _client.post(
      '/api/v1/billing/stripe/setup-intents/$setupIntentId/confirm',
      {
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return SetupIntentResult.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تأكيد حفظ طريقة الدفع',
    );
  }

  /// Get Stripe publishable key for SDK initialization
  /// الحصول على مفتاح Stripe العام لتهيئة SDK
  Future<StripeConfig> getStripeConfig() async {
    final response = await _client.get('/api/v1/billing/stripe/config');

    if (response is Map<String, dynamic>) {
      return StripeConfig.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في الحصول على إعدادات Stripe',
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Saved Payment Methods - طرق الدفع المحفوظة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get saved payment methods
  /// الحصول على طرق الدفع المحفوظة
  Future<List<SavedPaymentMethod>> getSavedPaymentMethods() async {
    final response = await _client.get(
      '/api/v1/billing/payment-methods',
      queryParameters: {'tenant_id': _client.tenantId},
    );

    if (response is Map && response['payment_methods'] is List) {
      return (response['payment_methods'] as List)
          .cast<Map<String, dynamic>>()
          .map((json) => SavedPaymentMethod.fromJson(json))
          .toList();
    }

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => SavedPaymentMethod.fromJson(json))
          .toList();
    }

    return [];
  }

  /// Delete a saved payment method
  /// حذف طريقة دفع محفوظة
  Future<void> deletePaymentMethod({required String paymentMethodId}) async {
    await _client.delete(
      '/api/v1/billing/payment-methods/$paymentMethodId',
    );
  }

  /// Set default payment method
  /// تعيين طريقة الدفع الافتراضية
  Future<void> setDefaultPaymentMethod({required String paymentMethodId}) async {
    await _client.post(
      '/api/v1/billing/payment-methods/$paymentMethodId/default',
      {
        'tenant_id': _client.tenantId,
      },
    );
  }

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

  /// Deposit funds to wallet using secure payment flow
  /// إيداع أموال في المحفظة باستخدام الدفع الآمن
  ///
  /// For credit card payments:
  /// - First call [createPaymentIntent] to get a PaymentIntent
  /// - Use Stripe SDK to confirm payment with the client_secret
  /// - Then call this method with the [paymentIntentId]
  ///
  /// For Tharwatt/mobile money:
  /// - Provide [phoneNumber] for mobile money flow
  Future<PaymentResult> deposit({
    required double amount,
    required PaymentMethod method,
    String? phoneNumber, // For Tharwatt/mobile money
    String? paymentIntentId, // For credit card (from Stripe SDK flow)
    String? paymentMethodId, // For saved payment methods
  }) async {
    // Validate parameters based on payment method
    if (method == PaymentMethod.creditCard) {
      if (paymentIntentId == null && paymentMethodId == null) {
        throw ApiException(
          code: 'INVALID_PARAMS',
          message: 'يجب توفير معرف نية الدفع أو طريقة الدفع المحفوظة',
        );
      }
    } else if (method == PaymentMethod.tharwatt || method == PaymentMethod.mobileMoney) {
      if (phoneNumber == null || phoneNumber.isEmpty) {
        throw ApiException(
          code: 'INVALID_PARAMS',
          message: 'يجب توفير رقم الهاتف للدفع عبر المحمول',
        );
      }
    }

    final response = await _client.post(
      '/api/v1/billing/deposit',
      {
        'tenant_id': _client.tenantId,
        'amount': amount,
        'method': method.value,
        if (phoneNumber != null) 'phone_number': phoneNumber,
        if (paymentIntentId != null) 'payment_intent_id': paymentIntentId,
        if (paymentMethodId != null) 'payment_method_id': paymentMethodId,
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

  /// Create PaymentIntent for invoice payment
  /// إنشاء نية دفع لدفع فاتورة
  ///
  /// Use this to get a PaymentIntent for paying an invoice with a card.
  /// The returned client_secret should be used with the Stripe SDK.
  Future<StripePaymentIntent> createInvoicePaymentIntent({
    required String invoiceId,
  }) async {
    final response = await _client.post(
      '/api/v1/billing/invoices/$invoiceId/payment-intent',
      {
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return StripePaymentIntent.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في إنشاء نية الدفع للفاتورة',
    );
  }

  /// Pay invoice using secure payment flow
  /// دفع فاتورة باستخدام الدفع الآمن
  ///
  /// For credit card payments:
  /// - First call [createInvoicePaymentIntent] to get a PaymentIntent
  /// - Use Stripe SDK to confirm payment with the client_secret
  /// - Then call this method with the [paymentIntentId]
  ///
  /// For Tharwatt/mobile money:
  /// - Provide [phoneNumber] for mobile money flow
  Future<PaymentResult> payInvoice({
    required String invoiceId,
    required PaymentMethod method,
    String? phoneNumber, // For Tharwatt/mobile money
    String? paymentIntentId, // For credit card (from Stripe SDK flow)
    String? paymentMethodId, // For saved payment methods
  }) async {
    // Validate parameters based on payment method
    if (method == PaymentMethod.creditCard) {
      if (paymentIntentId == null && paymentMethodId == null) {
        throw ApiException(
          code: 'INVALID_PARAMS',
          message: 'يجب توفير معرف نية الدفع أو طريقة الدفع المحفوظة',
        );
      }
    } else if (method == PaymentMethod.tharwatt || method == PaymentMethod.mobileMoney) {
      if (phoneNumber == null || phoneNumber.isEmpty) {
        throw ApiException(
          code: 'INVALID_PARAMS',
          message: 'يجب توفير رقم الهاتف للدفع عبر المحمول',
        );
      }
    }

    final response = await _client.post(
      '/api/v1/billing/payments',
      {
        'invoice_id': invoiceId,
        'method': method.value,
        if (phoneNumber != null) 'phone_number': phoneNumber,
        if (paymentIntentId != null) 'payment_intent_id': paymentIntentId,
        if (paymentMethodId != null) 'payment_method_id': paymentMethodId,
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
      balance: ((json['balance'] ?? 0) as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'YER',
      pendingBalance: ((json['pending_balance'] ?? 0) as num).toDouble(),
      lastUpdated: DateTime.tryParse((json['last_updated'] as String?) ?? '') ?? DateTime.now(),
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
      success: (json['success'] as bool?) ?? false,
      paymentId: (payment?['payment_id'] ?? json['payment_id']) as String?,
      status: (payment?['status'] ?? json['status'] ?? 'unknown') as String,
      message: json['message'] as String?,
      messageAr: json['message_ar'] as String?,
      tharwattResponse: json['tharwatt_response'] as Map<String, dynamic>?,
      stripeResponse: json['stripe_response'] as Map<String, dynamic>?,
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
      id: (json['id'] ?? json['transaction_id'] ?? '') as String,
      type: (json['type'] as String?) ?? 'unknown',
      amount: ((json['amount'] ?? 0) as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'YER',
      status: (json['status'] as String?) ?? 'pending',
      description: json['description'] as String?,
      createdAt: DateTime.tryParse((json['created_at'] as String?) ?? '') ?? DateTime.now(),
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
      id: (json['plan_id'] ?? json['id'] ?? '') as String,
      name: (json['name'] as String?) ?? '',
      nameAr: (json['name_ar'] ?? json['name'] ?? '') as String,
      tier: (json['tier'] as String?) ?? 'starter',
      priceMonthly: ((json['price_monthly'] ?? 0) as num).toDouble(),
      priceYearly: ((json['price_yearly'] ?? 0) as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'USD',
      limits: Map<String, int>.from((json['limits'] as Map?) ?? {}),
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
      id: (json['subscription_id'] ?? json['id'] ?? '') as String,
      planId: (json['plan_id'] as String?) ?? '',
      status: (json['status'] as String?) ?? 'active',
      billingCycle: (json['billing_cycle'] as String?) ?? 'monthly',
      startDate: DateTime.tryParse((json['start_date'] as String?) ?? '') ?? DateTime.now(),
      endDate: json['end_date'] != null ? DateTime.tryParse(json['end_date'] as String) : null,
      nextBillingDate: json['next_billing_date'] != null
          ? DateTime.tryParse(json['next_billing_date'] as String)
          : null,
      plan: json['plan'] != null ? Plan.fromJson(json['plan'] as Map<String, dynamic>) : null,
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

// ═══════════════════════════════════════════════════════════════════════════════
// Stripe Models - نماذج Stripe
// ═══════════════════════════════════════════════════════════════════════════════

/// Stripe configuration for SDK initialization
/// إعدادات Stripe لتهيئة SDK
class StripeConfig {
  final String publishableKey;
  final String? merchantId;
  final bool applePay;
  final bool googlePay;
  final String merchantCountry;

  StripeConfig({
    required this.publishableKey,
    this.merchantId,
    this.applePay = false,
    this.googlePay = false,
    this.merchantCountry = 'YE',
  });

  factory StripeConfig.fromJson(Map<String, dynamic> json) {
    return StripeConfig(
      publishableKey: json['publishable_key'] ?? '',
      merchantId: json['merchant_id'],
      applePay: json['apple_pay'] ?? false,
      googlePay: json['google_pay'] ?? false,
      merchantCountry: json['merchant_country'] ?? 'YE',
    );
  }
}

/// Stripe PaymentIntent response
/// نية الدفع من Stripe
///
/// Contains the client_secret needed to confirm payment with Stripe SDK.
/// The client_secret should NEVER be logged or transmitted outside the device.
class StripePaymentIntent {
  /// Unique identifier for the PaymentIntent
  final String id;

  /// Client secret for confirming payment with Stripe SDK
  /// This is a sensitive value - never log or transmit it
  final String clientSecret;

  /// Amount in smallest currency unit (cents for USD)
  final int amount;

  /// Three-letter ISO currency code
  final String currency;

  /// Status of the PaymentIntent
  /// Values: requires_payment_method, requires_confirmation,
  /// requires_action, processing, succeeded, canceled
  final String status;

  /// Associated Stripe Customer ID if any
  final String? customerId;

  /// Ephemeral key for Stripe SDK (if applicable)
  final String? ephemeralKey;

  StripePaymentIntent({
    required this.id,
    required this.clientSecret,
    required this.amount,
    required this.currency,
    required this.status,
    this.customerId,
    this.ephemeralKey,
  });

  factory StripePaymentIntent.fromJson(Map<String, dynamic> json) {
    return StripePaymentIntent(
      id: json['id'] ?? json['payment_intent_id'] ?? '',
      clientSecret: json['client_secret'] ?? '',
      amount: json['amount'] ?? 0,
      currency: json['currency'] ?? 'usd',
      status: json['status'] ?? 'requires_payment_method',
      customerId: json['customer_id'],
      ephemeralKey: json['ephemeral_key'],
    );
  }

  /// Check if payment requires further action (like 3D Secure)
  bool get requiresAction => status == 'requires_action';

  /// Check if payment was successful
  bool get succeeded => status == 'succeeded';

  /// Check if payment is still processing
  bool get isProcessing => status == 'processing';
}

/// Stripe SetupIntent response
/// نية الإعداد من Stripe
///
/// Used for saving payment methods without charging.
class StripeSetupIntent {
  /// Unique identifier for the SetupIntent
  final String id;

  /// Client secret for confirming setup with Stripe SDK
  final String clientSecret;

  /// Status of the SetupIntent
  final String status;

  /// Associated Stripe Customer ID
  final String? customerId;

  /// Ephemeral key for Stripe SDK
  final String? ephemeralKey;

  /// Payment method ID once attached
  final String? paymentMethodId;

  StripeSetupIntent({
    required this.id,
    required this.clientSecret,
    required this.status,
    this.customerId,
    this.ephemeralKey,
    this.paymentMethodId,
  });

  factory StripeSetupIntent.fromJson(Map<String, dynamic> json) {
    return StripeSetupIntent(
      id: json['id'] ?? json['setup_intent_id'] ?? '',
      clientSecret: json['client_secret'] ?? '',
      status: json['status'] ?? 'requires_payment_method',
      customerId: json['customer_id'],
      ephemeralKey: json['ephemeral_key'],
      paymentMethodId: json['payment_method_id'],
    );
  }

  /// Check if setup was successful
  bool get succeeded => status == 'succeeded';
}

/// Result of confirming a SetupIntent
/// نتيجة تأكيد نية الإعداد
class SetupIntentResult {
  final bool success;
  final String? paymentMethodId;
  final String? last4;
  final String? brand;
  final String? message;
  final String? messageAr;

  SetupIntentResult({
    required this.success,
    this.paymentMethodId,
    this.last4,
    this.brand,
    this.message,
    this.messageAr,
  });

  factory SetupIntentResult.fromJson(Map<String, dynamic> json) {
    final paymentMethod = json['payment_method'] as Map<String, dynamic>?;
    return SetupIntentResult(
      success: json['success'] ?? false,
      paymentMethodId: paymentMethod?['id'] ?? json['payment_method_id'],
      last4: paymentMethod?['last4'] ?? json['last4'],
      brand: paymentMethod?['brand'] ?? json['brand'],
      message: json['message'],
      messageAr: json['message_ar'],
    );
  }
}

/// Saved payment method
/// طريقة الدفع المحفوظة
class SavedPaymentMethod {
  final String id;
  final String type; // 'card', 'bank_account'
  final String? last4;
  final String? brand; // 'visa', 'mastercard', etc.
  final int? expMonth;
  final int? expYear;
  final bool isDefault;
  final DateTime createdAt;

  SavedPaymentMethod({
    required this.id,
    required this.type,
    this.last4,
    this.brand,
    this.expMonth,
    this.expYear,
    this.isDefault = false,
    required this.createdAt,
  });

  factory SavedPaymentMethod.fromJson(Map<String, dynamic> json) {
    final card = json['card'] as Map<String, dynamic>?;
    return SavedPaymentMethod(
      id: json['id'] ?? '',
      type: json['type'] ?? 'card',
      last4: card?['last4'] ?? json['last4'],
      brand: card?['brand'] ?? json['brand'],
      expMonth: card?['exp_month'] ?? json['exp_month'],
      expYear: card?['exp_year'] ?? json['exp_year'],
      isDefault: json['is_default'] ?? false,
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }

  /// Display string for the card (e.g., "Visa ****1234")
  String get displayName {
    if (type == 'card' && brand != null && last4 != null) {
      return '${brand!.toUpperCase()} ****$last4';
    }
    return last4 ?? 'Unknown';
  }

  /// Check if card is expired
  bool get isExpired {
    if (expMonth == null || expYear == null) return false;
    final now = DateTime.now();
    final expDate = DateTime(expYear!, expMonth! + 1, 0); // Last day of exp month
    return now.isAfter(expDate);
  }
}

/// Exception class
class ApiException implements Exception {
  final String code;
  final String message;

  ApiException({required this.code, required this.message});

  @override
  String toString() => 'ApiException($code): $message';
}
