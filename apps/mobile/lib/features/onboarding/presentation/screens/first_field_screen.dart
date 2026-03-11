import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/onboarding_page.dart';
import '../widgets/animated_illustration.dart';
import '../../state/onboarding_providers.dart';

/// SAHOOL First Field Screen
/// شاشة الحقل الأول
///
/// Allows user to create their first field (optional)
/// يسمح للمستخدم بإنشاء حقله الأول (اختياري)

class FirstFieldScreen extends ConsumerStatefulWidget {
  /// Callback when field is created or skipped
  final VoidCallback? onComplete;

  /// Callback when user goes back
  final VoidCallback? onBack;

  const FirstFieldScreen({
    super.key,
    this.onComplete,
    this.onBack,
  });

  @override
  ConsumerState<FirstFieldScreen> createState() => _FirstFieldScreenState();
}

class _FirstFieldScreenState extends ConsumerState<FirstFieldScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fieldNameController = TextEditingController();
  String? _selectedCropType;
  bool _isLoading = false;
  bool _showForm = false;

  // Common crop types in Yemen
  static const List<Map<String, String>> _cropTypes = [
    {'id': 'wheat', 'nameAr': 'قمح', 'icon': 'grain'},
    {'id': 'barley', 'nameAr': 'شعير', 'icon': 'grain'},
    {'id': 'sorghum', 'nameAr': 'ذرة رفيعة', 'icon': 'grain'},
    {'id': 'millet', 'nameAr': 'دخن', 'icon': 'grain'},
    {'id': 'maize', 'nameAr': 'ذرة صفراء', 'icon': 'grain'},
    {'id': 'coffee', 'nameAr': 'بن', 'icon': 'coffee'},
    {'id': 'qat', 'nameAr': 'قات', 'icon': 'eco'},
    {'id': 'grapes', 'nameAr': 'عنب', 'icon': 'grape'},
    {'id': 'dates', 'nameAr': 'نخيل', 'icon': 'palm'},
    {'id': 'vegetables', 'nameAr': 'خضروات', 'icon': 'vegetables'},
    {'id': 'alfalfa', 'nameAr': 'برسيم', 'icon': 'grass'},
    {'id': 'other', 'nameAr': 'أخرى', 'icon': 'eco'},
  ];

  @override
  void initState() {
    super.initState();
    // Pre-fill with existing data if available
    final firstField = ref.read(onboardingFirstFieldProvider);
    if (firstField.fieldName != null) {
      _fieldNameController.text = firstField.fieldName!;
      _selectedCropType = firstField.cropType;
      _showForm = true;
    }
  }

  @override
  void dispose() {
    _fieldNameController.dispose();
    super.dispose();
  }

  Future<void> _createField() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      await ref.read(onboardingControllerProvider.notifier).saveFirstField(
            fieldName: _fieldNameController.text.trim(),
            cropType: _selectedCropType,
          );
      widget.onComplete?.call();
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _skipField() {
    ref.read(onboardingControllerProvider.notifier).skipFirstField();
    widget.onComplete?.call();
  }

  @override
  Widget build(BuildContext context) {
    if (!_showForm) {
      return _buildPromptScreen();
    }
    return _buildFormScreen();
  }

  Widget _buildPromptScreen() {
    return OnboardingPage(
      showBackButton: true,
      onBack: widget.onBack,
      skipText: 'تخطي',
      onSkip: _skipField,
      progress: 0.8,
      title: 'أضف حقلك الأول',
      subtitle: 'ابدأ بإضافة حقلك الأول لاستكشاف جميع ميزات التطبيق',
      illustration: const AnimatedIllustration(
        type: IllustrationType.field,
        size: 180,
      ),
      child: Column(
        children: [
          const SizedBox(height: 24),

          // Benefits list
          _buildBenefitItem(
            icon: Icons.map_rounded,
            text: 'ارسم حدود حقلك بدقة على الخريطة',
          ),
          _buildBenefitItem(
            icon: Icons.satellite_alt_rounded,
            text: 'راقب صحة محاصيلك بالأقمار الصناعية',
          ),
          _buildBenefitItem(
            icon: Icons.water_drop_rounded,
            text: 'احصل على توصيات ري مخصصة',
          ),
          _buildBenefitItem(
            icon: Icons.cloud_rounded,
            text: 'تنبيهات طقس خاصة بموقع حقلك',
          ),

          const SizedBox(height: 32),

          // Add field button
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton.icon(
              onPressed: () {
                setState(() => _showForm = true);
              },
              icon: const Icon(Icons.add_rounded),
              label: const Text(
                'إضافة حقل',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.primary,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Skip button
          TextButton(
            onPressed: _skipField,
            child: const Text(
              'سأضيف الحقل لاحقاً',
              style: TextStyle(
                color: SahoolColors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFormScreen() {
    return OnboardingPage(
      showBackButton: true,
      onBack: () {
        setState(() => _showForm = false);
      },
      progress: 0.8,
      primaryButtonText: 'إنشاء الحقل',
      onPrimaryAction: _createField,
      secondaryButtonText: 'تخطي لاحقاً',
      onSecondaryAction: _skipField,
      isLoading: _isLoading,
      title: 'معلومات الحقل',
      subtitle: 'أدخل المعلومات الأساسية لحقلك',
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Field name
            _buildInputField(
              controller: _fieldNameController,
              label: 'اسم الحقل',
              hint: 'مثال: الحقل الشرقي',
              icon: Icons.landscape_rounded,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'الرجاء إدخال اسم الحقل';
                }
                return null;
              },
            ),

            const SizedBox(height: 24),

            // Crop type selection
            const Text(
              'نوع المحصول (اختياري)',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: SahoolColors.textDark,
              ),
            ),
            const SizedBox(height: 12),
            _buildCropTypeGrid(),

            const SizedBox(height: 24),

            // Map preview placeholder
            Container(
              height: 120,
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: InkWell(
                onTap: () {
                  try {
                    Navigator.of(context).pushNamed('/field/draw-boundary');
                  } on FlutterError {
                    // Route not registered during onboarding - expected
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('يمكنك رسم حدود الحقل بعد الإنشاء'),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  }
                },
                borderRadius: BorderRadius.circular(16),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.map_rounded,
                      size: 40,
                      color: Colors.grey[400],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'اضغط لرسم حدود الحقل على الخريطة (اختياري)',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Info text
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: SahoolColors.info.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.info_outline_rounded,
                    color: SahoolColors.info,
                    size: 20,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'يمكنك إضافة المزيد من الحقول والتفاصيل لاحقاً',
                      style: TextStyle(
                        color: Colors.grey[700],
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBenefitItem({
    required IconData icon,
    required String text,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: SahoolColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: SahoolColors.primary,
              size: 22,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 14,
                color: SahoolColors.textDark,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
            color: SahoolColors.textDark,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          validator: validator,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: Icon(icon, color: SahoolColors.primary),
            filled: true,
            fillColor: Colors.grey[100],
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(
                color: SahoolColors.primary,
                width: 2,
              ),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(
                color: SahoolColors.danger,
                width: 2,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCropTypeGrid() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: _cropTypes.map((crop) {
        final isSelected = _selectedCropType == crop['id'];
        return ChoiceChip(
          label: Text(crop['nameAr']!),
          selected: isSelected,
          onSelected: (selected) {
            setState(() {
              _selectedCropType = selected ? crop['id'] : null;
            });
          },
          selectedColor: SahoolColors.primary.withOpacity(0.2),
          backgroundColor: Colors.grey[100],
          labelStyle: TextStyle(
            color: isSelected ? SahoolColors.primary : SahoolColors.textDark,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: BorderSide(
              color: isSelected ? SahoolColors.primary : Colors.transparent,
              width: 1.5,
            ),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        );
      }).toList(),
    );
  }
}
