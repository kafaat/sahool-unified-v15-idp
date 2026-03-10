import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/onboarding_page.dart';
import '../../state/onboarding_providers.dart';

/// SAHOOL Setup Profile Screen
/// شاشة إعداد الملف الشخصي
///
/// Collects basic user information
/// تجمع المعلومات الأساسية للمستخدم

class SetupProfileScreen extends ConsumerStatefulWidget {
  /// Callback when profile is saved
  final VoidCallback? onComplete;

  /// Callback when user goes back
  final VoidCallback? onBack;

  const SetupProfileScreen({
    super.key,
    this.onComplete,
    this.onBack,
  });

  @override
  ConsumerState<SetupProfileScreen> createState() => _SetupProfileScreenState();
}

class _SetupProfileScreenState extends ConsumerState<SetupProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _userNameController = TextEditingController();
  final _farmNameController = TextEditingController();
  final _userNameFocusNode = FocusNode();
  final _farmNameFocusNode = FocusNode();
  bool _isLoading = false;
  String? _profileImagePath;
  final _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    // Pre-fill with existing data if available
    final profile = ref.read(onboardingProfileProvider);
    if (profile.userName != null) {
      _userNameController.text = profile.userName!;
    }
    if (profile.farmName != null) {
      _farmNameController.text = profile.farmName!;
    }
  }

  @override
  void dispose() {
    _userNameController.dispose();
    _farmNameController.dispose();
    _userNameFocusNode.dispose();
    _farmNameFocusNode.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      await ref.read(onboardingControllerProvider.notifier).saveProfile(
            userName: _userNameController.text.trim(),
            farmName: _farmNameController.text.trim().isNotEmpty
                ? _farmNameController.text.trim()
                : null,
          );
      widget.onComplete?.call();
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return OnboardingPage(
      showBackButton: true,
      onBack: widget.onBack,
      skipText: null, // Profile is required, no skip
      progress: 0.6,
      primaryButtonText: 'حفظ ومتابعة',
      onPrimaryAction: _saveProfile,
      isLoading: _isLoading,
      title: 'معلوماتك الشخصية',
      subtitle: 'ساعدنا في التعرف عليك لتقديم تجربة مخصصة',
      illustration: _buildProfileIllustration(),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Profile picture section
            _buildProfilePictureSection(),

            const SizedBox(height: 32),

            // User name field
            _buildInputField(
              controller: _userNameController,
              focusNode: _userNameFocusNode,
              label: 'اسمك',
              hint: 'مثال: أحمد محمد',
              icon: Icons.person_rounded,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'الرجاء إدخال اسمك';
                }
                if (value.trim().length < 2) {
                  return 'الاسم قصير جداً';
                }
                return null;
              },
              textInputAction: TextInputAction.next,
              onFieldSubmitted: (_) {
                _farmNameFocusNode.requestFocus();
              },
            ),

            const SizedBox(height: 20),

            // Farm name field
            _buildInputField(
              controller: _farmNameController,
              focusNode: _farmNameFocusNode,
              label: 'اسم المزرعة (اختياري)',
              hint: 'مثال: مزرعة الخير',
              icon: Icons.agriculture_rounded,
              validator: null, // Optional field
              textInputAction: TextInputAction.done,
              onFieldSubmitted: (_) {
                _saveProfile();
              },
            ),

            const SizedBox(height: 24),

            // Info card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: SahoolColors.info.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.info_outline_rounded,
                    color: SahoolColors.info,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'يمكنك تعديل هذه المعلومات لاحقاً من الإعدادات',
                      style: TextStyle(
                        color: Colors.grey[700],
                        fontSize: 13,
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

  Widget _buildProfileIllustration() {
    return const SizedBox(
      height: 80,
      child: Center(
        child: Icon(
          Icons.account_circle_rounded,
          size: 70,
          color: SahoolColors.primary,
        ),
      ),
    );
  }

  Widget _buildProfilePictureSection() {
    return Center(
      child: Stack(
        children: [
          // Profile picture placeholder or selected image
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              color: SahoolColors.primary.withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(
                color: SahoolColors.primary.withOpacity(0.3),
                width: 3,
              ),
              image: _profileImagePath != null
                  ? DecorationImage(
                      image: FileImage(File(_profileImagePath!)),
                      fit: BoxFit.cover,
                    )
                  : null,
            ),
            child: _profileImagePath == null
                ? const Icon(
                    Icons.person_rounded,
                    size: 50,
                    color: SahoolColors.primary,
                  )
                : null,
          ),

          // Camera button
          Positioned(
            bottom: 0,
            right: 0,
            child: Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: SahoolColors.primary,
                shape: BoxShape.circle,
                border: Border.all(
                  color: Colors.white,
                  width: 2,
                ),
              ),
              child: IconButton(
                icon: const Icon(
                  Icons.camera_alt_rounded,
                  size: 16,
                  color: Colors.white,
                ),
                onPressed: _showImagePickerSheet,
                padding: EdgeInsets.zero,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showImagePickerSheet() {
    showModalBottomSheet<void>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
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
                const SizedBox(height: 16),
                const Text(
                  'اختر صورة الملف الشخصي',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.textDark,
                  ),
                ),
                const SizedBox(height: 16),
                ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: SahoolColors.primary,
                    child: Icon(Icons.camera_alt_rounded, color: Colors.white),
                  ),
                  title: const Text('الكاميرا'),
                  subtitle: const Text('التقط صورة جديدة'),
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(ImageSource.camera);
                  },
                ),
                ListTile(
                  leading: CircleAvatar(
                    backgroundColor: SahoolColors.primary.withOpacity(0.8),
                    child: const Icon(Icons.photo_library_rounded, color: Colors.white),
                  ),
                  title: const Text('المعرض'),
                  subtitle: const Text('اختر من معرض الصور'),
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(ImageSource.gallery);
                  },
                ),
                if (_profileImagePath != null)
                  ListTile(
                    leading: const CircleAvatar(
                      backgroundColor: SahoolColors.danger,
                      child: Icon(Icons.delete_rounded, color: Colors.white),
                    ),
                    title: const Text('إزالة الصورة'),
                    onTap: () {
                      Navigator.pop(context);
                      setState(() => _profileImagePath = null);
                    },
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final pickedFile = await _imagePicker.pickImage(
        source: source,
        maxWidth: 512,
        maxHeight: 512,
        imageQuality: 80,
      );
      if (pickedFile != null && mounted) {
        setState(() => _profileImagePath = pickedFile.path);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تعذر اختيار الصورة، يرجى المحاولة مرة أخرى'),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  Widget _buildInputField({
    required TextEditingController controller,
    required FocusNode focusNode,
    required String label,
    required String hint,
    required IconData icon,
    String? Function(String?)? validator,
    TextInputAction? textInputAction,
    void Function(String)? onFieldSubmitted,
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
          focusNode: focusNode,
          validator: validator,
          textInputAction: textInputAction,
          onFieldSubmitted: onFieldSubmitted,
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
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 16,
            ),
          ),
        ),
      ],
    );
  }
}
