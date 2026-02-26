/// Billing Providers - مزودات بيانات الفوترة
/// Riverpod state management for Billing feature
/// إدارة حالة الفوترة والاشتراكات باستخدام Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

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

  /// Load all billing information
  /// تحميل جميع معلومات الفوترة
  Future<void> loadBillingInfo() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      // Simulate API call with mock data
      await Future<void>.delayed(const Duration(milliseconds: 600));
      state = state.copyWith(
        currentPlan: _mockPlans[1], // Professional
        invoices: _mockInvoices,
        paymentHistory: _mockPayments,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل بيانات الفوترة',
      );
    }
  }

  /// Change subscription plan
  /// تغيير خطة الاشتراك
  Future<bool> changePlan(BillingPlan newPlan) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await Future<void>.delayed(const Duration(milliseconds: 800));
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

  /// Process a payment for an invoice
  /// معالجة دفع لفاتورة
  Future<bool> makePayment(String invoiceId) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await Future<void>.delayed(const Duration(milliseconds: 800));
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
        amount: state.invoices.firstWhere((i) => i.id == invoiceId).amount,
        currency: 'USD',
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

  /// Refresh invoices list
  /// تحديث قائمة الفواتير
  Future<void> getInvoices() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await Future<void>.delayed(const Duration(milliseconds: 400));
      state = state.copyWith(
        invoices: _mockInvoices,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في جلب الفواتير',
      );
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

/// Available plans provider
/// مزود الخطط المتاحة
final availablePlansProvider = Provider.autoDispose<List<BillingPlan>>((ref) {
  return _mockPlans;
});
