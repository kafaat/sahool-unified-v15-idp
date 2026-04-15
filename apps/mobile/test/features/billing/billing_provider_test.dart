import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/billing/presentation/providers/billing_provider.dart';

void main() {
  group('BillingState', () {
    test('should have correct default values', () {
      const state = BillingState();
      expect(state.isLoading, false);
      expect(state.currentPlan, isNull);
      expect(state.invoices, isEmpty);
      expect(state.paymentHistory, isEmpty);
      expect(state.error, isNull);
    });

    test('copyWith should preserve values when not specified', () {
      const state = BillingState(isLoading: true);
      final copy = state.copyWith();
      expect(copy.isLoading, true);
    });

    test('copyWith should update specified values', () {
      const state = BillingState();
      final copy = state.copyWith(isLoading: true, error: 'فشل الاتصال');
      expect(copy.isLoading, true);
      expect(copy.error, 'فشل الاتصال');
    });
  });

  group('PlanTier', () {
    test('should have all expected tiers', () {
      expect(PlanTier.values, hasLength(3));
      expect(PlanTier.values, contains(PlanTier.starter));
      expect(PlanTier.values, contains(PlanTier.professional));
      expect(PlanTier.values, contains(PlanTier.enterprise));
    });
  });

  group('InvoiceStatus', () {
    test('should have all expected statuses', () {
      expect(InvoiceStatus.values, contains(InvoiceStatus.paid));
      expect(InvoiceStatus.values, contains(InvoiceStatus.pending));
      expect(InvoiceStatus.values, contains(InvoiceStatus.overdue));
    });
  });

  group('BillingPlan', () {
    test('should create plan with all fields', () {
      const plan = BillingPlan(
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
        features: ['Up to 5 fields'],
        featuresAr: ['حتى 5 حقول'],
      );

      expect(plan.name, 'Starter');
      expect(plan.nameAr, 'المبتدئ');
      expect(plan.priceMonthly, 29.0);
      expect(plan.fieldsLimit, 5);
    });
  });

  group('BillingInvoice', () {
    test('should create invoice with all fields', () {
      final invoice = BillingInvoice(
        id: 'inv_001',
        invoiceNumber: 'INV-2026-001',
        amount: 79.0,
        currency: 'USD',
        status: InvoiceStatus.paid,
        issueDate: DateTime(2026, 3, 1),
        dueDate: DateTime(2026, 3, 31),
        description: 'Professional Plan - March 2026',
        descriptionAr: 'الخطة المحترفة - مارس 2026',
      );

      expect(invoice.invoiceNumber, 'INV-2026-001');
      expect(invoice.amount, 79.0);
      expect(invoice.status, InvoiceStatus.paid);
    });
  });

  group('BillingNotifier', () {
    test('should initialize with default state', () {
      final notifier = BillingNotifier();
      // Access internal state through public API
      expect(notifier.state.isLoading, false);
      expect(notifier.state.currentPlan, isNull);
    });
  });
}
