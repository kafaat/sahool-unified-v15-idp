import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';

/// شاشة المحفظة المالية - تصميم Fintech احترافي
/// Professional Fintech Wallet Screen
class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  // بيانات وهمية للعرض
  final double _balance = 4250.00;
  final int _creditScore = 850;
  final int _maxCreditScore = 1000;

  final List<Map<String, dynamic>> _transactions = [
    {
      'title': 'بيع محصول بطاطس',
      'amount': 1200.0,
      'isIncome': true,
      'date': 'اليوم، 10:30 ص',
      'icon': Icons.agriculture,
    },
    {
      'title': 'شراء أسمدة يوريا',
      'amount': 350.0,
      'isIncome': false,
      'date': 'أمس، 3:45 م',
      'icon': Icons.shopping_bag,
    },
    {
      'title': 'خدمات استشارية',
      'amount': 50.0,
      'isIncome': false,
      'date': 'منذ يومين',
      'icon': Icons.support_agent,
    },
    {
      'title': 'بيع محصول قمح',
      'amount': 2800.0,
      'isIncome': true,
      'date': 'منذ 3 أيام',
      'icon': Icons.grass,
    },
    {
      'title': 'شراء معدات ري',
      'amount': 1500.0,
      'isIncome': false,
      'date': 'منذ أسبوع',
      'icon': Icons.water_drop,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: const Text("محفظتي"),
        backgroundColor: SahoolColors.forestGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            onPressed: () {
              // إعدادات المحفظة
            },
            icon: const Icon(Icons.settings_outlined),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // 1. بطاقة الرصيد الرئيسية
            _buildBalanceCard(),

            // 2. بطاقة التقييم الائتماني
            _buildCreditScoreCard(),

            // 3. سجل العمليات
            _buildTransactionsSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildBalanceCard() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1B5E20), Color(0xFF2E7D32)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: SahoolColors.forestGreen.withOpacity(0.4),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // رأس البطاقة
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "الرصيد الكلي",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                ),
              ),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.credit_card,
                  color: Colors.white70,
                  size: 20,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // الرصيد
          Text(
            "\$ ${_balance.toStringAsFixed(2)}",
            style: const TextStyle(
              color: Colors.white,
              fontSize: 36,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 8),

          // آخر تحديث
          Text(
            "آخر تحديث: ${DateTime.now().toString().substring(0, 16)}",
            style: TextStyle(
              color: Colors.white.withOpacity(0.6),
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 24),

          // أزرار الإجراءات
          Row(
            children: [
              Expanded(
                child: _ActionButton(
                  icon: Icons.arrow_upward,
                  label: "إيداع",
                  onTap: () => _showDepositDialog(),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _ActionButton(
                  icon: Icons.arrow_downward,
                  label: "سحب",
                  onTap: () => _showWithdrawDialog(),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _ActionButton(
                  icon: Icons.swap_horiz,
                  label: "تحويل",
                  onTap: () => _showTransferDialog(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCreditScoreCard() {
    final scorePercentage = _creditScore / _maxCreditScore;
    String scoreStatus;
    Color scoreColor;

    if (scorePercentage >= 0.8) {
      scoreStatus = "ممتاز";
      scoreColor = Colors.green;
    } else if (scorePercentage >= 0.6) {
      scoreStatus = "جيد";
      scoreColor = Colors.orange;
    } else {
      scoreStatus = "يحتاج تحسين";
      scoreColor = Colors.red;
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // مؤشر التقدم الدائري
          SizedBox(
            width: 60,
            height: 60,
            child: Stack(
              children: [
                CircularProgressIndicator(
                  value: scorePercentage,
                  strokeWidth: 8,
                  backgroundColor: Colors.grey[200],
                  valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
                ),
                Center(
                  child: Icon(
                    Icons.shield,
                    color: scoreColor,
                    size: 24,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 20),

          // التفاصيل
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "التقييم الائتماني",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Text(
                      scoreStatus,
                      style: TextStyle(
                        color: scoreColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      "($_creditScore/$_maxCreditScore)",
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // سهم للتفاصيل
          Icon(
            Icons.arrow_forward_ios,
            color: Colors.grey[400],
            size: 16,
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionsSection() {
    return Container(
      margin: const EdgeInsets.only(top: 20),
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // رأس القسم
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "آخر العمليات",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              TextButton(
                onPressed: () {
                  // عرض كل العمليات
                },
                child: const Text("عرض الكل"),
              ),
            ],
          ),
          const SizedBox(height: 10),

          // قائمة العمليات
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _transactions.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final transaction = _transactions[index];
              return _TransactionItem(
                title: transaction['title'] as String,
                amount: transaction['amount'] as double,
                isIncome: transaction['isIncome'] as bool,
                date: transaction['date'] as String,
                icon: transaction['icon'] as IconData,
              );
            },
          ),

          const SizedBox(height: 80), // مساحة للتمرير
        ],
      ),
    );
  }

  void _showDepositDialog() {
    _showAmountDialog("إيداع", "أدخل مبلغ الإيداع", Colors.green);
  }

  void _showWithdrawDialog() {
    _showAmountDialog("سحب", "أدخل مبلغ السحب", Colors.red);
  }

  void _showTransferDialog() {
    _showAmountDialog("تحويل", "أدخل مبلغ التحويل", Colors.blue);
  }

  void _showAmountDialog(String title, String hint, Color color) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
            left: 20,
            right: 20,
            top: 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              TextField(
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  hintText: hint,
                  prefixIcon: const Icon(Icons.attach_money),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('تم $title بنجاح'),
                        backgroundColor: color,
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: color,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    "تأكيد $title",
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 30),
            ],
          ),
        );
      },
    );
  }
}

/// زر الإجراء في بطاقة الرصيد
class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 18),
            const SizedBox(width: 6),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// عنصر العملية المالية
class _TransactionItem extends StatelessWidget {
  final String title;
  final double amount;
  final bool isIncome;
  final String date;
  final IconData icon;

  const _TransactionItem({
    required this.title,
    required this.amount,
    required this.isIncome,
    required this.date,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        backgroundColor: isIncome
            ? Colors.green.withOpacity(0.1)
            : Colors.red.withOpacity(0.1),
        child: Icon(
          icon,
          color: isIncome ? Colors.green : Colors.red,
          size: 20,
        ),
      ),
      title: Text(
        title,
        style: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 14,
        ),
      ),
      subtitle: Text(
        date,
        style: TextStyle(
          color: Colors.grey[500],
          fontSize: 12,
        ),
      ),
      trailing: Text(
        "${isIncome ? '+' : '-'} \$${amount.toStringAsFixed(0)}",
        style: TextStyle(
          color: isIncome ? Colors.green : Colors.red,
          fontWeight: FontWeight.bold,
          fontSize: 16,
        ),
      ),
    );
  }
}
