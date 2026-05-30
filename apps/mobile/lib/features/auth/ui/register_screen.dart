import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/auth/auth_service.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/utils/app_logger.dart';
import '../../../core/utils/input_validator.dart';

/// شاشة إنشاء حساب جديد
class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen>
    with SingleTickerProviderStateMixin {
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  late final TabController _tabController;

  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  String? _firstNameError;
  String? _lastNameError;
  String? _emailError;
  String? _phoneError;
  String? _passwordError;
  String? _confirmPasswordError;
  String? _generalError;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  // التحقق من صحة البيانات
  bool _validate() {
    bool valid = true;

    // الاسم الأول
    final firstName = _firstNameController.text.trim();
    if (firstName.isEmpty) {
      _firstNameError = 'الاسم الأول مطلوب';
      valid = false;
    } else if (firstName.length < 2) {
      _firstNameError = 'الاسم الأول يجب أن يكون حرفين على الأقل';
      valid = false;
    } else {
      _firstNameError = null;
    }

    // اسم العائلة
    final lastName = _lastNameController.text.trim();
    if (lastName.isEmpty) {
      _lastNameError = 'اسم العائلة مطلوب';
      valid = false;
    } else if (lastName.length < 2) {
      _lastNameError = 'اسم العائلة يجب أن يكون حرفين على الأقل';
      valid = false;
    } else {
      _lastNameError = null;
    }

    // البريد الإلكتروني أو رقم الهاتف حسب التبويب المحدد
    if (_tabController.index == 0) {
      // تبويب البريد الإلكتروني
      final email = _emailController.text.trim();
      if (email.isEmpty) {
        _emailError = 'البريد الإلكتروني مطلوب';
        valid = false;
      } else if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(email)) {
        _emailError = 'البريد الإلكتروني غير صالح';
        valid = false;
      } else {
        _emailError = null;
      }
      _phoneError = null;
    } else {
      // تبويب رقم الهاتف
      final phone = _phoneController.text.trim();
      if (phone.isEmpty) {
        _phoneError = 'رقم الهاتف مطلوب';
        valid = false;
      } else if (!RegExp(r'^(77|78|71|73|70)\d{7}$').hasMatch(phone)) {
        _phoneError = 'رقم الهاتف غير صالح (مثال: 77XXXXXXX)';
        valid = false;
      } else {
        _phoneError = null;
      }
      _emailError = null;
    }

    // كلمة المرور
    final password = _passwordController.text;
    if (password.isEmpty) {
      _passwordError = 'كلمة المرور مطلوبة';
      valid = false;
    } else if (password.length < 8) {
      _passwordError = 'كلمة المرور يجب أن تكون ٨ أحرف على الأقل';
      valid = false;
    } else if (!password.contains(RegExp(r'[A-Z]'))) {
      _passwordError = 'كلمة المرور يجب أن تحتوي على حرف كبير';
      valid = false;
    } else if (!password.contains(RegExp(r'[a-z]'))) {
      _passwordError = 'كلمة المرور يجب أن تحتوي على حرف صغير';
      valid = false;
    } else if (!password.contains(RegExp(r'[0-9]'))) {
      _passwordError = 'كلمة المرور يجب أن تحتوي على رقم';
      valid = false;
    } else {
      _passwordError = null;
    }

    // تأكيد كلمة المرور
    final confirmPassword = _confirmPasswordController.text;
    if (confirmPassword.isEmpty) {
      _confirmPasswordError = 'تأكيد كلمة المرور مطلوب';
      valid = false;
    } else if (confirmPassword != password) {
      _confirmPasswordError = 'كلمة المرور غير متطابقة';
      valid = false;
    } else {
      _confirmPasswordError = null;
    }

    setState(() {});
    return valid;
  }

  Future<void> _register() async {
    setState(() {
      _generalError = null;
    });

    if (!_validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final authService = ref.read(authServiceProvider);
      final isEmailTab = _tabController.index == 0;

      await authService.register(
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        email: isEmailTab ? _emailController.text.trim() : null,
        phone: isEmailTab ? null : _phoneController.text.trim(),
        password: _passwordController.text,
      );

      AppLogger.i('Register successful', tag: 'REGISTER');

      if (mounted) {
        context.go('/home');
      }
    } on AuthException catch (e) {
      AppLogger.e('Register failed', tag: 'REGISTER', error: e);
      if (mounted) {
        setState(() {
          _isLoading = false;
          _generalError = e.message;
        });
      }
    } catch (e) {
      AppLogger.e('Register unexpected error', tag: 'REGISTER', error: e);
      if (mounted) {
        setState(() {
          _isLoading = false;
          _generalError = 'حدث خطأ أثناء إنشاء الحساب. يرجى المحاولة مجدداً';
        });
      }
    }
  }

  /// عرض رسالة اليمن فقط عند الضغط على رمز البلد
  void _showCountryCodeInfo() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('التطبيق يدعم حالياً أرقام الهواتف اليمنية فقط (+967)'),
        behavior: SnackBarBehavior.floating,
        duration: Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // زر العودة
                IconButton(
                  onPressed: () => context.go('/login'),
                  icon: const Icon(Icons.arrow_back),
                  style: IconButton.styleFrom(
                    backgroundColor: Colors.grey[100],
                  ),
                ),

                const SizedBox(height: 32),

                // الأيقونة والعنوان
                Center(
                  child: Column(
                    children: [
                      Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: SahoolColors.primary.withValues(alpha: 0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.person_add,
                          size: 40,
                          color: SahoolColors.primary,
                        ),
                      ),
                      const SizedBox(height: 24),
                      const Text(
                        'إنشاء حساب جديد',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 32),

                // تبويبات البريد الإلكتروني / رقم الهاتف
                Container(
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: TabBar(
                    controller: _tabController,
                    onTap: (_) => setState(() {
                      _emailError = null;
                      _phoneError = null;
                    }),
                    indicator: BoxDecoration(
                      color: SahoolColors.primary,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    labelColor: Colors.white,
                    unselectedLabelColor: Colors.grey[700],
                    dividerColor: Colors.transparent,
                    tabs: const [
                      Tab(text: 'البريد الإلكتروني'),
                      Tab(text: 'رقم الهاتف'),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // الاسم الأول
                _buildTextField(
                  controller: _firstNameController,
                  label: 'الاسم الأول',
                  hint: 'أحمد',
                  icon: Icons.person_outline,
                  errorText: _firstNameError,
                  onChanged: (_) => setState(() => _firstNameError = null),
                ),

                const SizedBox(height: 16),

                // اسم العائلة
                _buildTextField(
                  controller: _lastNameController,
                  label: 'اسم العائلة',
                  hint: 'محمد',
                  icon: Icons.person_outline,
                  errorText: _lastNameError,
                  onChanged: (_) => setState(() => _lastNameError = null),
                ),

                const SizedBox(height: 16),

                // محتوى التبويب (بريد / هاتف)
                // TabBarView needs a bounded height inside Column+SingleChildScrollView
                SizedBox(
                  height: 95,
                  child: TabBarView(
                    controller: _tabController,
                    physics: const NeverScrollableScrollPhysics(),
                    children: [
                      // تبويب البريد الإلكتروني
                      _buildTextField(
                        controller: _emailController,
                        label: 'البريد الإلكتروني',
                        hint: 'example@email.com',
                        icon: Icons.email_outlined,
                        keyboardType: TextInputType.emailAddress,
                        errorText: _emailError,
                        onChanged: (_) => setState(() => _emailError = null),
                      ),

                      // تبويب رقم الهاتف
                      _buildPhoneInput(),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // كلمة المرور
                _buildPasswordField(
                  controller: _passwordController,
                  label: 'كلمة المرور',
                  hint: '••••••••',
                  errorText: _passwordError,
                  obscure: _obscurePassword,
                  onToggleObscure: () =>
                      setState(() => _obscurePassword = !_obscurePassword),
                  onChanged: (_) => setState(() => _passwordError = null),
                ),

                const SizedBox(height: 8),

                // تلميح متطلبات كلمة المرور
                Text(
                  '٨ أحرف على الأقل، حرف كبير، حرف صغير، رقم',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),

                const SizedBox(height: 16),

                // تأكيد كلمة المرور
                _buildPasswordField(
                  controller: _confirmPasswordController,
                  label: 'تأكيد كلمة المرور',
                  hint: '••••••••',
                  errorText: _confirmPasswordError,
                  obscure: _obscureConfirmPassword,
                  onToggleObscure: () => setState(
                      () => _obscureConfirmPassword = !_obscureConfirmPassword),
                  onChanged: (_) =>
                      setState(() => _confirmPasswordError = null),
                ),

                // رسالة خطأ عامة
                if (_generalError != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red[50],
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.red[200]!),
                    ),
                    child: Text(
                      _generalError!,
                      style: const TextStyle(color: Colors.red, fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],

                const SizedBox(height: 32),

                // زر إنشاء الحساب
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
                        : const Text(
                            'إنشاء الحساب',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                  ),
                ),

                const SizedBox(height: 24),

                // رابط تسجيل الدخول
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'لديك حساب بالفعل؟',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                    TextButton(
                      onPressed: () => context.push('/login'),
                      child: const Text(
                        'تسجيل الدخول',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// حقل إدخال هاتف اليمن بنفس نمط login_screen.dart
  Widget _buildPhoneInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DecoratedBox(
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: _phoneError != null ? Colors.red : Colors.grey[300]!,
            ),
          ),
          child: Row(
            children: [
              // رمز البلد - اليمن فقط
              GestureDetector(
                onTap: _showCountryCodeInfo,
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                  decoration: BoxDecoration(
                    border: Border(
                      left: BorderSide(color: Colors.grey[300]!),
                    ),
                  ),
                  child: Row(
                    children: [
                      const Text(
                        '🇾🇪',
                        style: TextStyle(fontSize: 24),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '+967',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[700],
                        ),
                      ),
                      const SizedBox(width: 2),
                      Icon(Icons.info_outline,
                          color: Colors.grey[500], size: 16),
                    ],
                  ),
                ),
              ),
              // حقل رقم الهاتف
              Expanded(
                child: TextField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                  decoration: const InputDecoration(
                    hintText: '7XX XXX XXX',
                    border: InputBorder.none,
                    contentPadding:
                        EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                  ),
                  inputFormatters: InputValidator.phoneFormatters(maxLength: 9),
                  onChanged: (_) => setState(() => _phoneError = null),
                ),
              ),
            ],
          ),
        ),
        if (_phoneError != null) ...[
          const SizedBox(height: 8),
          Text(
            _phoneError!,
            style: const TextStyle(color: Colors.red, fontSize: 14),
          ),
        ],
      ],
    );
  }

  /// حقل إدخال نصي عام
  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    String? errorText,
    TextInputType keyboardType = TextInputType.text,
    void Function(String)? onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: controller,
          keyboardType: keyboardType,
          onChanged: onChanged,
          decoration: InputDecoration(
            labelText: label,
            hintText: hint,
            prefixIcon: Icon(icon),
            filled: true,
            fillColor: Colors.grey[100],
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide(
                color: errorText != null ? Colors.red : Colors.grey[300]!,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide(
                color: errorText != null ? Colors.red : SahoolColors.primary,
                width: 2,
              ),
            ),
            errorText: errorText,
          ),
        ),
      ],
    );
  }

  /// حقل كلمة المرور مع زر إظهار/إخفاء
  Widget _buildPasswordField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required bool obscure,
    required VoidCallback onToggleObscure,
    String? errorText,
    void Function(String)? onChanged,
  }) {
    return TextField(
      controller: controller,
      obscureText: obscure,
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: const Icon(Icons.lock_outline),
        suffixIcon: IconButton(
          icon: Icon(obscure ? Icons.visibility_off : Icons.visibility),
          onPressed: onToggleObscure,
        ),
        filled: true,
        fillColor: Colors.grey[100],
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: errorText != null ? Colors.red : Colors.grey[300]!,
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: errorText != null ? Colors.red : SahoolColors.primary,
            width: 2,
          ),
        ),
        errorText: errorText,
      ),
    );
  }
}
