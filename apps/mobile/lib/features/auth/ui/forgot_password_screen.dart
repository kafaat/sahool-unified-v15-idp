import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/sahool_theme.dart';
import '../../../core/utils/input_validator.dart';
import 'otp_verification_screen.dart';

/// SAHOOL Forgot Password Screen
/// شاشة استعادة كلمة المرور
///
/// Features:
/// - Multi-channel OTP delivery (SMS, WhatsApp, Telegram, Email)
/// - Dynamic input field based on selected channel
/// - Beautiful App Store / Play Store inspired design
/// - Bilingual support (Arabic primary, English secondary)
/// - Smooth animations and transitions
/// - Comprehensive error handling

/// Recovery channel information
class RecoveryChannel {
  final OTPChannel channel;
  final String nameAr;
  final String nameEn;
  final IconData icon;
  final Color color;
  final String inputType; // 'phone' or 'email'
  final String hintAr;
  final String hintEn;

  const RecoveryChannel({
    required this.channel,
    required this.nameAr,
    required this.nameEn,
    required this.icon,
    required this.color,
    required this.inputType,
    required this.hintAr,
    required this.hintEn,
  });
}

/// Available recovery channels
const List<RecoveryChannel> _recoveryChannels = [
  RecoveryChannel(
    channel: OTPChannel.sms,
    nameAr: 'رسالة نصية',
    nameEn: 'SMS',
    icon: Icons.sms_outlined,
    color: Color(0xFF2196F3),
    inputType: 'phone',
    hintAr: 'أدخل رقم هاتفك',
    hintEn: 'Enter your phone number',
  ),
  RecoveryChannel(
    channel: OTPChannel.whatsapp,
    nameAr: 'واتساب',
    nameEn: 'WhatsApp',
    icon: Icons.chat_bubble_outline,
    color: Color(0xFF25D366),
    inputType: 'phone',
    hintAr: 'أدخل رقم واتساب',
    hintEn: 'Enter your WhatsApp number',
  ),
  RecoveryChannel(
    channel: OTPChannel.telegram,
    nameAr: 'تيليجرام',
    nameEn: 'Telegram',
    icon: Icons.send_outlined,
    color: Color(0xFF0088CC),
    inputType: 'phone',
    hintAr: 'أدخل رقم تيليجرام',
    hintEn: 'Enter your Telegram number',
  ),
  RecoveryChannel(
    channel: OTPChannel.email,
    nameAr: 'البريد الإلكتروني',
    nameEn: 'Email',
    icon: Icons.email_outlined,
    color: Color(0xFFEA4335),
    inputType: 'email',
    hintAr: 'أدخل بريدك الإلكتروني',
    hintEn: 'Enter your email address',
  ),
];

/// Forgot Password Screen Widget
class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen>
    with TickerProviderStateMixin {
  // Controllers
  final TextEditingController _inputController = TextEditingController();
  final FocusNode _inputFocusNode = FocusNode();

  // State
  int _selectedChannelIndex = 0;
  bool _isLoading = false;
  String? _errorMessage;

  // Animation controllers
  late AnimationController _fadeController;
  late AnimationController _slideController;
  late AnimationController _shakeController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _shakeAnimation;

  RecoveryChannel get _selectedChannel => _recoveryChannels[_selectedChannelIndex];

  @override
  void initState() {
    super.initState();
    _initAnimations();

    // Add focus listener to update UI
    _inputFocusNode.addListener(_onInputChange);

    // Add text controller listener for clear button
    _inputController.addListener(_onInputChange);
  }

  void _onInputChange() {
    setState(() {});
  }

  void _initAnimations() {
    // Fade animation for content
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeOut,
    );
    _fadeController.forward();

    // Slide animation for input field
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutCubic,
    ));
    _slideController.forward();

    // Shake animation for errors
    _shakeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _shakeAnimation = Tween<double>(begin: 0, end: 10)
        .chain(CurveTween(curve: Curves.elasticIn))
        .animate(_shakeController);
  }

  @override
  void dispose() {
    _inputController.removeListener(_onInputChange);
    _inputController.dispose();
    _inputFocusNode.removeListener(_onInputChange);
    _inputFocusNode.dispose();
    _fadeController.dispose();
    _slideController.dispose();
    _shakeController.dispose();
    super.dispose();
  }

  /// Handle channel selection
  void _onChannelSelected(int index) {
    if (_selectedChannelIndex == index) return;

    setState(() {
      _selectedChannelIndex = index;
      _errorMessage = null;
      _inputController.clear();
    });

    // Animate input field change
    _slideController.reset();
    _slideController.forward();

    // Haptic feedback
    HapticFeedback.selectionClick();
  }

  /// Validate input based on selected channel
  ValidationResult _validateInput() {
    final input = _inputController.text.trim();
    final channel = _selectedChannel;

    if (input.isEmpty) {
      return ValidationResult.error(
        '${channel.nameEn} is required',
        '${channel.hintAr}',
      );
    }

    if (channel.inputType == 'phone') {
      // Yemen phone validation (primary market)
      return InputValidator.validateYemenPhone(input);
    } else {
      // Email validation
      return InputValidator.validateEmail(input);
    }
  }

  /// Get formatted identifier for API
  String _getFormattedIdentifier() {
    final input = _inputController.text.trim();
    if (_selectedChannel.inputType == 'phone') {
      // Add Yemen country code
      return '+967${input.replaceAll(RegExp(r'[\s\-\(\)]'), '')}';
    }
    return input;
  }

  /// Submit recovery request
  Future<void> _submitRecoveryRequest() async {
    // Clear previous error
    setState(() => _errorMessage = null);

    // Validate input
    final validation = _validateInput();
    if (!validation.isValid) {
      setState(() => _errorMessage = validation.errorMessageAr);
      _shakeController.forward(from: 0);
      HapticFeedback.heavyImpact();
      return;
    }

    // Start loading
    setState(() => _isLoading = true);

    try {
      // TODO: Call API to send OTP
      // await ref.read(authServiceProvider).sendPasswordResetOTP(
      //   identifier: _getFormattedIdentifier(),
      //   channel: _selectedChannel.channel.name,
      // );

      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));

      // Navigate to OTP verification screen
      if (mounted) {
        Navigator.of(context).push(
          PageRouteBuilder(
            pageBuilder: (context, animation, secondaryAnimation) {
              return OTPVerificationScreen(
                identifier: _getFormattedIdentifier(),
                channel: _selectedChannel.channel,
                purpose: OTPPurpose.passwordReset,
                onVerified: () {
                  // OTP verified successfully
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('تم التحقق بنجاح'),
                      backgroundColor: Colors.green,
                    ),
                  );
                },
                onResetTokenReceived: (token) {
                  // Navigate to reset password screen with token
                  // Navigator.of(context).pushReplacementNamed(
                  //   '/reset-password',
                  //   arguments: {'token': token},
                  // );
                  return null;
                },
              );
            },
            transitionsBuilder: (context, animation, secondaryAnimation, child) {
              return SlideTransition(
                position: Tween<Offset>(
                  begin: const Offset(1.0, 0.0),
                  end: Offset.zero,
                ).animate(CurvedAnimation(
                  parent: animation,
                  curve: Curves.easeOutCubic,
                )),
                child: child,
              );
            },
          ),
        );
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'حدث خطأ أثناء إرسال رمز التحقق';
      });
      _shakeController.forward(from: 0);
      HapticFeedback.heavyImpact();
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: SahoolColors.background,
      body: SafeArea(
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 16),

                  // Back button
                  _buildBackButton(colorScheme),

                  const SizedBox(height: 32),

                  // Header with icon and titles
                  _buildHeader(theme),

                  const SizedBox(height: 40),

                  // Channel selection grid
                  _buildChannelGrid(colorScheme, theme),

                  const SizedBox(height: 32),

                  // Input field section
                  SlideTransition(
                    position: _slideAnimation,
                    child: _buildInputSection(colorScheme, theme),
                  ),

                  const SizedBox(height: 24),

                  // Error message
                  AnimatedBuilder(
                    animation: _shakeAnimation,
                    builder: (context, child) {
                      return Transform.translate(
                        offset: Offset(_shakeAnimation.value, 0),
                        child: child,
                      );
                    },
                    child: _buildErrorMessage(colorScheme, theme),
                  ),

                  const SizedBox(height: 24),

                  // Submit button
                  _buildSubmitButton(colorScheme, theme),

                  const SizedBox(height: 32),

                  // Help section
                  _buildHelpSection(colorScheme, theme),

                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Build back button
  Widget _buildBackButton(ColorScheme colorScheme) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: IconButton(
        onPressed: () => Navigator.of(context).pop(),
        icon: const Icon(Icons.arrow_back_ios_new, size: 20),
        style: IconButton.styleFrom(
          foregroundColor: SahoolColors.textDark,
        ),
      ),
    );
  }

  /// Build header with icon and titles
  Widget _buildHeader(ThemeData theme) {
    return Center(
      child: Column(
        children: [
          // Animated lock icon
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0.8, end: 1.0),
            duration: const Duration(milliseconds: 600),
            curve: Curves.elasticOut,
            builder: (context, value, child) {
              return Transform.scale(
                scale: value,
                child: child,
              );
            },
            child: Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    SahoolColors.primary.withOpacity(0.1),
                    SahoolColors.secondary.withOpacity(0.1),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Container(
                  width: 70,
                  height: 70,
                  decoration: BoxDecoration(
                    color: SahoolColors.primary.withOpacity(0.15),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.lock_reset,
                    size: 36,
                    color: SahoolColors.primary,
                  ),
                ),
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Arabic title (primary)
          Text(
            'استعادة كلمة المرور',
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: SahoolColors.textDark,
            ),
          ),

          const SizedBox(height: 8),

          // English title (secondary)
          Text(
            'Password Recovery',
            style: theme.textTheme.titleMedium?.copyWith(
              color: SahoolColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),

          const SizedBox(height: 16),

          // Subtitle
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              'اختر طريقة استلام رمز التحقق',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: SahoolColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  /// Build channel selection grid
  Widget _buildChannelGrid(ColorScheme colorScheme, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section title
        Text(
          'طريقة الاستلام',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: SahoolColors.textDark,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Recovery Method',
          style: theme.textTheme.bodySmall?.copyWith(
            color: SahoolColors.textSecondary,
          ),
        ),
        const SizedBox(height: 16),

        // Channel grid
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.4,
          ),
          itemCount: _recoveryChannels.length,
          itemBuilder: (context, index) {
            return _buildChannelCard(index, colorScheme, theme);
          },
        ),
      ],
    );
  }

  /// Build individual channel card
  Widget _buildChannelCard(int index, ColorScheme colorScheme, ThemeData theme) {
    final channel = _recoveryChannels[index];
    final isSelected = _selectedChannelIndex == index;

    return GestureDetector(
      onTap: () => _onChannelSelected(index),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOutCubic,
        decoration: BoxDecoration(
          color: isSelected
              ? channel.color.withOpacity(0.1)
              : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected
                ? channel.color
                : Colors.grey[200]!,
            width: isSelected ? 2 : 1,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: channel.color.withOpacity(0.2),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ]
              : SahoolShadows.small,
        ),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Icon with animated scale
              AnimatedScale(
                scale: isSelected ? 1.1 : 1.0,
                duration: const Duration(milliseconds: 200),
                child: Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: channel.color.withOpacity(isSelected ? 0.2 : 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    channel.icon,
                    color: channel.color,
                    size: 22,
                  ),
                ),
              ),
              const SizedBox(height: 8),

              // Arabic name
              Text(
                channel.nameAr,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                  color: isSelected ? channel.color : SahoolColors.textDark,
                ),
              ),

              // English name
              Text(
                channel.nameEn,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: SahoolColors.textSecondary,
                  fontSize: 11,
                ),
              ),

              // Selection indicator
              if (isSelected)
                Container(
                  margin: const EdgeInsets.only(top: 4),
                  width: 20,
                  height: 3,
                  decoration: BoxDecoration(
                    color: channel.color,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  /// Build input section
  Widget _buildInputSection(ColorScheme colorScheme, ThemeData theme) {
    final channel = _selectedChannel;
    final isPhone = channel.inputType == 'phone';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section title
        Row(
          children: [
            Icon(
              isPhone ? Icons.phone_outlined : Icons.email_outlined,
              size: 18,
              color: channel.color,
            ),
            const SizedBox(width: 8),
            Text(
              isPhone ? 'رقم الهاتف' : 'البريد الإلكتروني',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: SahoolColors.textDark,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          isPhone ? 'Phone Number' : 'Email Address',
          style: theme.textTheme.bodySmall?.copyWith(
            color: SahoolColors.textSecondary,
          ),
        ),
        const SizedBox(height: 12),

        // Input field
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: _errorMessage != null
                  ? SahoolColors.danger
                  : _inputFocusNode.hasFocus
                      ? channel.color
                      : Colors.grey[200]!,
              width: _inputFocusNode.hasFocus ? 2 : 1,
            ),
            boxShadow: SahoolShadows.small,
          ),
          child: Row(
            children: [
              // Country code prefix (for phone)
              if (isPhone) ...[
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 18,
                  ),
                  decoration: BoxDecoration(
                    border: Border(
                      left: BorderSide(color: Colors.grey[200]!),
                    ),
                  ),
                  child: Row(
                    children: [
                      const Text(
                        '+967',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: SahoolColors.textDark,
                        ),
                      ),
                      const SizedBox(width: 4),
                      Icon(
                        Icons.arrow_drop_down,
                        color: Colors.grey[400],
                        size: 20,
                      ),
                    ],
                  ),
                ),
              ],

              // Text field
              Expanded(
                child: TextField(
                  controller: _inputController,
                  focusNode: _inputFocusNode,
                  keyboardType: isPhone
                      ? TextInputType.phone
                      : TextInputType.emailAddress,
                  textDirection: isPhone ? TextDirection.ltr : null,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: SahoolColors.textDark,
                    letterSpacing: isPhone ? 1 : 0,
                  ),
                  decoration: InputDecoration(
                    hintText: channel.hintAr,
                    hintStyle: TextStyle(
                      color: Colors.grey[400],
                      fontWeight: FontWeight.normal,
                    ),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 18,
                    ),
                    prefixIcon: !isPhone
                        ? Icon(
                            Icons.email_outlined,
                            color: Colors.grey[400],
                          )
                        : null,
                  ),
                  inputFormatters: isPhone
                      ? InputValidator.phoneFormatters(maxLength: 9)
                      : null,
                  onChanged: (_) {
                    if (_errorMessage != null) {
                      setState(() => _errorMessage = null);
                    }
                  },
                  onSubmitted: (_) => _submitRecoveryRequest(),
                ),
              ),

              // Clear button
              if (_inputController.text.isNotEmpty)
                IconButton(
                  onPressed: () {
                    _inputController.clear();
                    setState(() => _errorMessage = null);
                  },
                  icon: Icon(
                    Icons.cancel,
                    color: Colors.grey[400],
                    size: 20,
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }

  /// Build error message
  Widget _buildErrorMessage(ColorScheme colorScheme, ThemeData theme) {
    if (_errorMessage == null) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: SahoolColors.danger.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: SahoolColors.danger.withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.error_outline,
            color: SahoolColors.danger,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _errorMessage!,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: SahoolColors.danger,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Build submit button
  Widget _buildSubmitButton(ColorScheme colorScheme, ThemeData theme) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _submitRecoveryRequest,
        style: ElevatedButton.styleFrom(
          backgroundColor: _selectedChannel.color,
          foregroundColor: Colors.white,
          disabledBackgroundColor: Colors.grey[300],
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          shadowColor: _selectedChannel.color.withOpacity(0.4),
        ),
        child: _isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  color: Colors.white,
                  strokeWidth: 2.5,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(_selectedChannel.icon, size: 20),
                  const SizedBox(width: 12),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'إرسال رمز التحقق',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        'Send Verification Code',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 12),
                  const Icon(Icons.arrow_forward_ios, size: 16),
                ],
              ),
      ),
    );
  }

  /// Build help section
  Widget _buildHelpSection(ColorScheme colorScheme, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolColors.info.withOpacity(0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: SahoolColors.info.withOpacity(0.1),
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: SahoolColors.info.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.help_outline,
                  color: SahoolColors.info,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'تحتاج مساعدة؟',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: SahoolColors.textDark,
                      ),
                    ),
                    Text(
                      'Need Help?',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: SahoolColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              TextButton(
                onPressed: () {
                  // TODO: Navigate to support
                },
                child: Text(
                  'تواصل معنا',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: SahoolColors.info,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'سيتم إرسال رمز التحقق المكون من 6 أرقام إلى القناة المختارة. '
            'الرمز صالح لمدة 5 دقائق.',
            style: theme.textTheme.bodySmall?.copyWith(
              color: SahoolColors.textSecondary,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}
