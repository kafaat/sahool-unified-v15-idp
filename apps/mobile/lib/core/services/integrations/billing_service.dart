/// SAHOOL Billing Service Integration
/// تكامل خدمة الفوترة
///
/// Handles billing-related operations:
/// - Wallet management
/// - Transactions
/// - Subscriptions
/// - Invoices
/// - Usage tracking
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../network/api_result.dart';
import '../service_connector.dart';

/// Wallet model
class Wallet {
  final String id;
  final String userId;
  final double balance;
  final String currency;
  final String? status;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final Map<String, dynamic>? metadata;

  const Wallet({
    required this.id,
    required this.userId,
    required this.balance,
    required this.currency,
    this.status,
    required this.createdAt,
    this.updatedAt,
    this.metadata,
  });

  factory Wallet.fromJson(Map<String, dynamic> json) {
    return Wallet(
      id: json['id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      balance: (json['balance'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'SAR',
      status: json['status'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      updatedAt:
          json['updated_at'] != null ? DateTime.tryParse(json['updated_at'] as String) : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

/// Transaction model
class BillingTransaction {
  final String id;
  final String type;
  final double amount;
  final String currency;
  final String status;
  final String? description;
  final String? descriptionAr;
  final String? reference;
  final DateTime createdAt;
  final DateTime? completedAt;
  final Map<String, dynamic>? metadata;

  const BillingTransaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.currency,
    required this.status,
    this.description,
    this.descriptionAr,
    this.reference,
    required this.createdAt,
    this.completedAt,
    this.metadata,
  });

  factory BillingTransaction.fromJson(Map<String, dynamic> json) {
    return BillingTransaction(
      id: json['id'] as String? ?? '',
      type: json['type'] as String? ?? '',
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'SAR',
      status: json['status'] as String? ?? 'pending',
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      reference: json['reference'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      completedAt:
          json['completed_at'] != null ? DateTime.tryParse(json['completed_at'] as String) : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  bool get isCredit => type == 'deposit' || type == 'credit' || type == 'refund';
  bool get isDebit => type == 'withdraw' || type == 'debit' || type == 'payment';
}

/// Subscription model
class Subscription {
  final String id;
  final String planId;
  final String planName;
  final String? planNameAr;
  final String status;
  final DateTime startDate;
  final DateTime? endDate;
  final DateTime? nextBillingDate;
  final double amount;
  final String currency;
  final String billingCycle;
  final bool autoRenew;
  final Map<String, dynamic>? features;
  final Map<String, dynamic>? limits;

  const Subscription({
    required this.id,
    required this.planId,
    required this.planName,
    this.planNameAr,
    required this.status,
    required this.startDate,
    this.endDate,
    this.nextBillingDate,
    required this.amount,
    required this.currency,
    required this.billingCycle,
    this.autoRenew = true,
    this.features,
    this.limits,
  });

  factory Subscription.fromJson(Map<String, dynamic> json) {
    return Subscription(
      id: json['id'] as String? ?? '',
      planId: json['plan_id'] as String? ?? '',
      planName: json['plan_name'] as String? ?? '',
      planNameAr: json['plan_name_ar'] as String?,
      status: json['status'] as String? ?? 'inactive',
      startDate: json['start_date'] != null
          ? DateTime.tryParse(json['start_date'] as String) ?? DateTime.now()
          : DateTime.now(),
      endDate: json['end_date'] != null ? DateTime.tryParse(json['end_date'] as String) : null,
      nextBillingDate: json['next_billing_date'] != null
          ? DateTime.tryParse(json['next_billing_date'] as String)
          : null,
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'SAR',
      billingCycle: json['billing_cycle'] as String? ?? 'monthly',
      autoRenew: json['auto_renew'] as bool? ?? true,
      features: json['features'] as Map<String, dynamic>?,
      limits: json['limits'] as Map<String, dynamic>?,
    );
  }

  bool get isActive => status == 'active';
  bool get isExpired => endDate != null && endDate!.isBefore(DateTime.now());
}

/// Subscription plan model
class SubscriptionPlan {
  final String id;
  final String name;
  final String? nameAr;
  final String? description;
  final String? descriptionAr;
  final double monthlyPrice;
  final double? yearlyPrice;
  final String currency;
  final Map<String, dynamic>? features;
  final Map<String, dynamic>? limits;
  final bool isPopular;
  final int? trialDays;

  const SubscriptionPlan({
    required this.id,
    required this.name,
    this.nameAr,
    this.description,
    this.descriptionAr,
    required this.monthlyPrice,
    this.yearlyPrice,
    required this.currency,
    this.features,
    this.limits,
    this.isPopular = false,
    this.trialDays,
  });

  factory SubscriptionPlan.fromJson(Map<String, dynamic> json) {
    return SubscriptionPlan(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      monthlyPrice: (json['monthly_price'] as num?)?.toDouble() ?? 0.0,
      yearlyPrice: (json['yearly_price'] as num?)?.toDouble(),
      currency: json['currency'] as String? ?? 'SAR',
      features: json['features'] as Map<String, dynamic>?,
      limits: json['limits'] as Map<String, dynamic>?,
      isPopular: json['is_popular'] as bool? ?? false,
      trialDays: (json['trial_days'] as num?)?.toInt(),
    );
  }

  double get yearlyDiscount {
    if (yearlyPrice == null) return 0;
    final monthlyTotal = monthlyPrice * 12;
    return ((monthlyTotal - yearlyPrice!) / monthlyTotal) * 100;
  }
}

/// Invoice model
class Invoice {
  final String id;
  final String? subscriptionId;
  final double amount;
  final double? tax;
  final double total;
  final String currency;
  final String status;
  final DateTime issueDate;
  final DateTime dueDate;
  final DateTime? paidAt;
  final String? invoiceNumber;
  final List<InvoiceItem>? items;
  final String? pdfUrl;

  const Invoice({
    required this.id,
    this.subscriptionId,
    required this.amount,
    this.tax,
    required this.total,
    required this.currency,
    required this.status,
    required this.issueDate,
    required this.dueDate,
    this.paidAt,
    this.invoiceNumber,
    this.items,
    this.pdfUrl,
  });

  factory Invoice.fromJson(Map<String, dynamic> json) {
    return Invoice(
      id: json['id'] as String? ?? '',
      subscriptionId: json['subscription_id'] as String?,
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      tax: (json['tax'] as num?)?.toDouble(),
      total: (json['total'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'SAR',
      status: json['status'] as String? ?? 'pending',
      issueDate: json['issue_date'] != null
          ? DateTime.tryParse(json['issue_date'] as String) ?? DateTime.now()
          : DateTime.now(),
      dueDate:
          json['due_date'] != null ? DateTime.tryParse(json['due_date'] as String) ?? DateTime.now() : DateTime.now(),
      paidAt: json['paid_at'] != null ? DateTime.tryParse(json['paid_at'] as String) : null,
      invoiceNumber: json['invoice_number'] as String?,
      items: (json['items'] as List?)
          ?.map((e) => InvoiceItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      pdfUrl: json['pdf_url'] as String?,
    );
  }

  bool get isPaid => status == 'paid';
  bool get isOverdue => status != 'paid' && dueDate.isBefore(DateTime.now());
}

/// Invoice item model
class InvoiceItem {
  final String description;
  final String? descriptionAr;
  final int quantity;
  final double unitPrice;
  final double total;

  const InvoiceItem({
    required this.description,
    this.descriptionAr,
    required this.quantity,
    required this.unitPrice,
    required this.total,
  });

  factory InvoiceItem.fromJson(Map<String, dynamic> json) {
    return InvoiceItem(
      description: json['description'] as String? ?? '',
      descriptionAr: json['description_ar'] as String?,
      quantity: (json['quantity'] as num?)?.toInt() ?? 1,
      unitPrice: (json['unit_price'] as num?)?.toDouble() ?? 0.0,
      total: (json['total'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

/// Usage summary model
class UsageSummary {
  final String period;
  final DateTime startDate;
  final DateTime endDate;
  final Map<String, UsageMetric> metrics;
  final double totalCost;
  final String currency;

  const UsageSummary({
    required this.period,
    required this.startDate,
    required this.endDate,
    required this.metrics,
    required this.totalCost,
    required this.currency,
  });

  factory UsageSummary.fromJson(Map<String, dynamic> json) {
    final metricsJson = json['metrics'] as Map<String, dynamic>? ?? {};
    return UsageSummary(
      period: json['period'] as String? ?? '',
      startDate: json['start_date'] != null
          ? DateTime.tryParse(json['start_date'] as String) ?? DateTime.now()
          : DateTime.now(),
      endDate:
          json['end_date'] != null ? DateTime.tryParse(json['end_date'] as String) ?? DateTime.now() : DateTime.now(),
      metrics: metricsJson.map(
        (key, value) => MapEntry(key, UsageMetric.fromJson(value as Map<String, dynamic>)),
      ),
      totalCost: (json['total_cost'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'SAR',
    );
  }
}

/// Usage metric model
class UsageMetric {
  final String name;
  final String? nameAr;
  final int used;
  final int? limit;
  final String unit;
  final double? cost;

  const UsageMetric({
    required this.name,
    this.nameAr,
    required this.used,
    this.limit,
    required this.unit,
    this.cost,
  });

  factory UsageMetric.fromJson(Map<String, dynamic> json) {
    return UsageMetric(
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      used: (json['used'] as num?)?.toInt() ?? 0,
      limit: (json['limit'] as num?)?.toInt(),
      unit: json['unit'] as String? ?? '',
      cost: (json['cost'] as num?)?.toDouble(),
    );
  }

  double get usagePercentage {
    if (limit == null || limit == 0) return 0;
    return (used / limit!) * 100;
  }

  bool get isNearLimit => usagePercentage >= 80;
  bool get isOverLimit => limit != null && used > limit!;
}

/// Billing Service Connector
/// موصل خدمة الفوترة
class BillingServiceConnector extends ServiceConnector {
  BillingServiceConnector({required super.ref}) : super(serviceId: 'billing');

  // ═══════════════════════════════════════════════════════════════════════════════
  // Wallet Operations
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Get wallet
  /// الحصول على المحفظة
  Future<ApiResult<Wallet>> getWallet() async {
    return get(
      getEndpoint('wallet') ?? '/api/v1/billing/wallet',
      parser: (data) => Wallet.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Deposit to wallet
  /// إيداع في المحفظة
  Future<ApiResult<BillingTransaction>> deposit({
    required double amount,
    required String paymentMethod,
    Map<String, dynamic>? paymentDetails,
  }) async {
    return post(
      getEndpoint('deposit') ?? '/api/v1/billing/wallet/deposit',
      data: {
        'amount': amount,
        'payment_method': paymentMethod,
        if (paymentDetails != null) 'payment_details': paymentDetails,
      },
      parser: (data) => BillingTransaction.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Withdraw from wallet
  /// سحب من المحفظة
  Future<ApiResult<BillingTransaction>> withdraw({
    required double amount,
    required String withdrawMethod,
    Map<String, dynamic>? withdrawDetails,
  }) async {
    return post(
      getEndpoint('withdraw') ?? '/api/v1/billing/wallet/withdraw',
      data: {
        'amount': amount,
        'withdraw_method': withdrawMethod,
        if (withdrawDetails != null) 'withdraw_details': withdrawDetails,
      },
      parser: (data) => BillingTransaction.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Transfer between wallets
  /// تحويل بين المحافظ
  Future<ApiResult<BillingTransaction>> transfer({
    required String recipientId,
    required double amount,
    String? description,
  }) async {
    return post(
      getEndpoint('transfer') ?? '/api/v1/billing/wallet/transfer',
      data: {
        'recipient_id': recipientId,
        'amount': amount,
        if (description != null) 'description': description,
      },
      parser: (data) => BillingTransaction.fromJson(data as Map<String, dynamic>),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Transaction Operations
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Get transactions
  /// الحصول على المعاملات
  Future<ApiResult<List<BillingTransaction>>> getTransactions({
    int? page,
    int? limit,
    String? type,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{
      if (page != null) 'page': page,
      if (limit != null) 'limit': limit,
      if (type != null) 'type': type,
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
    };

    return get(
      getEndpoint('transactions') ?? '/api/v1/billing/transactions',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => BillingTransaction.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['transactions'] != null) {
          return (data['transactions'] as List? ?? [])
              .map((e) => BillingTransaction.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <BillingTransaction>[];
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Subscription Operations
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Get current subscription
  /// الحصول على الاشتراك الحالي
  Future<ApiResult<Subscription?>> getCurrentSubscription() async {
    return get(
      getEndpoint('subscription') ?? '/api/v1/billing/subscription',
      parser: (data) {
        if (data == null || (data is Map && data.isEmpty)) return null;
        return Subscription.fromJson(data as Map<String, dynamic>);
      },
    );
  }

  /// Get available plans
  /// الحصول على الخطط المتاحة
  Future<ApiResult<List<SubscriptionPlan>>> getPlans() async {
    return get(
      getEndpoint('plans') ?? '/api/v1/billing/plans',
      parser: (data) {
        if (data is List) {
          return data.map((e) => SubscriptionPlan.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['plans'] != null) {
          return (data['plans'] as List? ?? [])
              .map((e) => SubscriptionPlan.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <SubscriptionPlan>[];
      },
    );
  }

  /// Subscribe to plan
  /// الاشتراك في خطة
  Future<ApiResult<Subscription>> subscribeToPlan({
    required String planId,
    String billingCycle = 'monthly',
    String? couponCode,
  }) async {
    return post(
      getEndpoint('subscription') ?? '/api/v1/billing/subscription',
      data: {
        'plan_id': planId,
        'billing_cycle': billingCycle,
        if (couponCode != null) 'coupon_code': couponCode,
      },
      parser: (data) => Subscription.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Cancel subscription
  /// إلغاء الاشتراك
  Future<ApiResult<bool>> cancelSubscription({
    String? reason,
    bool immediate = false,
  }) async {
    return delete(
      getEndpoint('subscription') ?? '/api/v1/billing/subscription',
      data: {
        if (reason != null) 'reason': reason,
        'immediate': immediate,
      },
      parser: (_) => true,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Invoice Operations
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Get invoices
  /// الحصول على الفواتير
  Future<ApiResult<List<Invoice>>> getInvoices({
    int? page,
    int? limit,
    String? status,
  }) async {
    final queryParams = <String, dynamic>{
      if (page != null) 'page': page,
      if (limit != null) 'limit': limit,
      if (status != null) 'status': status,
    };

    return get(
      getEndpoint('invoices') ?? '/api/v1/billing/invoices',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => Invoice.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['invoices'] != null) {
          return (data['invoices'] as List? ?? [])
              .map((e) => Invoice.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <Invoice>[];
      },
    );
  }

  /// Pay invoice
  /// دفع الفاتورة
  Future<ApiResult<Invoice>> payInvoice(String invoiceId) async {
    return post(
      '${getEndpoint('invoices') ?? '/api/v1/billing/invoices'}/$invoiceId/pay',
      parser: (data) => Invoice.fromJson(data as Map<String, dynamic>),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Usage Operations
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Get usage summary
  /// الحصول على ملخص الاستخدام
  Future<ApiResult<UsageSummary>> getUsage({
    String period = 'current',
  }) async {
    return get(
      getEndpoint('usage') ?? '/api/v1/billing/usage',
      queryParameters: {'period': period},
      parser: (data) => UsageSummary.fromJson(data as Map<String, dynamic>),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Billing Service Provider
final billingServiceProvider = Provider<BillingServiceConnector>((ref) {
  return BillingServiceConnector(ref: ref);
});

/// Wallet Provider
final walletProvider = FutureProvider<Wallet?>((ref) async {
  final service = ref.watch(billingServiceProvider);
  final result = await service.getWallet();
  return result.dataOrNull;
});

/// Wallet Balance Provider
final walletBalanceProvider = FutureProvider<double>((ref) async {
  final wallet = await ref.watch(walletProvider.future);
  return wallet?.balance ?? 0.0;
});

/// Transactions Provider
final transactionsProvider = FutureProvider<List<BillingTransaction>>((ref) async {
  final service = ref.watch(billingServiceProvider);
  final result = await service.getTransactions();
  return result.dataOrNull ?? [];
});

/// Current Subscription Provider
final currentSubscriptionProvider = FutureProvider<Subscription?>((ref) async {
  final service = ref.watch(billingServiceProvider);
  final result = await service.getCurrentSubscription();
  return result.dataOrNull;
});

/// Subscription Plans Provider
final subscriptionPlansProvider = FutureProvider<List<SubscriptionPlan>>((ref) async {
  final service = ref.watch(billingServiceProvider);
  final result = await service.getPlans();
  return result.dataOrNull ?? [];
});

/// Invoices Provider
final invoicesProvider = FutureProvider<List<Invoice>>((ref) async {
  final service = ref.watch(billingServiceProvider);
  final result = await service.getInvoices();
  return result.dataOrNull ?? [];
});

/// Unpaid Invoices Provider
final unpaidInvoicesProvider = FutureProvider<List<Invoice>>((ref) async {
  final service = ref.watch(billingServiceProvider);
  final result = await service.getInvoices(status: 'pending');
  return result.dataOrNull ?? [];
});

/// Usage Summary Provider
final usageSummaryProvider = FutureProvider<UsageSummary?>((ref) async {
  final service = ref.watch(billingServiceProvider);
  final result = await service.getUsage();
  return result.dataOrNull;
});

/// Has Active Subscription Provider
final hasActiveSubscriptionProvider = FutureProvider<bool>((ref) async {
  final subscription = await ref.watch(currentSubscriptionProvider.future);
  return subscription?.isActive ?? false;
});
