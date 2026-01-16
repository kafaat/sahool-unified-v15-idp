import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/security/screen_security_service.dart';
import '../../../core/security/security_config.dart';

/// OTP Login Screen - تسجيل الدخول برقم الهاتف
/// تصميم بسيط للمزارعين الذين لا يحفظون كلمات المرور
class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _phoneController = TextEditingController();
  final List<TextEditingController> _otpControllers = List.generate(
    4,
    (_) => TextEditingController(),
  );
  final List<FocusNode> _otpFocusNodes = List.generate(4, (_) => FocusNode());

  bool _isOtpSent = false;
  bool _isLoading = false;
  int _resendTimer = 0;

  @override
  void dispose() {
    _phoneController.dispose();
    for (var controller in _otpControllers) {
      controller.dispose();
    }
    for (var node in _otpFocusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  void _sendOtp() async {
    if (_phoneController.text.length < 9) return;

    setState(() => _isLoading = true);

    // Simulate API call
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _isLoading = false;
      _isOtpSent = true;
      _resendTimer = 60;
    });

    // Start countdown
    _startResendTimer();

    // Focus first OTP field
    _otpFocusNodes[0].requestFocus();
  }

  void _startResendTimer() {
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 1));
      if (mounted && _resendTimer > 0) {
        setState(() => _resendTimer--);
        return true;
      }
      return false;
    });
  }

  void _verifyOtp() async {
    final otp = _otpControllers.map((c) => c.text).join();
    if (otp.length != 4) return;

    setState(() => _isLoading = true);

    // Simulate verification
    await Future.delayed(const Duration(seconds: 1));

    if (mounted) {
      context.go('/map');
    }
  }

  void _onOtpChanged(int index, String value) {
    if (value.isNotEmpty && index < 3) {
      _otpFocusNodes[index + 1].requestFocus();
    }
    if (value.isEmpty && index > 0) {
      _otpFocusNodes[index - 1].requestFocus();
    }

    // Auto verify when all digits entered
    final otp = _otpControllers.map((c) => c.text).join();
    if (otp.length == 4) {
      _verifyOtp();
    }
  }

  @override
  Widget build(BuildContext context) {
    return SecureScreen(
      screenType: SecuredScreenType.authentication,
      showWarning: ref.watch(securityConfigProvider).showScreenSecurityWarning,
      warningMessageAr: 'لا يمكن أخذ لقطات شاشة في شاشة تسجيل الدخول لحماية بياناتك',
      warningMessageEn: 'Screenshots are disabled on login screen to protect your credentials',
      child: Scaffold(
        body: SafeArea(
          child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Back button
              IconButton(
                onPressed: () => _isOtpSent
                    ? setState(() => _isOtpSent = false)
                    : context.go('/role-selection'),
                icon: const Icon(Icons.arrow_back),
                style: IconButton.styleFrom(
                  backgroundColor: Colors.grey[100],
                ),
              ),

              const SizedBox(height: 40),

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
                      child: Icon(
                        _isOtpSent ? Icons.sms : Icons.phone_android,
                        size: 40,
                        color: SahoolColors.primary,
                      ),
                    ),
                    const SizedBox(height: 24),
                    Text(
                      _isOtpSent ? 'أدخل رمز التحقق' : 'تسجيل الدخول',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _isOtpSent
                          ? 'تم إرسال رمز مكون من 4 أرقام إلى\n${_phoneController.text}'
                          : 'أدخل رقم هاتفك للمتابعة',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[600],
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 48),

              // Phone or OTP input
              if (!_isOtpSent) _buildPhoneInput() else _buildOtpInput(),

              const SizedBox(height: 32),

              // Action button
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _isLoading
                      ? null
                      : (_isOtpSent ? _verifyOtp : _sendOtp),
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
                          _isOtpSent ? 'تحقق' : 'أرسل الرمز',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),

              // Resend OTP
              if (_isOtpSent) ...[
                const SizedBox(height: 24),
                Center(
                  child: _resendTimer > 0
                      ? Text(
                          'إعادة الإرسال بعد $_resendTimer ثانية',
                          style: TextStyle(color: Colors.grey[600]),
                        )
                      : TextButton(
                          onPressed: () {
                            setState(() => _isOtpSent = false);
                            _sendOtp();
                          },
                          child: const Text(
                            'إعادة إرسال الرمز',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                ),
              ],

              const SizedBox(height: 32),

              // Register link
              Center(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'ليس لديك حساب؟',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                    TextButton(
                      onPressed: () => context.go('/register'),
                      child: const Text(
                        'إنشاء حساب',
                        style: TextStyle(fontWeight: FontWeight.bold),
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
                  label: const Text('تحتاج مساعدة؟'),
                ),
              ),
            ],
          ),
        ),
      ),
    ),
    );
  }

  Widget _buildPhoneInput() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Row(
        children: [
          // Country code
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
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
                Icon(Icons.arrow_drop_down, color: Colors.grey[600]),
              ],
            ),
          ),
          // Phone input
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
                contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 20),
              ),
              inputFormatters: [
                FilteringTextInputFormatter.digitsOnly,
                LengthLimitingTextInputFormatter(9),
              ],
              onChanged: (_) => setState(() {}),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOtpInput() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(4, (index) {
        return Container(
          width: 64,
          height: 72,
          margin: const EdgeInsets.symmetric(horizontal: 8),
          child: TextField(
            controller: _otpControllers[index],
            focusNode: _otpFocusNodes[index],
            keyboardType: TextInputType.number,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
            decoration: InputDecoration(
              filled: true,
              fillColor: Colors.grey[100],
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
                borderSide: BorderSide(color: Colors.grey[300]!),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
                borderSide: const BorderSide(color: SahoolColors.primary, width: 2),
              ),
              contentPadding: const EdgeInsets.symmetric(vertical: 20),
            ),
            inputFormatters: [
              FilteringTextInputFormatter.digitsOnly,
              LengthLimitingTextInputFormatter(1),
            ],
            onChanged: (value) => _onOtpChanged(index, value),
          ),
        );
      }),
    );
  }
}
