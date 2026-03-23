import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/auth/auth_service.dart';
import '../../../core/auth/biometric_service.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/utils/app_logger.dart';
import '../../../core/utils/input_validator.dart';
import '../services/otp_service.dart';
import 'biometric_login_widget.dart';

/// Supported country for phone login
/// البلد المدعوم لتسجيل الدخول بالهاتف
class SupportedCountry {
  final String code;
  final String dialCode;
  final String flag;
  final String nameAr;
  final String nameEn;
  final String hintText;
  final int phoneLength;

  const SupportedCountry({
    required this.code,
    required this.dialCode,
    required this.flag,
    required this.nameAr,
    required this.nameEn,
    required this.hintText,
    required this.phoneLength,
  });

  String get displayName => '$nameAr / $nameEn';
}

/// List of supported countries - البلدان المدعومة
const List<SupportedCountry> supportedCountries = [
  SupportedCountry(
    code: 'YE',
    dialCode: '+967',
    flag: '\u{1F1FE}\u{1F1EA}',
    nameAr: 'اليمن',
    nameEn: 'Yemen',
    hintText: '7XX XXX XXX',
    phoneLength: 9,
  ),
  SupportedCountry(
    code: 'SA',
    dialCode: '+966',
    flag: '\u{1F1F8}\u{1F1E6}',
    nameAr: 'السعودية',
    nameEn: 'Saudi Arabia',
    hintText: '5XX XXX XXX',
    phoneLength: 9,
  ),
  SupportedCountry(
    code: 'IQ',
    dialCode: '+964',
    flag: '\u{1F1EE}\u{1F1F6}',
    nameAr: 'العراق',
    nameEn: 'Iraq',
    hintText: '7XXX XXX XXXX',
    phoneLength: 10,
  ),
  SupportedCountry(
    code: 'EG',
    dialCode: '+20',
    flag: '\u{1F1EA}\u{1F1EC}',
    nameAr: 'مصر',
    nameEn: 'Egypt',
    hintText: '1XX XXXX XXXX',
    phoneLength: 10,
  ),
  SupportedCountry(
    code: 'JO',
    dialCode: '+962',
    flag: '\u{1F1EF}\u{1F1F4}',
    nameAr: 'الأردن',
    nameEn: 'Jordan',
    hintText: '7XX XXX XXXX',
    phoneLength: 9,
  ),
  SupportedCountry(
    code: 'AE',
    dialCode: '+971',
    flag: '\u{1F1E6}\u{1F1EA}',
    nameAr: 'الإمارات',
    nameEn: 'UAE',
    hintText: '5XX XXX XXXX',
    phoneLength: 9,
  ),
];

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

  // Selected country - default Yemen
  SupportedCountry _selectedCountry = supportedCountries.first;

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
        unawaited(_authenticateWithBiometric());
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
    _resendCountdownTimer?.cancel();
    _resendCountdownTimer = null;
    _phoneController.dispose();
    for (final controller in _otpControllers) {
      controller.dispose();
    }
    for (final node in _otpFocusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  Future<void> _sendOtp() async {
    // Validate phone number per selected country
    final validation = InputValidator.validateInternationalPhone(
      _phoneController.text,
      _selectedCountry.dialCode,
    );

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
      final phoneWithCode = '${_selectedCountry.dialCode}${_phoneController.text}';
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
    _resendCountdownTimer?.cancel();
    _resendCountdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted || _resendTimer <= 0) {
        timer.cancel();
        return;
      }
      setState(() => _resendTimer--);
      if (_resendTimer <= 0) {
        timer.cancel();
      }
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
      final phoneWithCode = '${_selectedCountry.dialCode}${_phoneController.text}';
      final result = await otpService.verifyOTP(
        identifier: phoneWithCode,
        otp: otp,
        purpose: OTPPurpose.phoneVerification,
      );

      await result.when(
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
                        color: SahoolColors.primary.withValues(alpha: 0.1),
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
                      if (context.mounted) {
                        context.go('/map');
                      }
                    } on AuthException catch (e) {
                      if (context.mounted) {
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
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'كيفية تسجيل الدخول:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text('1. اختر بلدك من قائمة رموز البلدان'),
            const SizedBox(height: 4),
            Text('2. أدخل رقم هاتفك (${_selectedCountry.phoneLength} أرقام)'),
            const SizedBox(height: 4),
            const Text('3. اضغط "أرسل الرمز"'),
            const SizedBox(height: 4),
            const Text('4. أدخل رمز التحقق المكون من 6 أرقام'),
            const SizedBox(height: 16),
            const Text(
              'البلدان المدعومة:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            ...supportedCountries.map((c) => Text(
              '${c.flag} ${c.nameAr} (${c.dialCode})',
            )),
            const SizedBox(height: 16),
            const Text(
              'للتواصل مع الدعم الفني:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text('البريد: support@sahool.app'),
            const Text('الهاتف: +967-1-XXX-XXX'),
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

  /// عرض قائمة البلدان المدعومة
  void _showCountrySelector() {
    showModalBottomSheet<SupportedCountry>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'اختر البلد / Select Country',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const Divider(height: 1),
            ...supportedCountries.map((country) => ListTile(
              leading: Text(country.flag, style: const TextStyle(fontSize: 28)),
              title: Text(
                '${country.nameAr} / ${country.nameEn}',
                style: const TextStyle(fontSize: 16),
              ),
              trailing: Text(
                country.dialCode,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: country.code == _selectedCountry.code
                      ? SahoolColors.primary
                      : Colors.grey[600],
                ),
              ),
              selected: country.code == _selectedCountry.code,
              selectedTileColor: SahoolColors.primary.withValues(alpha: 0.08),
              onTap: () {
                Navigator.of(context).pop(country);
              },
            )),
            const SizedBox(height: 8),
          ],
        ),
      ),
    ).then((selected) {
      if (selected != null && selected.code != _selectedCountry.code) {
        setState(() {
          _selectedCountry = selected;
          _phoneController.clear();
          _phoneErrorMessage = null;
        });
      }
    });
  }

  Widget _buildPhoneInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DecoratedBox(
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
              // Country code selector - اختيار البلد
              GestureDetector(
                onTap: _showCountrySelector,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 20),
                  decoration: BoxDecoration(
                    border: Border(
                      left: BorderSide(color: Colors.grey[300]!),
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _selectedCountry.flag,
                        style: const TextStyle(fontSize: 24),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        _selectedCountry.dialCode,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[700],
                        ),
                      ),
                      const SizedBox(width: 2),
                      Icon(Icons.arrow_drop_down, color: Colors.grey[500], size: 20),
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
                  decoration: InputDecoration(
                    hintText: _selectedCountry.hintText,
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                  ),
                  inputFormatters: InputValidator.phoneFormatters(
                    maxLength: _selectedCountry.phoneLength,
                  ),
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
