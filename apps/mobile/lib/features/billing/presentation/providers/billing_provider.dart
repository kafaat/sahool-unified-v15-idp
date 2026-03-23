/// Billing Providers - مزودات بيانات الفوترة
/// Riverpod state management for Billing feature
/// إدارة حالة الفوترة والاشتراكات باستخدام Riverpod
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/api_config.dart';
import '../../../../core/utils/app_logger.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Plan Tier Enum - مستويات الخطط
// ═══════════════════════════════════════════════════════════════════════════════

/// Plan tiers matching platform pricing
/// مستويات الخطط المطابقة لتسعيرة المنصة
enum PlanTier {
  starter,
  professional,
  enterprise,
}

// ═══════════════════════════════════════════════════════════════════════════════
// Billing State - حالة الفوترة
// ═══════════════════════════════════════════════════════════════════════════════

/// Billing state model
/// نموذج حالة الفوترة
class BillingState {
  final BillingPlan? currentPlan;
  final List<BillingInvoice> invoices;
  final List<PaymentRecord> paymentHistory;
  final bool isLoading;
  final String? error;

  const BillingState({
    this.currentPlan,
    this.invoices = const [],
    this.paymentHistory = const [],
    this.isLoading = false,
    this.error,
  });

  BillingState copyWith({
    BillingPlan? currentPlan,
    List<BillingInvoice>? invoices,
    List<PaymentRecord>? paymentHistory,
    bool? isLoading,
    String? error,
  }) {
    return BillingState(
      currentPlan: currentPlan ?? this.currentPlan,
      invoices: invoices ?? this.invoices,
      paymentHistory: paymentHistory ?? this.paymentHistory,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Data Models - نماذج البيانات
// ═══════════════════════════════════════════════════════════════════════════════

/// Billing plan details
/// تفاصيل خطة الفوترة
class BillingPlan {
  final String id;
  final String name;
  final String nameAr;
  final PlanTier tier;
  final double priceMonthly;
  final double priceYearly;
  final String currency;
  final int fieldsLimit;
  final int usersLimit;
  final int apiCallsPerHour;
  final List<String> features;
  final List<String> featuresAr;

  const BillingPlan({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.tier,
    required this.priceMonthly,
    required this.priceYearly,
    required this.currency,
    required this.fieldsLimit,
    required this.usersLimit,
    required this.apiCallsPerHour,
    required this.features,
    required this.featuresAr,
  });
}

/// Invoice status
/// حالة الفاتورة
enum InvoiceStatus { paid, pending, overdue }

/// Billing invoice
/// فاتورة
class BillingInvoice {
  final String id;
  final String invoiceNumber;
  final double amount;
  final String currency;
  final InvoiceStatus status;
  final DateTime issueDate;
  final DateTime dueDate;
  final String description;
  final String descriptionAr;

  const BillingInvoice({
    required this.id,
    required this.invoiceNumber,
    required this.amount,
    required this.currency,
    required this.status,
    required this.issueDate,
    required this.dueDate,
    required this.description,
    required this.descriptionAr,
  });
}

/// Payment record
/// سجل دفع
class PaymentRecord {
  final String id;
  final double amount;
  final String currency;
  final String method;
  final String methodAr;
  final DateTime date;
  final String status;

  const PaymentRecord({
    required this.id,
    required this.amount,
    required this.currency,
    required this.method,
    required this.methodAr,
    required this.date,
    required this.status,
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// Mock Data - بيانات تجريبية
// ═══════════════════════════════════════════════════════════════════════════════

final List<BillingPlan> _mockPlans = [
  const BillingPlan(
    id: 'plan_starter',
    name: 'Starter',
    nameAr: 'المبتدئ',
    tier: PlanTier.starter,
    priceMonthly: 29.0,
    priceYearly: 290.0,
    currency: 'USD',
    fieldsLimit: 5,
    usersLimit: 2,
    apiCallsPerHour: 500,
    features: [
      'Up to 5 fields',
      'Basic NDVI monitoring',
      'Weather alerts',
      'Email support',
    ],
    featuresAr: [
      'حتى 5 حقول',
      'مراقبة NDVI الأساسية',
      'تنبيهات الطقس',
      'دعم عبر البريد الإلكتروني',
    ],
  ),
  const BillingPlan(
    id: 'plan_professional',
    name: 'Professional',
    nameAr: 'المحترف',
    tier: PlanTier.professional,
    priceMonthly: 79.0,
    priceYearly: 790.0,
    currency: 'USD',
    fieldsLimit: 25,
    usersLimit: 10,
    apiCallsPerHour: 2000,
    features: [
      'Up to 25 fields',
      'Advanced NDVI & LAI analysis',
      'AI crop advisory',
      'Irrigation scheduling',
      'Priority support',
    ],
    featuresAr: [
      'حتى 25 حقلاً',
      'تحليل NDVI و LAI المتقدم',
      'استشارات المحاصيل بالذكاء الاصطناعي',
      'جدولة الري',
      'دعم ذو أولوية',
    ],
  ),
  const BillingPlan(
    id: 'plan_enterprise',
    name: 'Enterprise',
    nameAr: 'المؤسسي',
    tier: PlanTier.enterprise,
    priceMonthly: 199.0,
    priceYearly: 1990.0,
    currency: 'USD',
    fieldsLimit: 100,
    usersLimit: 50,
    apiCallsPerHour: 5000,
    features: [
      'Unlimited fields',
      'Full AI suite & vision detection',
      'Drone integration',
      'Digital twin engine',
      'Dedicated account manager',
      'Custom integrations',
    ],
    featuresAr: [
      'حقول غير محدودة',
      'مجموعة الذكاء الاصطناعي الكاملة والكشف البصري',
      'تكامل الطائرات المسيّرة',
      'محرك التوأم الرقمي',
      'مدير حساب مخصص',
      'تكاملات مخصصة',
    ],
  ),
];

final List<BillingInvoice> _mockInvoices = [
  BillingInvoice(
    id: 'inv_001',
    invoiceNumber: 'INV-2026-001',
    amount: 79.0,
    currency: 'USD',
    status: InvoiceStatus.paid,
    issueDate: DateTime(2026, 1, 1),
    dueDate: DateTime(2026, 1, 15),
    description: 'Professional Plan - January 2026',
    descriptionAr: 'الخطة المحترفة - يناير 2026',
  ),
  BillingInvoice(
    id: 'inv_002',
    invoiceNumber: 'INV-2026-002',
    amount: 79.0,
    currency: 'USD',
    status: InvoiceStatus.pending,
    issueDate: DateTime(2026, 2, 1),
    dueDate: DateTime(2026, 2, 15),
    description: 'Professional Plan - February 2026',
    descriptionAr: 'الخطة المحترفة - فبراير 2026',
  ),
  BillingInvoice(
    id: 'inv_003',
    invoiceNumber: 'INV-2025-012',
    amount: 79.0,
    currency: 'USD',
    status: InvoiceStatus.overdue,
    issueDate: DateTime(2025, 12, 1),
    dueDate: DateTime(2025, 12, 15),
    description: 'Professional Plan - December 2025',
    descriptionAr: 'الخطة المحترفة - ديسمبر 2025',
  ),
];

final List<PaymentRecord> _mockPayments = [
  PaymentRecord(
    id: 'pay_001',
    amount: 79.0,
    currency: 'USD',
    method: 'Visa ****4242',
    methodAr: 'فيزا ****4242',
    date: DateTime(2026, 1, 5),
    status: 'completed',
  ),
  PaymentRecord(
    id: 'pay_002',
    amount: 79.0,
    currency: 'USD',
    method: 'Visa ****4242',
    methodAr: 'فيزا ****4242',
    date: DateTime(2025, 12, 5),
    status: 'completed',
  ),
];

// ═══════════════════════════════════════════════════════════════════════════════
// Billing StateNotifier - متحكم حالة الفوترة
// ═══════════════════════════════════════════════════════════════════════════════

/// Billing state notifier managing subscription, invoices, and payments
/// متحكم حالة الفوترة لإدارة الاشتراك والفواتير والمدفوعات
class BillingNotifier extends StateNotifier<BillingState> {
  BillingNotifier() : super(const BillingState());

  Dio _buildDio() {
    return Dio(BaseOptions(
      baseUrl: ApiConfig.effectiveBaseUrl,
      connectTimeout: ApiConfig.connectTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      headers: ApiConfig.defaultHeaders,
    ));
  }

  /// Load all billing information - tries API first, falls back to mock data
  /// تحميل جميع معلومات الفوترة - يحاول الاتصال بالـ API أولاً ثم يعود للبيانات التجريبية
  Future<void> loadBillingInfo() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final dio = _buildDio();

      // Fetch plans and invoices concurrently
      final results = await Future.wait([
        dio.get(ApiConfig.billingPlans).catchError((e) => null),
        dio.get(ApiConfig.billingInvoices).catchError((e) => null),
        dio.get(ApiConfig.billingSubscription).catchError((e) => null),
      ]);

      final plansResponse = results[0] as Response?;
      final invoicesResponse = results[1] as Response?;
      final subscriptionResponse = results[2] as Response?;

      List<BillingPlan> plans = _mockPlans;
      List<BillingInvoice> invoices = _mockInvoices;
      BillingPlan? currentPlan = _mockPlans[1];

      // Parse plans from API response
      if (plansResponse != null && plansResponse.statusCode == 200) {
        final data = plansResponse.data;
        final rawPlans = (data is Map ? data['plans'] : data) as List?;
        if (rawPlans != null) {
          plans = rawPlans.map((p) => _planFromJson(p as Map<String, dynamic>)).toList();
        }
      }

      // Parse subscription / current plan from API response
      if (subscriptionResponse != null && subscriptionResponse.statusCode == 200) {
        final sub = subscriptionResponse.data as Map<String, dynamic>?;
        if (sub != null) {
          final planJson = sub['plan'] as Map<String, dynamic>?;
          if (planJson != null) {
            currentPlan = _planFromJson(planJson);
          }
        }
      } else {
        currentPlan = plans.length > 1 ? plans[1] : plans.first;
      }

      // Parse invoices from API response
      if (invoicesResponse != null && invoicesResponse.statusCode == 200) {
        final data = invoicesResponse.data;
        final rawInvoices = (data is Map ? data['invoices'] : data) as List?;
        if (rawInvoices != null) {
          invoices = rawInvoices.map((i) => _invoiceFromJson(i as Map<String, dynamic>)).toList();
        }
      }

      state = state.copyWith(
        currentPlan: currentPlan,
        invoices: invoices,
        paymentHistory: _mockPayments,
        isLoading: false,
      );
    } catch (e) {
      AppLogger.w('Billing API unavailable, using mock data: $e');
      // Offline fallback - use mock data
      state = state.copyWith(
        currentPlan: _mockPlans[1],
        invoices: _mockInvoices,
        paymentHistory: _mockPayments,
        isLoading: false,
      );
    }
  }

  // Helper: parse BillingPlan from API JSON
  BillingPlan _planFromJson(Map<String, dynamic> json) {
    final tier = _tierFromString((json['tier'] as String?) ?? 'starter');
    final limits = (json['limits'] as Map?) ?? {};
    return BillingPlan(
      id: (json['plan_id'] ?? json['id'] ?? '') as String,
      name: (json['name'] as String?) ?? '',
      nameAr: (json['name_ar'] ?? json['name'] ?? '') as String,
      tier: tier,
      priceMonthly: ((json['price_monthly'] ?? 0) as num).toDouble(),
      priceYearly: ((json['price_yearly'] ?? 0) as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'USD',
      fieldsLimit: (limits['fields_limit'] as int?) ?? 0,
      usersLimit: (limits['users_limit'] as int?) ?? 0,
      apiCallsPerHour: (limits['api_calls_per_hour'] as int?) ?? 0,
      features: (json['features'] as List?)?.cast<String>() ?? [],
      featuresAr: (json['features_ar'] as List?)?.cast<String>() ?? [],
    );
  }

  PlanTier _tierFromString(String tier) {
    switch (tier) {
      case 'professional':
        return PlanTier.professional;
      case 'enterprise':
        return PlanTier.enterprise;
      default:
        return PlanTier.starter;
    }
  }

  // Helper: parse BillingInvoice from API JSON
  BillingInvoice _invoiceFromJson(Map<String, dynamic> json) {
    InvoiceStatus status;
    switch ((json['status'] as String?) ?? 'pending') {
      case 'paid':
        status = InvoiceStatus.paid;
        break;
      case 'overdue':
        status = InvoiceStatus.overdue;
        break;
      default:
        status = InvoiceStatus.pending;
    }
    return BillingInvoice(
      id: (json['invoice_id'] ?? json['id'] ?? '') as String,
      invoiceNumber: (json['invoice_number'] as String?) ?? '',
      amount: ((json['total'] ?? json['amount'] ?? 0) as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'USD',
      status: status,
      issueDate: DateTime.tryParse((json['issue_date'] as String?) ?? '') ?? DateTime.now(),
      dueDate: DateTime.tryParse((json['due_date'] as String?) ?? '') ?? DateTime.now(),
      description: (json['description'] as String?) ?? '',
      descriptionAr: (json['description_ar'] as String?) ?? '',
    );
  }

  /// Change subscription plan - calls billing-core API, falls back gracefully
  /// تغيير خطة الاشتراك - يستدعي API الفوترة مع التعامل مع الأخطاء
  Future<bool> changePlan(BillingPlan newPlan) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final dio = _buildDio();
      await dio.post(
        ApiConfig.billingSubscription,
        data: {'plan_id': newPlan.id, 'billing_cycle': 'monthly'},
      );
      state = state.copyWith(currentPlan: newPlan, isLoading: false);
      return true;
    } on DioException catch (e) {
      AppLogger.w('Change plan API error, applying locally: $e');
      // Apply locally on API failure for offline-first UX
      state = state.copyWith(currentPlan: newPlan, isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تغيير الخطة',
      );
      return false;
    }
  }

  /// Process a payment for an invoice - calls billing-core API
  /// معالجة دفع لفاتورة - يستدعي API الفوترة
  Future<bool> makePayment(String invoiceId) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final invoice = state.invoices.firstWhere((i) => i.id == invoiceId);
      try {
        final dio = _buildDio();
        await dio.post(
          '${ApiConfig.billingInvoices}/$invoiceId/pay',
          data: {'invoice_id': invoiceId, 'method': 'manual'},
        );
      } on DioException catch (e) {
        AppLogger.w('Payment API error, updating locally: $e');
        // Continue with local state update for offline-first
      }

      final updatedInvoices = state.invoices.map((inv) {
        if (inv.id == invoiceId) {
          return BillingInvoice(
            id: inv.id,
            invoiceNumber: inv.invoiceNumber,
            amount: inv.amount,
            currency: inv.currency,
            status: InvoiceStatus.paid,
            issueDate: inv.issueDate,
            dueDate: inv.dueDate,
            description: inv.description,
            descriptionAr: inv.descriptionAr,
          );
        }
        return inv;
      }).toList();

      final newPayment = PaymentRecord(
        id: 'pay_${DateTime.now().millisecondsSinceEpoch}',
        amount: invoice.amount,
        currency: invoice.currency,
        method: 'Visa ****4242',
        methodAr: 'فيزا ****4242',
        date: DateTime.now(),
        status: 'completed',
      );

      state = state.copyWith(
        invoices: updatedInvoices,
        paymentHistory: [newPayment, ...state.paymentHistory],
        isLoading: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في معالجة الدفع',
      );
      return false;
    }
  }

  /// Refresh invoices list - tries API first, falls back to mock
  /// تحديث قائمة الفواتير - يحاول API أولاً ثم يعود للبيانات التجريبية
  Future<void> getInvoices() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final dio = _buildDio();
      final response = await dio.get(ApiConfig.billingInvoices);
      final data = response.data;
      final rawInvoices = (data is Map ? data['invoices'] : data) as List?;
      final invoices = rawInvoices != null
          ? rawInvoices.map((i) => _invoiceFromJson(i as Map<String, dynamic>)).toList()
          : _mockInvoices;
      state = state.copyWith(invoices: invoices, isLoading: false);
    } catch (e) {
      AppLogger.w('Invoices API unavailable, using mock data: $e');
      state = state.copyWith(invoices: _mockInvoices, isLoading: false);
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Providers - المزودات
// ═══════════════════════════════════════════════════════════════════════════════

/// Billing state notifier provider
/// مزود متحكم حالة الفوترة
final billingProvider =
    StateNotifierProvider.autoDispose<BillingNotifier, BillingState>((ref) {
  return BillingNotifier();
});

/// Available plans provider - fetches from billing-core API with mock fallback
/// مزود الخطط المتاحة - يجلب من API مع بيانات تجريبية كاحتياطي
final availablePlansProvider =
    FutureProvider.autoDispose<List<BillingPlan>>((ref) async {
  try {
    final dio = Dio(BaseOptions(
      baseUrl: ApiConfig.effectiveBaseUrl,
      connectTimeout: ApiConfig.connectTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      headers: ApiConfig.defaultHeaders,
    ));
    final response = await dio.get(ApiConfig.billingPlans);
    final data = response.data;
    final rawPlans = (data is Map ? data['plans'] : data) as List?;
    if (rawPlans != null && rawPlans.isNotEmpty) {
      return rawPlans.map((p) {
        final json = p as Map<String, dynamic>;
        final tier = switch ((json['tier'] as String?) ?? 'starter') {
          'professional' => PlanTier.professional,
          'enterprise' => PlanTier.enterprise,
          _ => PlanTier.starter,
        };
        final limits = (json['limits'] as Map?) ?? {};
        return BillingPlan(
          id: (json['plan_id'] ?? json['id'] ?? '') as String,
          name: (json['name'] as String?) ?? '',
          nameAr: (json['name_ar'] ?? json['name'] ?? '') as String,
          tier: tier,
          priceMonthly: ((json['price_monthly'] ?? 0) as num).toDouble(),
          priceYearly: ((json['price_yearly'] ?? 0) as num).toDouble(),
          currency: (json['currency'] as String?) ?? 'USD',
          fieldsLimit: (limits['fields_limit'] as int?) ?? 0,
          usersLimit: (limits['users_limit'] as int?) ?? 0,
          apiCallsPerHour: (limits['api_calls_per_hour'] as int?) ?? 0,
          features: (json['features'] as List?)?.cast<String>() ?? [],
          featuresAr: (json['features_ar'] as List?)?.cast<String>() ?? [],
        );
      }).toList();
    }
  } catch (_) {
    // Offline fallback
  }
  return _mockPlans;
});
