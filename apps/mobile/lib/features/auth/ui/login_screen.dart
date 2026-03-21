import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/auth/auth_service.dart';
import '../../../core/auth/biometric_service.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/utils/app_logger.dart';
import '../../../core/utils/input_validator.dart';
import '../services/otp_service.dart';
import 'biometric_login_widget.dart';

/// OTP Login Screen - تسجيل الدخول برقم الهاتف
/// تصميم بسيط للمزارعين الذين لا يحفظون كلمات المرور
/// يدعم تسجيل الدخول بالبصمة إذا كانت مفعّلة
class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _phoneController = TextEditingController();
  final List<TextEditingController> _otpControllers = List.generate(
    6,
    (_) => TextEditingController(),
  );
  final List<FocusNode> _otpFocusNodes = List.generate(6, (_) => FocusNode());

  bool _isOtpSent = false;
  bool _isLoading = false;
  int _resendTimer = 0;
  Timer? _resendCountdownTimer;
  String? _phoneErrorMessage;
  String? _otpErrorMessage;

  // Biometric state
  bool _isBiometricAvailable = false;
  bool _isBiometricEnabled = false;

  @override
  void initState() {
    super.initState();
    _checkBiometricStatus();
  }

  Future<void> _checkBiometricStatus() async {
    final biometricService = ref.read(biometricServiceProvider);
    final available = await biometricService.isAvailable();
    final enabled = await biometricService.isEnabled();

    if (mounted) {
      setState(() {
        _isBiometricAvailable = available;
        _isBiometricEnabled = enabled;
      });

      // Auto-trigger biometric if available and enabled
      if (available && enabled) {
        _authenticateWithBiometric();
      }
    }
  }

  Future<void> _authenticateWithBiometric() async {
    try {
      // تسجيل الدخول بالبصمة مع استرجاع التوكن عبر AuthService
      final authService = ref.read(authServiceProvider);
      final user = await authService.loginWithBiometric();

      if (user != null && mounted) {
        context.go('/map');
      }
    } on AuthException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.message),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } on BiometricException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.message),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      // Silent fail - user can use phone/OTP
      AppLogger.w('Biometric auto-login failed', tag: 'LOGIN');
    }
  }

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

  Future<void> _sendOtp() async {
    // Validate phone number
    final validation = InputValidator.validateYemenPhone(_phoneController.text);

    if (!validation.isValid) {
      setState(() {
        _phoneErrorMessage = validation.errorMessageAr;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _phoneErrorMessage = null;
    });

    try {
      // إرسال رمز التحقق عبر خدمة OTP الفعلية
      final otpService = ref.read(otpServiceProvider);
      final phoneWithCode = '+967${_phoneController.text}';
      final result = await otpService.sendOTP(
        identifier: phoneWithCode,
        channel: OTPChannel.sms,
        purpose: OTPPurpose.phoneVerification,
      );

      result.when(
        success: (response) {
          if (mounted) {
            setState(() {
              _isLoading = false;
              _isOtpSent = true;
              _resendTimer = response.cooldownSeconds ?? 60;
            });

            // Start countdown
            _startResendTimer();

            // Focus first OTP field
            _otpFocusNodes[0].requestFocus();
          }
        },
        failure: (message, statusCode) {
          if (mounted) {
            setState(() {
              _isLoading = false;
              _phoneErrorMessage = message;
            });
          }
        },
      );
    } catch (e) {
      AppLogger.e('OTP send failed', error: e, tag: 'LOGIN');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _phoneErrorMessage = 'حدث خطأ أثناء إرسال رمز التحقق';
        });
      }
    }
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

  Future<void> _verifyOtp() async {
    final otp = _otpControllers.map((c) => c.text).join();

    // Validate OTP - 6 أرقام
    final validation = InputValidator.validateOtp(otp, length: 6);

    if (!validation.isValid) {
      setState(() {
        _otpErrorMessage = validation.errorMessageAr;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _otpErrorMessage = null;
    });

    try {
      // التحقق من رمز OTP عبر الخدمة الفعلية
      final otpService = ref.read(otpServiceProvider);
      final phoneWithCode = '+967${_phoneController.text}';
      final result = await otpService.verifyOTP(
        identifier: phoneWithCode,
        otp: otp,
        purpose: OTPPurpose.phoneVerification,
      );

      result.when(
        success: (response) async {
          // تسجيل الدخول باستخدام AuthService وتخزين التوكن
          try {
            final authService = ref.read(authServiceProvider);
            // Use phone login - the backend issues tokens after OTP verification
            final user = await authService.login(phoneWithCode, otp);
            AppLogger.i('Login successful', tag: 'LOGIN', data: {'userId': user.id});

            if (mounted) {
              setState(() => _isLoading = false);
              context.go('/map');
            }
          } on AuthException catch (e) {
            AppLogger.e('Auth after OTP failed', error: e, tag: 'LOGIN');
            if (mounted) {
              setState(() {
                _isLoading = false;
                _otpErrorMessage = e.message;
              });
            }
          }
        },
        failure: (message, statusCode) {
          if (mounted) {
            setState(() {
              _isLoading = false;
              _otpErrorMessage = message;
            });
            // مسح حقول OTP عند الخطأ
            for (final controller in _otpControllers) {
              controller.clear();
            }
            _otpFocusNodes[0].requestFocus();
          }
        },
      );
    } catch (e) {
      AppLogger.e('OTP verification failed', error: e, tag: 'LOGIN');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _otpErrorMessage = 'حدث خطأ أثناء التحقق من الرمز';
        });
      }
    }
  }

  void _onOtpChanged(int index, String value) {
    // Clear error message when user types
    if (_otpErrorMessage != null) {
      setState(() {
        _otpErrorMessage = null;
      });
    }

    if (value.isNotEmpty && index < 5) {
      _otpFocusNodes[index + 1].requestFocus();
    }
    if (value.isEmpty && index > 0) {
      _otpFocusNodes[index - 1].requestFocus();
    }

    // Auto verify when all 6 digits entered
    final otp = _otpControllers.map((c) => c.text).join();
    if (otp.length == 6) {
      _verifyOtp();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
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
                          ? 'تم إرسال رمز مكون من 6 أرقام إلى\n${_phoneController.text}'
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

              // Biometric login option
              if (_isBiometricAvailable && _isBiometricEnabled && !_isOtpSent)
                BiometricLoginWidget(
                  onSuccess: () async {
                    // تسجيل الدخول بالبصمة مع استرجاع التوكن
                    try {
                      final authService = ref.read(authServiceProvider);
                      await authService.loginWithBiometric();
                      if (mounted) {
                        context.go('/map');
                      }
                    } on AuthException catch (e) {
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(e.message),
                            backgroundColor: Colors.red,
                            behavior: SnackBarBehavior.floating,
                          ),
                        );
                      }
                    } catch (e) {
                      AppLogger.e('Biometric login failed', error: e, tag: 'LOGIN');
                    }
                  },
                ),

              const SizedBox(height: 24),

              // Help text - نص المساعدة
              Center(
                child: TextButton.icon(
                  onPressed: () => _showHelpDialog(),
                  icon: const Icon(Icons.help_outline, size: 20),
                  label: const Text('تحتاج مساعدة؟'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// عرض نافذة المساعدة
  void _showHelpDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: const Row(
          children: [
            Icon(Icons.help_outline, color: SahoolColors.primary),
            SizedBox(width: 8),
            Text('المساعدة'),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'كيفية تسجيل الدخول:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text('1. أدخل رقم هاتفك اليمني (9 أرقام تبدأ بـ 7)'),
            SizedBox(height: 4),
            Text('2. اضغط "أرسل الرمز"'),
            SizedBox(height: 4),
            Text('3. أدخل رمز التحقق المكون من 6 أرقام'),
            SizedBox(height: 16),
            Text(
              'للتواصل مع الدعم الفني:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text('البريد: support@sahool.app'),
            Text('الهاتف: +967-1-XXX-XXX'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('حسناً'),
          ),
        ],
      ),
    );
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

  Widget _buildPhoneInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: _phoneErrorMessage != null
                  ? Colors.red
                  : Colors.grey[300]!,
            ),
          ),
          child: Row(
            children: [
              // Country code - اليمن فقط
              GestureDetector(
                onTap: _showCountryCodeInfo,
                child: Container(
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
                      const SizedBox(width: 2),
                      Icon(Icons.info_outline, color: Colors.grey[500], size: 16),
                    ],
                  ),
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
                  inputFormatters: InputValidator.phoneFormatters(maxLength: 9),
                  onChanged: (_) => setState(() {
                    // Clear error message when user types
                    _phoneErrorMessage = null;
                  }),
                ),
              ),
            ],
          ),
        ),
        // Error message
        if (_phoneErrorMessage != null) ...[
          const SizedBox(height: 8),
          Text(
            _phoneErrorMessage!,
            style: const TextStyle(
              color: Colors.red,
              fontSize: 14,
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildOtpInput() {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(6, (index) {
            return Container(
              width: 48,
              height: 64,
              margin: const EdgeInsets.symmetric(horizontal: 4),
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
                    borderSide: BorderSide(
                      color: _otpErrorMessage != null
                          ? Colors.red
                          : Colors.grey[300]!,
                    ),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(
                      color: _otpErrorMessage != null
                          ? Colors.red
                          : SahoolColors.primary,
                      width: 2,
                    ),
                  ),
                  errorBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Colors.red, width: 2),
                  ),
                  contentPadding: const EdgeInsets.symmetric(vertical: 20),
                ),
                inputFormatters: InputValidator.otpFormatters(length: 1),
                onChanged: (value) => _onOtpChanged(index, value),
              ),
            );
          }),
        ),
        // Error message
        if (_otpErrorMessage != null) ...[
          const SizedBox(height: 16),
          Text(
            _otpErrorMessage!,
            style: const TextStyle(
              color: Colors.red,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ],
    );
  }
}
