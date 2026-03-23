import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';
import '../widgets/widgets.dart';

/// Help Screen
/// شاشة المساعدة
class HelpScreen extends StatefulWidget {
  const HelpScreen({super.key});

  @override
  State<HelpScreen> createState() => _HelpScreenState();
}

class _HelpScreenState extends State<HelpScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  int _expandedIndex = -1;

  final List<_FAQCategory> _faqCategories = [
    _FAQCategory(
      title: 'البداية',
      icon: Icons.rocket_launch,
      color: SahoolTheme.primary,
      faqs: [
        _FAQ(
          question: 'كيف أبدأ باستخدام التطبيق؟',
          answer:
              'بعد تسجيل الدخول، يمكنك إضافة حقولك من خلال الضغط على زر "+" في الصفحة الرئيسية. ارسم حدود الحقل على الخريطة أو أدخل الإحداثيات يدوياً.',
        ),
        _FAQ(
          question: 'كيف أضيف حقلاً جديداً؟',
          answer:
              '1. اضغط على زر "+" في الصفحة الرئيسية\n2. اختر "حقل جديد"\n3. حدد موقع الحقل على الخريطة\n4. ارسم حدود الحقل\n5. أدخل معلومات المحصول\n6. احفظ الحقل',
        ),
        _FAQ(
          question: 'هل يعمل التطبيق بدون إنترنت؟',
          answer:
              'نعم! التطبيق مصمم للعمل دون اتصال. يمكنك عرض حقولك، تسجيل العمليات، ورؤية الخرائط المحفوظة. ستتم مزامنة البيانات تلقائياً عند توفر الاتصال.',
        ),
      ],
    ),
    _FAQCategory(
      title: 'الحقول والخرائط',
      icon: Icons.map,
      color: Colors.blue,
      faqs: [
        _FAQ(
          question: 'كيف أرسم حدود حقلي؟',
          answer:
              'في شاشة إضافة الحقل، اضغط على "رسم الحدود" ثم انقر على الخريطة لإضافة النقاط. اضغط على النقطة الأولى لإغلاق الشكل. يمكنك تعديل النقاط بسحبها.',
        ),
        _FAQ(
          question: 'كيف أنزّل خرائط للاستخدام دون اتصال؟',
          answer:
              'اذهب إلى الإعدادات > المزامنة والتخزين > الخرائط دون اتصال. اختر المنطقة التي تريد تنزيلها واضغط "تنزيل".',
        ),
        _FAQ(
          question: 'ما معنى ألوان صحة المحصول؟',
          answer:
              '🟢 أخضر داكن: صحة ممتازة (NDVI > 0.8)\n🟢 أخضر: صحة جيدة (0.6-0.8)\n🟡 أصفر: صحة متوسطة (0.4-0.6)\n🟠 برتقالي: صحة ضعيفة (0.2-0.4)\n🔴 أحمر: مشكلة (< 0.2)',
        ),
      ],
    ),
    _FAQCategory(
      title: 'المهام والتنبيهات',
      icon: Icons.task_alt,
      color: SahoolTheme.success,
      faqs: [
        _FAQ(
          question: 'كيف أضيف مهمة جديدة؟',
          answer:
              'من الصفحة الرئيسية، اضغط "+" واختر "مهمة جديدة". حدد الحقل، نوع المهمة، التاريخ، والأولوية. يمكنك أيضاً إضافة ملاحظات وصور.',
        ),
        _FAQ(
          question: 'كيف أتلقى تنبيهات الطقس؟',
          answer:
              'التنبيهات مفعلة تلقائياً. يمكنك تخصيصها من الإعدادات > الإشعارات. نرسل تحذيرات للصقيع، الأمطار الغزيرة، والحرارة الشديدة.',
        ),
        _FAQ(
          question: 'لماذا لم أتلقَ إشعاراً؟',
          answer:
              'تأكد من:\n1. تفعيل الإشعارات في إعدادات التطبيق\n2. السماح للتطبيق بإرسال الإشعارات في إعدادات الهاتف\n3. عدم تفعيل وضع "لا تزعج"\n4. عدم تشغيل "ساعات الهدوء"',
        ),
      ],
    ),
    _FAQCategory(
      title: 'المزامنة والبيانات',
      icon: Icons.sync,
      color: SahoolTheme.warning,
      faqs: [
        _FAQ(
          question: 'لماذا بياناتي لم تتم مزامنتها؟',
          answer:
              'تحقق من:\n1. اتصال الإنترنت\n2. تفعيل المزامنة التلقائية\n3. إذا كان "واي فاي فقط" مفعلاً، تأكد من الاتصال بواي فاي\n\nيمكنك المزامنة يدوياً من الإعدادات > المزامنة > "مزامنة الآن"',
        ),
        _FAQ(
          question: 'كيف أستعيد بياناتي المحذوفة؟',
          answer:
              'البيانات المحذوفة تبقى في سلة المهملات لمدة 30 يوماً. اذهب إلى الإعدادات > البيانات > سلة المهملات لاستعادتها.',
        ),
        _FAQ(
          question: 'كيف أنقل بياناتي لجهاز جديد؟',
          answer:
              '1. سجل الدخول بنفس الحساب على الجهاز الجديد\n2. ستتم مزامنة بياناتك تلقائياً\n3. لنقل الخرائط دون اتصال، قم بتنزيلها مرة أخرى',
        ),
      ],
    ),
    _FAQCategory(
      title: 'الحساب والأمان',
      icon: Icons.security,
      color: Colors.purple,
      faqs: [
        _FAQ(
          question: 'كيف أغير كلمة المرور؟',
          answer:
              'اذهب إلى الإعدادات > الحساب > تغيير كلمة المرور. أدخل كلمة المرور الحالية ثم الجديدة.',
        ),
        _FAQ(
          question: 'كيف أفعّل تسجيل الدخول بالبصمة؟',
          answer:
              'اذهب إلى الإعدادات > الحساب > الأمان > تسجيل الدخول بالبصمة. يجب أن يكون لديك بصمة مسجلة في جهازك.',
        ),
        _FAQ(
          question: 'نسيت كلمة المرور، ماذا أفعل؟',
          answer:
              'في شاشة تسجيل الدخول، اضغط "نسيت كلمة المرور". أدخل بريدك الإلكتروني وسنرسل لك رابط إعادة التعيين.',
        ),
      ],
    ),
  ];

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: isDark ? Colors.black : Colors.grey[100],
        appBar: AppBar(
          backgroundColor: isDark ? Colors.grey[900] : Colors.white,
          elevation: 0,
          title: Text(
            'المساعدة',
            style: TextStyle(
              color: isDark ? Colors.white : Colors.black87,
              fontWeight: FontWeight.bold,
            ),
          ),
          centerTitle: true,
          leading: IconButton(
            icon: const Icon(Icons.arrow_forward_ios),
            color: isDark ? Colors.white : Colors.black87,
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: Column(
          children: [
            // Search Bar
            Container(
              padding: const EdgeInsets.all(16),
              color: isDark ? Colors.grey[900] : Colors.white,
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'ابحث في المساعدة...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _searchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _searchController.clear();
                            setState(() => _searchQuery = '');
                          },
                        )
                      : null,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: isDark ? Colors.grey[800] : Colors.grey[100],
                ),
                onChanged: (value) => setState(() => _searchQuery = value),
              ),
            ),

            // Content
            Expanded(
              child: _searchQuery.isNotEmpty
                  ? _buildSearchResults()
                  : _buildCategoryList(),
            ),
          ],
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () => _showContactSupport(context),
          icon: const Icon(Icons.headset_mic),
          label: const Text('تواصل معنا'),
        ),
      ),
    );
  }

  Widget _buildCategoryList() {
    return ListView(
      padding: const EdgeInsets.only(bottom: 80),
      children: [
        // Quick Actions
        _QuickActionsSection(),

        // FAQ Categories
        ...List.generate(_faqCategories.length, (categoryIndex) {
          final category = _faqCategories[categoryIndex];
          return SettingsSection(
            title: category.title,
            titleAr: category.title,
            icon: category.icon,
            children: [
              ...List.generate(category.faqs.length, (faqIndex) {
                final globalIndex = _getGlobalIndex(categoryIndex, faqIndex);
                final faq = category.faqs[faqIndex];
                return _FAQTile(
                  faq: faq,
                  color: category.color,
                  isExpanded: _expandedIndex == globalIndex,
                  onTap: () {
                    setState(() {
                      _expandedIndex = _expandedIndex == globalIndex ? -1 : globalIndex;
                    });
                  },
                );
              }),
            ],
          );
        }),
      ],
    );
  }

  int _getGlobalIndex(int categoryIndex, int faqIndex) {
    int index = 0;
    for (int i = 0; i < categoryIndex; i++) {
      index += _faqCategories[i].faqs.length;
    }
    return index + faqIndex;
  }

  Widget _buildSearchResults() {
    final results = <_SearchResult>[];

    for (final category in _faqCategories) {
      for (final faq in category.faqs) {
        if (faq.question.contains(_searchQuery) ||
            faq.answer.contains(_searchQuery)) {
          results.add(_SearchResult(faq: faq, category: category));
        }
      }
    }

    if (results.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'لا توجد نتائج لـ "$_searchQuery"',
              style: TextStyle(fontSize: 16, color: Colors.grey[600]),
            ),
            const SizedBox(height: 8),
            TextButton.icon(
              onPressed: () => _showContactSupport(context),
              icon: const Icon(Icons.headset_mic),
              label: const Text('تواصل مع الدعم'),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: results.length,
      itemBuilder: (context, index) {
        final result = results[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ExpansionTile(
            leading: Icon(result.category.icon, color: result.category.color),
            title: Text(
              result.faq.question,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            subtitle: Text(
              result.category.title,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  result.faq.answer,
                  style: const TextStyle(height: 1.6),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showContactSupport(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).brightness == Brightness.dark
              ? Colors.grey[900]
              : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[400],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'كيف يمكننا مساعدتك؟',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            ListTile(
              leading: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: SahoolTheme.info.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.chat, color: SahoolTheme.info),
              ),
              title: const Text('الدردشة المباشرة'),
              subtitle: const Text('متاح من 9 ص - 5 م'),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('جاري فتح الدردشة...')),
                );
              },
            ),
            ListTile(
              leading: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: SahoolTheme.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.email, color: SahoolTheme.success),
              ),
              title: const Text('البريد الإلكتروني'),
              subtitle: const Text('support@sahool.app'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: SahoolTheme.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.phone, color: SahoolTheme.warning),
              ),
              title: const Text('الهاتف'),
              subtitle: const Text('+967 1 234 567'),
              onTap: () => Navigator.pop(context),
            ),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }
}

/// Quick Actions Section
class _QuickActionsSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'إجراءات سريعة',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.grey[700],
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.play_circle_outline,
                  label: 'دليل البداية',
                  color: SahoolTheme.primary,
                  onTap: () {},
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.video_library_outlined,
                  label: 'فيديوهات تعليمية',
                  color: Colors.red,
                  onTap: () {},
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.article_outlined,
                  label: 'دليل المستخدم',
                  color: Colors.blue,
                  onTap: () {},
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.tips_and_updates_outlined,
                  label: 'نصائح وحيل',
                  color: Colors.amber,
                  onTap: () {},
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Quick Action Card
class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isDark ? Colors.grey[900] : Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(isDark ? 0.3 : 0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// FAQ Tile
class _FAQTile extends StatelessWidget {
  final _FAQ faq;
  final Color color;
  final bool isExpanded;
  final VoidCallback onTap;

  const _FAQTile({
    required this.faq,
    required this.color,
    required this.isExpanded,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isExpanded ? color.withOpacity(0.05) : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.help_outline,
                    color: color,
                    size: 20,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      faq.question,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                        color: isDark ? Colors.white : Colors.black87,
                      ),
                    ),
                  ),
                  AnimatedRotation(
                    turns: isExpanded ? 0.5 : 0,
                    duration: const Duration(milliseconds: 200),
                    child: Icon(
                      Icons.expand_more,
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ),
              if (isExpanded) ...[
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.only(right: 32),
                  child: Text(
                    faq.answer,
                    style: TextStyle(
                      fontSize: 14,
                      height: 1.6,
                      color: isDark ? Colors.grey[300] : Colors.grey[700],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Spacer(),
                    TextButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.thumb_up_outlined, size: 16),
                      label: const Text('مفيد'),
                    ),
                    TextButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.thumb_down_outlined, size: 16),
                      label: const Text('غير مفيد'),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// FAQ Category Model
class _FAQCategory {
  final String title;
  final IconData icon;
  final Color color;
  final List<_FAQ> faqs;

  _FAQCategory({
    required this.title,
    required this.icon,
    required this.color,
    required this.faqs,
  });
}

/// FAQ Model
class _FAQ {
  final String question;
  final String answer;

  _FAQ({
    required this.question,
    required this.answer,
  });
}

/// Search Result Model
class _SearchResult {
  final _FAQ faq;
  final _FAQCategory category;

  _SearchResult({
    required this.faq,
    required this.category,
  });
}
