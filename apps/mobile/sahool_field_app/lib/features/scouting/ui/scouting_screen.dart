import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/sahool_theme.dart';

/// Scouting Form Screen - إضافة تقرير ميداني
/// واجهة بسيطة بأزرار كبيرة للإدخال السريع في الحقل
class ScoutingScreen extends StatefulWidget {
  const ScoutingScreen({super.key});

  @override
  State<ScoutingScreen> createState() => _ScoutingScreenState();
}

class _ScoutingScreenState extends State<ScoutingScreen> {
  String? _selectedCategory;
  String? _selectedIssue;
  double _severity = 0.5;
  String _notes = '';
  bool _hasPhoto = false;

  final Map<String, List<_IssueOption>> _categories = {
    'حشرات': [
      _IssueOption('من', 'حشرات صغيرة ماصة'),
      _IssueOption('دودة', 'يرقات على الأوراق'),
      _IssueOption('جراد', 'جراد صحراوي'),
      _IssueOption('أخرى', 'حشرات أخرى'),
    ],
    'فطريات': [
      _IssueOption('صدأ', 'بقع برتقالية'),
      _IssueOption('بياض', 'طبقة بيضاء'),
      _IssueOption('تعفن', 'تعفن الجذور'),
      _IssueOption('أخرى', 'فطريات أخرى'),
    ],
    'جفاف': [
      _IssueOption('ذبول', 'الأوراق ذابلة'),
      _IssueOption('اصفرار', 'اصفرار الأوراق'),
      _IssueOption('تجعد', 'تجعد الأوراق'),
      _IssueOption('أخرى', 'أعراض أخرى'),
    ],
    'نقص غذائي': [
      _IssueOption('نيتروجين', 'اصفرار عام'),
      _IssueOption('بوتاسيوم', 'حواف بنية'),
      _IssueOption('حديد', 'اصفرار بين العروق'),
      _IssueOption('أخرى', 'نقص آخر'),
    ],
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
        title: const Text('تقرير ميداني'),
        actions: [
          TextButton(
            onPressed: _canSubmit ? _submitReport : null,
            child: Text(
              'إرسال',
              style: TextStyle(
                color: _canSubmit ? SahoolColors.primary : Colors.grey,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Step 1: Category selection
            _buildStepHeader(1, 'نوع المشكلة', _selectedCategory != null),
            const SizedBox(height: 12),
            _buildCategoryGrid(),

            const SizedBox(height: 24),

            // Step 2: Issue selection (if category selected)
            if (_selectedCategory != null) ...[
              _buildStepHeader(2, 'تفاصيل المشكلة', _selectedIssue != null),
              const SizedBox(height: 12),
              _buildIssueGrid(),
              const SizedBox(height: 24),
            ],

            // Step 3: Severity slider (if issue selected)
            if (_selectedIssue != null) ...[
              _buildStepHeader(3, 'شدة المشكلة', true),
              const SizedBox(height: 12),
              _buildSeveritySlider(),
              const SizedBox(height: 24),

              // Step 4: Photo (optional)
              _buildStepHeader(4, 'صورة (اختياري)', _hasPhoto),
              const SizedBox(height: 12),
              _buildPhotoSection(),
              const SizedBox(height: 24),

              // Step 5: Notes (optional)
              _buildStepHeader(5, 'ملاحظات إضافية', _notes.isNotEmpty),
              const SizedBox(height: 12),
              _buildNotesSection(),
              const SizedBox(height: 32),

              // Submit button
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _canSubmit ? _submitReport : null,
                  icon: const Icon(Icons.send),
                  label: const Text('إرسال التقرير'),
                ),
              ),
            ],

            const SizedBox(height: 100),
          ],
        ),
      ),
    );
  }

  bool get _canSubmit =>
      _selectedCategory != null && _selectedIssue != null;

  Widget _buildStepHeader(int step, String title, bool isComplete) {
    return Row(
      children: [
        Container(
          width: 28,
          height: 28,
          decoration: BoxDecoration(
            color: isComplete ? SahoolColors.success : Colors.grey[300],
            shape: BoxShape.circle,
          ),
          child: Center(
            child: isComplete
                ? const Icon(Icons.check, color: Colors.white, size: 16)
                : Text(
                    '$step',
                    style: TextStyle(
                      color: isComplete ? Colors.white : Colors.grey[600],
                      fontWeight: FontWeight.bold,
                    ),
                  ),
          ),
        ),
        const SizedBox(width: 12),
        Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ],
    );
  }

  Widget _buildCategoryGrid() {
    final categories = [
      _CategoryTile('حشرات', Icons.bug_report, Colors.red),
      _CategoryTile('فطريات', Icons.spa, Colors.purple),
      _CategoryTile('جفاف', Icons.water_drop, Colors.orange),
      _CategoryTile('نقص غذائي', Icons.eco, Colors.green),
    ];

    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: categories.map((cat) {
        final isSelected = _selectedCategory == cat.name;
        return GestureDetector(
          onTap: () => setState(() {
            _selectedCategory = cat.name;
            _selectedIssue = null;
          }),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            decoration: BoxDecoration(
              color: isSelected ? cat.color.withOpacity(0.15) : Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isSelected ? cat.color : Colors.grey[300]!,
                width: isSelected ? 2 : 1,
              ),
              boxShadow: isSelected ? SahoolShadows.colored(cat.color) : SahoolShadows.small,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  cat.icon,
                  size: 36,
                  color: isSelected ? cat.color : Colors.grey[600],
                ),
                const SizedBox(height: 8),
                Text(
                  cat.name,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: isSelected ? cat.color : Colors.grey[800],
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildIssueGrid() {
    final issues = _categories[_selectedCategory] ?? [];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: issues.map((issue) {
        final isSelected = _selectedIssue == issue.name;
        return ChoiceChip(
          label: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                issue.name,
                style: TextStyle(
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
              Text(
                issue.description,
                style: TextStyle(
                  fontSize: 10,
                  color: isSelected ? Colors.white70 : Colors.grey[600],
                ),
              ),
            ],
          ),
          selected: isSelected,
          onSelected: (_) => setState(() => _selectedIssue = issue.name),
          selectedColor: SahoolColors.primary,
          backgroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        );
      }).toList(),
    );
  }

  Widget _buildSeveritySlider() {
    String severityLabel;
    Color severityColor;

    if (_severity < 0.33) {
      severityLabel = 'خفيف';
      severityColor = SahoolColors.success;
    } else if (_severity < 0.66) {
      severityLabel = 'متوسط';
      severityColor = SahoolColors.warning;
    } else {
      severityLabel = 'شديد';
      severityColor = SahoolColors.danger;
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('خفيف', style: TextStyle(color: SahoolColors.success)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: severityColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  severityLabel,
                  style: TextStyle(
                    color: severityColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const Text('شديد', style: TextStyle(color: SahoolColors.danger)),
            ],
          ),
          const SizedBox(height: 16),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              trackHeight: 8,
              thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 12),
            ),
            child: Slider(
              value: _severity,
              onChanged: (value) => setState(() => _severity = value),
              activeColor: severityColor,
              inactiveColor: Colors.grey[200],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPhotoSection() {
    return GestureDetector(
      onTap: () => setState(() => _hasPhoto = !_hasPhoto),
      child: Container(
        height: 150,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _hasPhoto ? SahoolColors.success : Colors.grey[300]!,
            width: _hasPhoto ? 2 : 1,
          ),
          boxShadow: SahoolShadows.small,
        ),
        child: _hasPhoto
            ? Stack(
                children: [
                  // Placeholder image
                  Container(
                    decoration: BoxDecoration(
                      color: SahoolColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Center(
                      child: Icon(Icons.image, size: 48, color: SahoolColors.primary),
                    ),
                  ),
                  Positioned(
                    top: 8,
                    left: 8,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: const BoxDecoration(
                        color: SahoolColors.success,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.check, color: Colors.white, size: 16),
                    ),
                  ),
                  Positioned(
                    top: 8,
                    right: 8,
                    child: IconButton(
                      onPressed: () => setState(() => _hasPhoto = false),
                      icon: const Icon(Icons.close),
                      style: IconButton.styleFrom(
                        backgroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.camera_alt, size: 40, color: Colors.grey[400]),
                  const SizedBox(height: 8),
                  Text(
                    'اضغط لالتقاط صورة',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildNotesSection() {
    return TextField(
      maxLines: 3,
      decoration: InputDecoration(
        hintText: 'أضف ملاحظات إضافية...',
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
      ),
      onChanged: (value) => setState(() => _notes = value),
    );
  }

  void _submitReport() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.check_circle, color: SahoolColors.success),
            const SizedBox(width: 12),
            const Text('تم الإرسال'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('تم حفظ التقرير بنجاح'),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('النوع: $_selectedCategory'),
                  Text('المشكلة: $_selectedIssue'),
                  Text('الشدة: ${(_severity * 100).toInt()}%'),
                ],
              ),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.pop();
            },
            child: const Text('تم'),
          ),
        ],
      ),
    );
  }
}

class _CategoryTile {
  final String name;
  final IconData icon;
  final Color color;

  _CategoryTile(this.name, this.icon, this.color);
}

class _IssueOption {
  final String name;
  final String description;

  _IssueOption(this.name, this.description);
}
