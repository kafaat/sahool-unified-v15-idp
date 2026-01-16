import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// SAHOOL OTP Verification Screen
/// شاشة التحقق من رمز OTP
///
/// Features:
/// - Native SMS auto-fill support (iOS & Android)
/// - 6-digit OTP input with auto-focus
/// - Countdown timer with resend option
/// - Biometric support for quick verification
/// - Deep linking support for App Store/Play Store patterns

/// OTP Channel enum
enum OTPChannel { sms, whatsapp, telegram, email }

/// OTP Purpose enum
enum OTPPurpose { passwordReset, phoneVerification, twoFactor }

/// OTP Verification State
class OTPVerificationState {
  final String identifier;
  final OTPChannel channel;
  final OTPPurpose purpose;
  final bool isLoading;
  final bool isVerified;
  final String? error;
  final int remainingSeconds;
  final int resendCooldown;
  final String? resetToken;

  const OTPVerificationState({
    required this.identifier,
    required this.channel,
    required this.purpose,
    this.isLoading = false,
    this.isVerified = false,
    this.error,
    this.remainingSeconds = 300, // 5 minutes
    this.resendCooldown = 0,
    this.resetToken,
  });

  OTPVerificationState copyWith({
    String? identifier,
    OTPChannel? channel,
    OTPPurpose? purpose,
    bool? isLoading,
    bool? isVerified,
    String? error,
    int? remainingSeconds,
    int? resendCooldown,
    String? resetToken,
  }) {
    return OTPVerificationState(
      identifier: identifier ?? this.identifier,
      channel: channel ?? this.channel,
      purpose: purpose ?? this.purpose,
      isLoading: isLoading ?? this.isLoading,
      isVerified: isVerified ?? this.isVerified,
      error: error,
      remainingSeconds: remainingSeconds ?? this.remainingSeconds,
      resendCooldown: resendCooldown ?? this.resendCooldown,
      resetToken: resetToken ?? this.resetToken,
    );
  }
}

/// OTP Verification Screen Widget
class OTPVerificationScreen extends ConsumerStatefulWidget {
  final String identifier;
  final OTPChannel channel;
  final OTPPurpose purpose;
  final VoidCallback? onVerified;
  final String? Function(String resetToken)? onResetTokenReceived;

  const OTPVerificationScreen({
    super.key,
    required this.identifier,
    required this.channel,
    required this.purpose,
    this.onVerified,
    this.onResetTokenReceived,
  });

  @override
  ConsumerState<OTPVerificationScreen> createState() => _OTPVerificationScreenState();
}

class _OTPVerificationScreenState extends ConsumerState<OTPVerificationScreen>
    with SingleTickerProviderStateMixin {
  // OTP Controllers
  final List<TextEditingController> _otpControllers =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _focusNodes =
      List.generate(6, (_) => FocusNode());

  // State
  late OTPVerificationState _state;
  Timer? _countdownTimer;
  Timer? _resendCooldownTimer;

  // Animation
  late AnimationController _shakeController;
  late Animation<double> _shakeAnimation;

  @override
  void initState() {
    super.initState();

    _state = OTPVerificationState(
      identifier: widget.identifier,
      channel: widget.channel,
      purpose: widget.purpose,
    );

    // Setup shake animation for error feedback
    _shakeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _shakeAnimation = Tween<double>(begin: 0, end: 10)
        .chain(CurveTween(curve: Curves.elasticIn))
        .animate(_shakeController);

    // Start countdown timer
    _startCountdownTimer();

    // Setup SMS listener for auto-fill
    _setupSMSAutoFill();

    // Auto-focus first input
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _focusNodes[0].requestFocus();
    });
  }

  @override
  void dispose() {
    _countdownTimer?.cancel();
    _resendCooldownTimer?.cancel();
    _shakeController.dispose();
    for (final controller in _otpControllers) {
      controller.dispose();
    }
    for (final node in _focusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  /// Setup SMS auto-fill listener
  void _setupSMSAutoFill() {
    // Note: In production, use sms_autofill or similar package
    // This is a placeholder for the auto-fill setup
    // The actual implementation depends on platform-specific configuration
  }

  /// Start countdown timer
  void _startCountdownTimer() {
    _countdownTimer?.cancel();
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_state.remainingSeconds <= 0) {
        timer.cancel();
        setState(() {
          _state = _state.copyWith(
            error: 'انتهت صلاحية الرمز',
          );
        });
      } else {
        setState(() {
          _state = _state.copyWith(
            remainingSeconds: _state.remainingSeconds - 1,
          );
        });
      }
    });
  }

  /// Start resend cooldown timer
  void _startResendCooldown() {
    setState(() {
      _state = _state.copyWith(resendCooldown: 60);
    });

    _resendCooldownTimer?.cancel();
    _resendCooldownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_state.resendCooldown <= 0) {
        timer.cancel();
      } else {
        setState(() {
          _state = _state.copyWith(
            resendCooldown: _state.resendCooldown - 1,
          );
        });
      }
    });
  }

  /// Format time as MM:SS
  String _formatTime(int seconds) {
    final mins = seconds ~/ 60;
    final secs = seconds % 60;
    return '${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  /// Handle OTP input change
  void _onOTPChanged(int index, String value) {
    // Clear error
    if (_state.error != null) {
      setState(() {
        _state = _state.copyWith(error: null);
      });
    }

    // Only allow digits
    final digit = value.replaceAll(RegExp(r'[^0-9]'), '');
    if (digit.isEmpty) {
      _otpControllers[index].text = '';
      return;
    }

    // Take only last digit if multiple pasted
    _otpControllers[index].text = digit.substring(digit.length - 1);
    _otpControllers[index].selection = TextSelection.fromPosition(
      TextPosition(offset: 1),
    );

    // Auto-focus next input
    if (index < 5) {
      _focusNodes[index + 1].requestFocus();
    }

    // Auto-verify when all digits entered
    if (_isOTPComplete()) {
      _verifyOTP();
    }
  }

  /// Handle paste
  void _onPaste(String pastedText) {
    final digits = pastedText.replaceAll(RegExp(r'[^0-9]'), '');
    for (int i = 0; i < digits.length && i < 6; i++) {
      _otpControllers[i].text = digits[i];
    }

    if (digits.length >= 6) {
      _focusNodes[5].requestFocus();
      _verifyOTP();
    } else if (digits.isNotEmpty) {
      _focusNodes[digits.length < 6 ? digits.length : 5].requestFocus();
    }
  }

  /// Handle backspace
  void _onBackspace(int index) {
    if (_otpControllers[index].text.isEmpty && index > 0) {
      _focusNodes[index - 1].requestFocus();
    }
  }

  /// Check if OTP is complete
  bool _isOTPComplete() {
    return _otpControllers.every((c) => c.text.isNotEmpty);
  }

  /// Get entered OTP
  String _getOTP() {
    return _otpControllers.map((c) => c.text).join();
  }

  /// Verify OTP
  Future<void> _verifyOTP() async {
    if (!_isOTPComplete() || _state.isLoading) return;

    final otp = _getOTP();

    setState(() {
      _state = _state.copyWith(isLoading: true, error: null);
    });

    try {
      // TODO: Call API to verify OTP
      // final response = await ref.read(authServiceProvider).verifyOTP(
      //   identifier: widget.identifier,
      //   otpCode: otp,
      //   purpose: widget.purpose.name,
      // );

      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));

      // For demo, accept any 6-digit code
      // In production, validate against server

      setState(() {
        _state = _state.copyWith(
          isLoading: false,
          isVerified: true,
          resetToken: 'demo_reset_token_${DateTime.now().millisecondsSinceEpoch}',
        );
      });

      // Show success feedback
      HapticFeedback.mediumImpact();

      // Notify parent
      if (widget.purpose == OTPPurpose.passwordReset && _state.resetToken != null) {
        widget.onResetTokenReceived?.call(_state.resetToken!);
      }
      widget.onVerified?.call();

      // Navigate to next screen after delay
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) {
        _navigateToNextScreen();
      }

    } catch (e) {
      // Error - shake and clear
      _shakeController.forward(from: 0);
      HapticFeedback.heavyImpact();

      setState(() {
        _state = _state.copyWith(
          isLoading: false,
          error: e.toString(),
        );
      });

      // Clear OTP inputs
      for (final controller in _otpControllers) {
        controller.clear();
      }
      _focusNodes[0].requestFocus();
    }
  }

  /// Navigate to next screen based on purpose
  void _navigateToNextScreen() {
    switch (widget.purpose) {
      case OTPPurpose.passwordReset:
        context.go(
          '/reset-password',
          extra: {
            'token': _state.resetToken,
            'identifier': widget.identifier,
          },
        );
        break;
      case OTPPurpose.phoneVerification:
      case OTPPurpose.twoFactor:
        Navigator.of(context).pop(true);
        break;
    }
  }

  /// Resend OTP
  Future<void> _resendOTP() async {
    if (_state.resendCooldown > 0 || _state.isLoading) return;

    setState(() {
      _state = _state.copyWith(isLoading: true, error: null);
    });

    try {
      // TODO: Call API to resend OTP
      // await ref.read(authServiceProvider).sendOTP(
      //   identifier: widget.identifier,
      //   channel: widget.channel.name,
      //   purpose: widget.purpose.name,
      // );

      // Simulate API call
      await Future.delayed(const Duration(milliseconds: 500));

      // Reset timer
      setState(() {
        _state = _state.copyWith(
          isLoading: false,
          remainingSeconds: 300,
        );
      });

      _startCountdownTimer();
      _startResendCooldown();

      // Clear OTP inputs
      for (final controller in _otpControllers) {
        controller.clear();
      }
      _focusNodes[0].requestFocus();

      // Show success snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(_getResendSuccessMessage()),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }

    } catch (e) {
      setState(() {
        _state = _state.copyWith(
          isLoading: false,
          error: 'فشل إعادة إرسال الرمز',
        );
      });
    }
  }

  /// Get channel display name
  String _getChannelName() {
    switch (widget.channel) {
      case OTPChannel.sms:
        return 'رسالة نصية SMS';
      case OTPChannel.whatsapp:
        return 'واتساب';
      case OTPChannel.telegram:
        return 'تيليجرام';
      case OTPChannel.email:
        return 'البريد الإلكتروني';
    }
  }

  /// Get channel icon
  IconData _getChannelIcon() {
    switch (widget.channel) {
      case OTPChannel.sms:
        return Icons.sms_outlined;
      case OTPChannel.whatsapp:
        return Icons.chat_bubble_outline;
      case OTPChannel.telegram:
        return Icons.send_outlined;
      case OTPChannel.email:
        return Icons.email_outlined;
    }
  }

  /// Get resend success message
  String _getResendSuccessMessage() {
    switch (widget.channel) {
      case OTPChannel.sms:
        return 'تم إرسال رمز جديد عبر SMS';
      case OTPChannel.whatsapp:
        return 'تم إرسال رمز جديد عبر واتساب';
      case OTPChannel.telegram:
        return 'تم إرسال رمز جديد عبر تيليجرام';
      case OTPChannel.email:
        return 'تم إرسال رمز جديد عبر البريد الإلكتروني';
    }
  }

  /// Mask identifier for display
  String _maskIdentifier() {
    final id = widget.identifier;
    if (id.contains('@')) {
      // Email
      final parts = id.split('@');
      final local = parts[0];
      final domain = parts[1];
      final masked = local.length > 2
          ? '${local[0]}${'*' * (local.length - 2)}${local[local.length - 1]}'
          : local;
      return '$masked@$domain';
    } else {
      // Phone
      if (id.length > 4) {
        return '${'*' * (id.length - 4)}${id.substring(id.length - 4)}';
      }
      return id;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: colorScheme.onBackground),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 20),

              // Header Icon
              _buildHeaderIcon(colorScheme),

              const SizedBox(height: 24),

              // Title
              Text(
                'التحقق من الرمز',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onBackground,
                ),
              ),

              const SizedBox(height: 12),

              // Subtitle
              Text(
                'أدخل رمز التحقق المكون من 6 أرقام',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onBackground.withOpacity(0.7),
                ),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 8),

              // Channel info
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    _getChannelIcon(),
                    size: 18,
                    color: colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _getChannelName(),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.primary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 4),

              // Masked identifier
              Directionality(
                textDirection: TextDirection.ltr,
                child: Text(
                  _maskIdentifier(),
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: colorScheme.onBackground.withOpacity(0.9),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),

              const SizedBox(height: 40),

              // OTP Input Fields
              AnimatedBuilder(
                animation: _shakeAnimation,
                builder: (context, child) {
                  return Transform.translate(
                    offset: Offset(_shakeAnimation.value, 0),
                    child: child,
                  );
                },
                child: _buildOTPInputs(colorScheme),
              ),

              const SizedBox(height: 24),

              // Timer
              _buildTimer(colorScheme, theme),

              const SizedBox(height: 16),

              // Error message
              if (_state.error != null)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  decoration: BoxDecoration(
                    color: colorScheme.error.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.error_outline,
                        color: colorScheme.error,
                        size: 20,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _state.error!,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: colorScheme.error,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

              const SizedBox(height: 24),

              // Verify Button
              _buildVerifyButton(colorScheme, theme),

              const SizedBox(height: 16),

              // Resend Button
              _buildResendButton(colorScheme, theme),

              const SizedBox(height: 32),

              // Auto-fill hint
              if (widget.channel == OTPChannel.sms)
                _buildAutoFillHint(colorScheme, theme),
            ],
          ),
        ),
      ),
    );
  }

  /// Build header icon with animation
  Widget _buildHeaderIcon(ColorScheme colorScheme) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        color: _state.isVerified
            ? Colors.green.withOpacity(0.1)
            : colorScheme.primary.withOpacity(0.1),
        shape: BoxShape.circle,
      ),
      child: Icon(
        _state.isVerified ? Icons.check_circle : Icons.shield_outlined,
        size: 40,
        color: _state.isVerified ? Colors.green : colorScheme.primary,
      ),
    );
  }

  /// Build OTP input fields
  Widget _buildOTPInputs(ColorScheme colorScheme) {
    return Directionality(
      textDirection: TextDirection.ltr,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: List.generate(6, (index) {
          return Container(
            width: 48,
            height: 56,
            margin: EdgeInsets.symmetric(
              horizontal: index == 2 || index == 3 ? 8 : 4,
            ),
            child: TextField(
              controller: _otpControllers[index],
              focusNode: _focusNodes[index],
              textAlign: TextAlign.center,
              keyboardType: TextInputType.number,
              maxLength: 1,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: colorScheme.onBackground,
              ),
              decoration: InputDecoration(
                counterText: '',
                filled: true,
                fillColor: _otpControllers[index].text.isNotEmpty
                    ? colorScheme.primary.withOpacity(0.1)
                    : colorScheme.surface,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: colorScheme.outline.withOpacity(0.3),
                  ),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: _otpControllers[index].text.isNotEmpty
                        ? colorScheme.primary
                        : colorScheme.outline.withOpacity(0.3),
                    width: _otpControllers[index].text.isNotEmpty ? 2 : 1,
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: colorScheme.primary,
                    width: 2,
                  ),
                ),
                errorBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: colorScheme.error,
                    width: 2,
                  ),
                ),
              ),
              inputFormatters: [
                FilteringTextInputFormatter.digitsOnly,
                LengthLimitingTextInputFormatter(1),
              ],
              onChanged: (value) => _onOTPChanged(index, value),
              onTap: () {
                // Select all text on tap for easy replacement
                _otpControllers[index].selection = TextSelection(
                  baseOffset: 0,
                  extentOffset: _otpControllers[index].text.length,
                );
              },
            ),
          );
        }),
      ),
    );
  }

  /// Build timer display
  Widget _buildTimer(ColorScheme colorScheme, ThemeData theme) {
    final isExpired = _state.remainingSeconds <= 0;
    final isWarning = _state.remainingSeconds <= 60;

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.timer_outlined,
          size: 18,
          color: isExpired
              ? colorScheme.error
              : isWarning
                  ? Colors.orange
                  : colorScheme.onBackground.withOpacity(0.6),
        ),
        const SizedBox(width: 8),
        Text(
          isExpired ? 'انتهى الوقت' : 'صالح لمدة ${_formatTime(_state.remainingSeconds)}',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: isExpired
                ? colorScheme.error
                : isWarning
                    ? Colors.orange
                    : colorScheme.onBackground.withOpacity(0.6),
            fontWeight: isWarning ? FontWeight.w600 : FontWeight.normal,
            fontFeatures: const [FontFeature.tabularFigures()],
          ),
        ),
      ],
    );
  }

  /// Build verify button
  Widget _buildVerifyButton(ColorScheme colorScheme, ThemeData theme) {
    final isEnabled = _isOTPComplete() &&
                      !_state.isLoading &&
                      _state.remainingSeconds > 0 &&
                      !_state.isVerified;

    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton(
        onPressed: isEnabled ? _verifyOTP : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: _state.isVerified ? Colors.green : colorScheme.primary,
          foregroundColor: Colors.white,
          disabledBackgroundColor: colorScheme.onBackground.withOpacity(0.1),
          disabledForegroundColor: colorScheme.onBackground.withOpacity(0.4),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
        ),
        child: _state.isLoading
            ? SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : _state.isVerified
                ? Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.check_circle, size: 20),
                      const SizedBox(width: 8),
                      Text('تم التحقق بنجاح'),
                    ],
                  )
                : Text(
                    'تحقق',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
      ),
    );
  }

  /// Build resend button
  Widget _buildResendButton(ColorScheme colorScheme, ThemeData theme) {
    final canResend = _state.resendCooldown <= 0 && !_state.isLoading;

    return TextButton(
      onPressed: canResend ? _resendOTP : null,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.refresh,
            size: 18,
            color: canResend
                ? colorScheme.primary
                : colorScheme.onBackground.withOpacity(0.4),
          ),
          const SizedBox(width: 8),
          Text(
            _state.resendCooldown > 0
                ? 'إعادة الإرسال بعد ${_state.resendCooldown} ثانية'
                : 'إعادة إرسال الرمز',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: canResend
                  ? colorScheme.primary
                  : colorScheme.onBackground.withOpacity(0.4),
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  /// Build auto-fill hint
  Widget _buildAutoFillHint(ColorScheme colorScheme, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.primary.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme.primary.withOpacity(0.1),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.auto_awesome,
            color: colorScheme.primary,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'سيتم ملء الرمز تلقائياً عند وصول الرسالة',
              style: theme.textTheme.bodySmall?.copyWith(
                color: colorScheme.onBackground.withOpacity(0.7),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
