/// Billing Screen - Subscription and Payment Management
/// شاشة الفوترة - إدارة الاشتراكات والمدفوعات
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../providers/billing_provider.dart';
import '../widgets/plan_card.dart';

/// Full billing management screen
/// شاشة إدارة الفوترة الكاملة
class BillingScreen extends ConsumerStatefulWidget {
  const BillingScreen({super.key});

  @override
  ConsumerState<BillingScreen> createState() => _BillingScreenState();
}

class _BillingScreenState extends ConsumerState<BillingScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    Future.microtask(() {
      ref.read(billingProvider.notifier).loadBillingInfo();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final billingState = ref.watch(billingProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الفوترة والاشتراكات'),
          backgroundColor: SahoolColors.forestGreen,
          foregroundColor: Colors.white,
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: const [
              Tab(text: 'الاشتراك', icon: Icon(Icons.card_membership)),
              Tab(text: 'الفواتير', icon: Icon(Icons.receipt_long)),
              Tab(text: 'المدفوعات', icon: Icon(Icons.payment)),
            ],
          ),
        ),
        body: billingState.isLoading
            ? const Center(child: CircularProgressIndicator())
            : RefreshIndicator(
                onRefresh: () async {
                  await ref.read(billingProvider.notifier).loadBillingInfo();
                },
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildSubscriptionTab(billingState),
                    _buildInvoicesTab(billingState),
                    _buildPaymentsTab(billingState),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildSubscriptionTab(BillingState state) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Current plan header
          _buildCurrentPlanHeader(state),
          const SizedBox(height: 24),

          // Usage stats
          Text(
            'استخدام الخدمات',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          _buildUsageStats(state),
          const SizedBox(height: 24),

          // Available plans
          Text(
            'الخطط المتاحة',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          ...ref.watch(availablePlansProvider).map((plan) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: PlanCard(
                  plan: plan,
                  isCurrent: plan.id == state.currentPlan?.id,
                  onUpgrade: () => _handlePlanChange(plan),
                ),
              )),
        ],
      ),
    );
  }

  Widget _buildCurrentPlanHeader(BillingState state) {
    final plan = state.currentPlan;
    if (plan == null) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [SahoolColors.forestGreen, SahoolColors.forestGreen.withValues(alpha: 0.8)],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: SahoolColors.forestGreen.withValues(alpha: 0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'خطتك الحالية',
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  plan.name,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            '${plan.priceMonthly} ريال/شهر',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'التجديد: 15 مارس 2026',
            style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildUsageStats(BillingState state) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildUsageRow('طلبات API', 245, 500, Colors.blue),
            const SizedBox(height: 16),
            _buildUsageRow('تخزين البيانات', 120, 500, Colors.green),
            const SizedBox(height: 16),
            _buildUsageRow('تحليل صور', 18, 30, Colors.orange),
            const SizedBox(height: 16),
            _buildUsageRow('استشارات AI', 42, 60, Colors.purple),
          ],
        ),
      ),
    );
  }

  Widget _buildUsageRow(String label, int used, int total, Color color) {
    final percentage = used / total;
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
            Text(
              '$used / $total',
              style: TextStyle(color: Colors.grey[600], fontSize: 13),
            ),
          ],
        ),
        const SizedBox(height: 6),
        LinearProgressIndicator(
          value: percentage.clamp(0.0, 1.0),
          backgroundColor: Colors.grey[200],
          valueColor: AlwaysStoppedAnimation(
            percentage > 0.9 ? Colors.red : color,
          ),
          minHeight: 8,
          borderRadius: BorderRadius.circular(4),
        ),
      ],
    );
  }

  Widget _buildInvoicesTab(BillingState state) {
    final invoices = state.invoices;
    if (invoices.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.receipt_long, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('لا توجد فواتير', style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: invoices.length,
      itemBuilder: (context, index) {
        final invoice = invoices[index];
        return _buildInvoiceCard(invoice);
      },
    );
  }

  Widget _buildInvoiceCard(BillingInvoice invoice) {
    final statusColor = switch (invoice.status) {
      InvoiceStatus.paid => Colors.green,
      InvoiceStatus.pending => Colors.orange,
      InvoiceStatus.overdue => Colors.red,
    };
    final statusLabel = switch (invoice.status) {
      InvoiceStatus.paid => 'مدفوعة',
      InvoiceStatus.pending => 'معلقة',
      InvoiceStatus.overdue => 'متأخرة',
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: statusColor.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(Icons.receipt, color: statusColor),
        ),
        title: Text(
          invoice.descriptionAr,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text('${invoice.amount} ${invoice.currency}', style: TextStyle(color: Colors.grey[600])),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: statusColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                statusLabel,
                style: TextStyle(color: statusColor, fontSize: 12, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
        trailing: Text(
          '${invoice.issueDate.day}/${invoice.issueDate.month}/${invoice.issueDate.year}',
          style: TextStyle(color: Colors.grey[500], fontSize: 12),
        ),
      ),
    );
  }

  Widget _buildPaymentsTab(BillingState state) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Payment method
          Text(
            'طريقة الدفع',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              leading: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.blue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.credit_card, color: Colors.blue),
              ),
              title: const Text('**** **** **** 4242', style: TextStyle(fontWeight: FontWeight.bold)),
              subtitle: const Text('Visa - تنتهي 12/27'),
              trailing: TextButton(
                onPressed: () => _showPaymentMethodPicker(context),
                child: const Text('تغيير'),
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Payment history
          Text(
            'سجل المدفوعات',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          ...state.paymentHistory.map((payment) => Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: const Icon(Icons.check_circle, color: Colors.green),
                  title: Text(payment.methodAr),
                  subtitle: Text('${payment.date.day}/${payment.date.month}/${payment.date.year}'),
                  trailing: Text(
                    '${payment.amount} ${payment.currency}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              )),
        ],
      ),
    );
  }

  void _showPaymentMethodPicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetContext) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'اختر طريقة الدفع',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildPaymentOption(
              context: sheetContext,
              icon: Icons.credit_card,
              title: 'بطاقة ائتمان / خصم',
              subtitle: 'Visa, Mastercard',
              color: Colors.blue,
            ),
            _buildPaymentOption(
              context: sheetContext,
              icon: Icons.account_balance,
              title: 'تحويل بنكي',
              subtitle: 'تحويل مباشر من حسابك البنكي',
              color: Colors.green,
            ),
            _buildPaymentOption(
              context: sheetContext,
              icon: Icons.phone_android,
              title: 'محفظة إلكترونية',
              subtitle: 'Apple Pay, Google Pay',
              color: Colors.orange,
            ),
            _buildPaymentOption(
              context: sheetContext,
              icon: Icons.account_balance_wallet,
              title: 'رصيد المحفظة',
              subtitle: 'الدفع من رصيد محفظة سهول',
              color: Colors.purple,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPaymentOption({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: color),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          Navigator.pop(context);
          ScaffoldMessenger.of(this.context).showSnackBar(
            SnackBar(
              content: Text('تم اختيار: $title'),
              backgroundColor: SahoolColors.forestGreen,
            ),
          );
        },
      ),
    );
  }

  void _handlePlanChange(BillingPlan plan) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تغيير الخطة'),
        content: Text('هل تريد الترقية إلى خطة ${plan.name}؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ref.read(billingProvider.notifier).changePlan(plan);
            },
            child: const Text('تأكيد'),
          ),
        ],
      ),
    );
  }
}
