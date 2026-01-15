import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/security/screen_security_service.dart';
import '../../../core/security/security_config.dart';
import '../data/auth_service.dart';

/// Registration Screen - شاشة التسجيل
/// تصميم بسيط للمزارعين لإنشاء حساب جديد
class RegistrationScreen extends ConsumerStatefulWidget {
  const RegistrationScreen({super.key});

  @override
  ConsumerState<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends ConsumerState<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _phoneController = TextEditingController();

  final _emailFocusNode = FocusNode();
  final _passwordFocusNode = FocusNode();
  final _confirmPasswordFocusNode = FocusNode();
  final _firstNameFocusNode = FocusNode();
  final _lastNameFocusNode = FocusNode();
  final _phoneFocusNode = FocusNode();

  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isArabic = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _emailFocusNode.dispose();
    _passwordFocusNode.dispose();
    _confirmPasswordFocusNode.dispose();
    _firstNameFocusNode.dispose();
    _lastNameFocusNode.dispose();
    _phoneFocusNode.dispose();
    super.dispose();
  }

  String _tr(String ar, String en) => _isArabic ? ar : en;

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final authService = ref.read(authServiceProvider);

    final request = RegisterRequest(
      email: _emailController.text.trim(),
      password: _passwordController.text,
      firstName: _firstNameController.text.trim(),
      lastName: _lastNameController.text.trim(),
      phone: _phoneController.text.trim().isNotEmpty
          ? _phoneController.text.trim()
          : null,
    );

    final result = await authService.register(request);

    if (!mounted) return;

    setState(() => _isLoading = false);

    if (result.success) {
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _tr('تم إنشاء الحساب بنجاح!', 'Account created successfully!'),
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                _tr(
                  'مرحباً ${result.response!.user.fullName}',
                  'Welcome ${result.response!.user.fullName}',
                ),
                style: const TextStyle(fontSize: 12),
              ),
            ],
          ),
          backgroundColor: SahoolColors.success,
          duration: const Duration(seconds: 2),
          behavior: SnackBarBehavior.floating,
        ),
      );

      // Navigate to home screen after short delay
      await Future.delayed(const Duration(milliseconds: 500));
      if (mounted) {
        context.go('/map');
      }
    } else {
      // Show error message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _isArabic
                    ? result.errorMessageAr ?? 'حدث خطأ غير متوقع'
                    : result.errorMessage ?? 'An unexpected error occurred',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              if (!_isArabic && result.errorMessageAr != null) ...[
                const SizedBox(height: 4),
                Text(
                  result.errorMessageAr!,
                  style: const TextStyle(fontSize: 12),
                ),
              ],
            ],
          ),
          backgroundColor: SahoolColors.danger,
          duration: const Duration(seconds: 4),
          behavior: SnackBarBehavior.floating,
          action: SnackBarAction(
            label: _tr('حاول مرة أخرى', 'Retry'),
            textColor: Colors.white,
            onPressed: _register,
          ),
        ),
      );
    }
  }

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return _tr('البريد الإلكتروني مطلوب', 'Email is required');
    }
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value)) {
      return _tr(
        'يرجى إدخال بريد إلكتروني صالح',
        'Please enter a valid email address',
      );
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return _tr('كلمة المرور مطلوبة', 'Password is required');
    }
    if (value.length < 8) {
      return _tr(
        'كلمة المرور يجب أن تكون 8 أحرف على الأقل',
        'Password must be at least 8 characters',
      );
    }
    if (!RegExp(r'[A-Z]').hasMatch(value)) {
      return _tr(
        'يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل',
        'Password must contain at least one uppercase letter',
      );
    }
    if (!RegExp(r'[0-9]').hasMatch(value)) {
      return _tr(
        'يجب أن تحتوي كلمة المرور على رقم واحد على الأقل',
        'Password must contain at least one number',
      );
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) {
      return _tr('تأكيد كلمة المرور مطلوب', 'Confirm password is required');
    }
    if (value != _passwordController.text) {
      return _tr('كلمات المرور غير متطابقة', 'Passwords do not match');
    }
    return null;
  }

  String? _validateName(String? value, bool isFirst) {
    if (value == null || value.isEmpty) {
      return isFirst
          ? _tr('الاسم الأول مطلوب', 'First name is required')
          : _tr('الاسم الأخير مطلوب', 'Last name is required');
    }
    if (value.length < 2) {
      return _tr(
        'يجب أن يكون الاسم حرفين على الأقل',
        'Name must be at least 2 characters',
      );
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return SecureScreen(
      screenType: SecuredScreenType.authentication,
      showWarning: ref.watch(securityConfigProvider).showScreenSecurityWarning,
      warningMessageAr:
          'لا يمكن أخذ لقطات شاشة في شاشة التسجيل لحماية بياناتك',
      warningMessageEn:
          'Screenshots are disabled on registration screen to protect your credentials',
      child: Scaffold(
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Top bar with back button and language toggle
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      IconButton(
                        onPressed: () => context.go('/login'),
                        icon: const Icon(Icons.arrow_back),
                        style: IconButton.styleFrom(
                          backgroundColor: Colors.grey[100],
                        ),
                      ),
                      _buildLanguageToggle(),
                    ],
                  ),

                  const SizedBox(height: 32),

                  // Header
                  Center(
                    child: Column(
                      children: [
                        Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            color: SahoolColors.primary.withOpacity(0.1),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.person_add,
                            size: 40,
                            color: SahoolColors.primary,
                          ),
                        ),
                        const SizedBox(height: 24),
                        Text(
                          _tr('إنشاء حساب جديد', 'Create Account'),
                          style: const TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _tr(
                            'أدخل بياناتك للتسجيل في سهول',
                            'Enter your details to register',
                          ),
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey[600],
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 40),

                  // Name fields row
                  Row(
                    children: [
                      Expanded(
                        child: _buildTextField(
                          controller: _firstNameController,
                          focusNode: _firstNameFocusNode,
                          label: _tr('الاسم الأول', 'First Name'),
                          hint: _tr('محمد', 'Mohammed'),
                          icon: Icons.person_outline,
                          validator: (v) => _validateName(v, true),
                          textInputAction: TextInputAction.next,
                          onFieldSubmitted: (_) =>
                              _lastNameFocusNode.requestFocus(),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildTextField(
                          controller: _lastNameController,
                          focusNode: _lastNameFocusNode,
                          label: _tr('الاسم الأخير', 'Last Name'),
                          hint: _tr('أحمد', 'Ahmed'),
                          icon: Icons.person_outline,
                          validator: (v) => _validateName(v, false),
                          textInputAction: TextInputAction.next,
                          onFieldSubmitted: (_) =>
                              _emailFocusNode.requestFocus(),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Email field
                  _buildTextField(
                    controller: _emailController,
                    focusNode: _emailFocusNode,
                    label: _tr('البريد الإلكتروني', 'Email'),
                    hint: _tr('example@mail.com', 'example@mail.com'),
                    icon: Icons.email_outlined,
                    keyboardType: TextInputType.emailAddress,
                    validator: _validateEmail,
                    textInputAction: TextInputAction.next,
                    onFieldSubmitted: (_) => _phoneFocusNode.requestFocus(),
                  ),

                  const SizedBox(height: 20),

                  // Phone field (optional)
                  _buildPhoneField(),

                  const SizedBox(height: 20),

                  // Password field
                  _buildTextField(
                    controller: _passwordController,
                    focusNode: _passwordFocusNode,
                    label: _tr('كلمة المرور', 'Password'),
                    hint: _tr('أدخل كلمة المرور', 'Enter password'),
                    icon: Icons.lock_outline,
                    obscureText: _obscurePassword,
                    validator: _validatePassword,
                    textInputAction: TextInputAction.next,
                    onFieldSubmitted: (_) =>
                        _confirmPasswordFocusNode.requestFocus(),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword
                            ? Icons.visibility_off_outlined
                            : Icons.visibility_outlined,
                        color: Colors.grey[600],
                      ),
                      onPressed: () =>
                          setState(() => _obscurePassword = !_obscurePassword),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Confirm password field
                  _buildTextField(
                    controller: _confirmPasswordController,
                    focusNode: _confirmPasswordFocusNode,
                    label: _tr('تأكيد كلمة المرور', 'Confirm Password'),
                    hint: _tr('أعد إدخال كلمة المرور', 'Re-enter password'),
                    icon: Icons.lock_outline,
                    obscureText: _obscureConfirmPassword,
                    validator: _validateConfirmPassword,
                    textInputAction: TextInputAction.done,
                    onFieldSubmitted: (_) => _register(),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscureConfirmPassword
                            ? Icons.visibility_off_outlined
                            : Icons.visibility_outlined,
                        color: Colors.grey[600],
                      ),
                      onPressed: () => setState(
                          () => _obscureConfirmPassword = !_obscureConfirmPassword),
                    ),
                  ),

                  const SizedBox(height: 12),

                  // Password requirements hint
                  _buildPasswordHint(),

                  const SizedBox(height: 32),

                  // Register button
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _register,
                      child: _isLoading
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 2,
                              ),
                            )
                          : Text(
                              _tr('إنشاء الحساب', 'Create Account'),
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Login link
                  Center(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          _tr('لديك حساب بالفعل؟', 'Already have an account?'),
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                        TextButton(
                          onPressed: () => context.go('/login'),
                          child: Text(
                            _tr('تسجيل الدخول', 'Sign In'),
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Help text
                  Center(
                    child: TextButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.help_outline, size: 20),
                      label: Text(_tr('تحتاج مساعدة؟', 'Need help?')),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLanguageToggle() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(25),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          GestureDetector(
            onTap: () => setState(() => _isArabic = true),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: _isArabic ? SahoolColors.primary : Colors.transparent,
                borderRadius: BorderRadius.circular(25),
              ),
              child: Text(
                'عربي',
                style: TextStyle(
                  color: _isArabic ? Colors.white : Colors.grey[600],
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          GestureDetector(
            onTap: () => setState(() => _isArabic = false),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: !_isArabic ? SahoolColors.primary : Colors.transparent,
                borderRadius: BorderRadius.circular(25),
              ),
              child: Text(
                'EN',
                style: TextStyle(
                  color: !_isArabic ? Colors.white : Colors.grey[600],
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required FocusNode focusNode,
    required String label,
    required String hint,
    required IconData icon,
    TextInputType keyboardType = TextInputType.text,
    bool obscureText = false,
    String? Function(String?)? validator,
    TextInputAction textInputAction = TextInputAction.next,
    void Function(String)? onFieldSubmitted,
    Widget? suffixIcon,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          focusNode: focusNode,
          keyboardType: keyboardType,
          obscureText: obscureText,
          validator: validator,
          textInputAction: textInputAction,
          onFieldSubmitted: onFieldSubmitted,
          style: const TextStyle(fontSize: 16),
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: Icon(icon, color: Colors.grey[600]),
            suffixIcon: suffixIcon,
            filled: true,
            fillColor: Colors.grey[100],
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: SahoolColors.primary, width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: SahoolColors.danger, width: 2),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: SahoolColors.danger, width: 2),
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

  Widget _buildPhoneField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              _tr('رقم الهاتف', 'Phone Number'),
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                _tr('اختياري', 'Optional'),
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey[600],
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[300]!),
          ),
          child: Row(
            children: [
              // Country code
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                decoration: BoxDecoration(
                  border: Border(
                    left: BorderSide(color: Colors.grey[300]!),
                  ),
                ),
                child: Row(
                  children: [
                    const Text(
                      '967+',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Icon(Icons.arrow_drop_down, color: Colors.grey[600]),
                  ],
                ),
              ),
              // Phone input
              Expanded(
                child: TextFormField(
                  controller: _phoneController,
                  focusNode: _phoneFocusNode,
                  keyboardType: TextInputType.phone,
                  textInputAction: TextInputAction.next,
                  onFieldSubmitted: (_) => _passwordFocusNode.requestFocus(),
                  style: const TextStyle(
                    fontSize: 16,
                    letterSpacing: 1,
                  ),
                  decoration: InputDecoration(
                    hintText: _tr('7XX XXX XXX', '7XX XXX XXX'),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                  ),
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                    LengthLimitingTextInputFormatter(9),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPasswordHint() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: SahoolColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: SahoolColors.info.withOpacity(0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.info_outline,
            size: 20,
            color: SahoolColors.info,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _tr('متطلبات كلمة المرور:', 'Password requirements:'),
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: SahoolColors.info,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _tr(
                    '8 أحرف على الأقل، حرف كبير واحد، رقم واحد',
                    'At least 8 characters, 1 uppercase letter, 1 number',
                  ),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[700],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
