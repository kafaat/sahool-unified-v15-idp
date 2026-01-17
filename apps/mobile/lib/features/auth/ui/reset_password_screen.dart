import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/sahool_theme.dart';

/// SAHOOL Reset Password Screen
/// شاشة إعادة تعيين كلمة المرور
///
/// Features:
/// - Token-based password reset (from OTP or email link)
/// - Password strength indicator with real-time feedback
/// - Confirm password validation
/// - Success animation with auto-redirect
/// - Bilingual support (Arabic primary)
/// - Beautiful iOS/Android store-quality UI

/// Password strength level enum
enum PasswordStrength { weak, fair, good, strong, veryStrong }

/// Password requirement status
class PasswordRequirement {
  final String label;
  final String labelAr;
  final bool isMet;

  const PasswordRequirement({
    required this.label,
    required this.labelAr,
    required this.isMet,
  });
}

/// Reset Password State
class ResetPasswordState {
  final String token;
  final String? identifier;
  final bool isLoading;
  final bool isSuccess;
  final String? error;
  final bool obscurePassword;
  final bool obscureConfirmPassword;
  final PasswordStrength strength;
  final List<PasswordRequirement> requirements;
  final bool passwordsMatch;

  const ResetPasswordState({
    required this.token,
    this.identifier,
    this.isLoading = false,
    this.isSuccess = false,
    this.error,
    this.obscurePassword = true,
    this.obscureConfirmPassword = true,
    this.strength = PasswordStrength.weak,
    this.requirements = const [],
    this.passwordsMatch = false,
  });

  ResetPasswordState copyWith({
    String? token,
    String? identifier,
    bool? isLoading,
    bool? isSuccess,
    String? error,
    bool? obscurePassword,
    bool? obscureConfirmPassword,
    PasswordStrength? strength,
    List<PasswordRequirement>? requirements,
    bool? passwordsMatch,
  }) {
    return ResetPasswordState(
      token: token ?? this.token,
      identifier: identifier ?? this.identifier,
      isLoading: isLoading ?? this.isLoading,
      isSuccess: isSuccess ?? this.isSuccess,
      error: error,
      obscurePassword: obscurePassword ?? this.obscurePassword,
      obscureConfirmPassword: obscureConfirmPassword ?? this.obscureConfirmPassword,
      strength: strength ?? this.strength,
      requirements: requirements ?? this.requirements,
      passwordsMatch: passwordsMatch ?? this.passwordsMatch,
    );
  }
}

/// Reset Password Screen Widget
class ResetPasswordScreen extends ConsumerStatefulWidget {
  final String token;
  final String? identifier;

  const ResetPasswordScreen({
    super.key,
    required this.token,
    this.identifier,
  });

  @override
  ConsumerState<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen>
    with TickerProviderStateMixin {
  // Controllers
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _passwordFocusNode = FocusNode();
  final _confirmPasswordFocusNode = FocusNode();

  // State
  late ResetPasswordState _state;

  // Animations
  late AnimationController _successController;
  late Animation<double> _successScaleAnimation;
  late Animation<double> _successOpacityAnimation;
  late AnimationController _shakeController;
  late Animation<double> _shakeAnimation;
  late AnimationController _strengthController;

  // Timer for redirect
  Timer? _redirectTimer;

  @override
  void initState() {
    super.initState();

    // Initialize state
    _state = ResetPasswordState(
      token: widget.token,
      identifier: widget.identifier,
      requirements: _getInitialRequirements(),
    );

    // Setup success animation
    _successController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _successScaleAnimation = Tween<double>(begin: 0.0, end: 1.0)
        .chain(CurveTween(curve: Curves.elasticOut))
        .animate(_successController);
    _successOpacityAnimation = Tween<double>(begin: 0.0, end: 1.0)
        .chain(CurveTween(curve: Curves.easeIn))
        .animate(_successController);

    // Setup shake animation for errors
    _shakeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _shakeAnimation = Tween<double>(begin: 0, end: 10)
        .chain(CurveTween(curve: Curves.elasticIn))
        .animate(_shakeController);

    // Setup strength bar animation
    _strengthController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    // Listen to password changes
    _passwordController.addListener(_onPasswordChanged);
    _confirmPasswordController.addListener(_onConfirmPasswordChanged);

    // Auto-focus password field
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _passwordFocusNode.requestFocus();
    });
  }

  @override
  void dispose() {
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _passwordFocusNode.dispose();
    _confirmPasswordFocusNode.dispose();
    _successController.dispose();
    _shakeController.dispose();
    _strengthController.dispose();
    _redirectTimer?.cancel();
    super.dispose();
  }

  /// Get initial password requirements
  List<PasswordRequirement> _getInitialRequirements() {
    return [
      const PasswordRequirement(
        label: 'At least 8 characters',
        labelAr: '8 احرف على الاقل',
        isMet: false,
      ),
      const PasswordRequirement(
        label: 'One uppercase letter',
        labelAr: 'حرف كبير واحد على الاقل',
        isMet: false,
      ),
      const PasswordRequirement(
        label: 'One lowercase letter',
        labelAr: 'حرف صغير واحد على الاقل',
        isMet: false,
      ),
      const PasswordRequirement(
        label: 'One number',
        labelAr: 'رقم واحد على الاقل',
        isMet: false,
      ),
      const PasswordRequirement(
        label: 'One special character',
        labelAr: 'رمز خاص واحد على الاقل',
        isMet: false,
      ),
    ];
  }

  /// Handle password changes
  void _onPasswordChanged() {
    final password = _passwordController.text;
    final requirements = _validatePasswordRequirements(password);
    final strength = _calculatePasswordStrength(password, requirements);
    final passwordsMatch = password.isNotEmpty &&
        password == _confirmPasswordController.text;

    setState(() {
      _state = _state.copyWith(
        requirements: requirements,
        strength: strength,
        passwordsMatch: passwordsMatch,
        error: null,
      );
    });

    // Animate strength bar
    _strengthController.animateTo(
      _getStrengthProgress(strength),
      curve: Curves.easeOut,
    );
  }

  /// Handle confirm password changes
  void _onConfirmPasswordChanged() {
    final password = _passwordController.text;
    final confirmPassword = _confirmPasswordController.text;
    final passwordsMatch = password.isNotEmpty && password == confirmPassword;

    setState(() {
      _state = _state.copyWith(
        passwordsMatch: passwordsMatch,
        error: null,
      );
    });
  }

  /// Validate password requirements
  List<PasswordRequirement> _validatePasswordRequirements(String password) {
    return [
      PasswordRequirement(
        label: 'At least 8 characters',
        labelAr: '8 احرف على الاقل',
        isMet: password.length >= 8,
      ),
      PasswordRequirement(
        label: 'One uppercase letter',
        labelAr: 'حرف كبير واحد على الاقل',
        isMet: RegExp(r'[A-Z]').hasMatch(password),
      ),
      PasswordRequirement(
        label: 'One lowercase letter',
        labelAr: 'حرف صغير واحد على الاقل',
        isMet: RegExp(r'[a-z]').hasMatch(password),
      ),
      PasswordRequirement(
        label: 'One number',
        labelAr: 'رقم واحد على الاقل',
        isMet: RegExp(r'[0-9]').hasMatch(password),
      ),
      PasswordRequirement(
        label: 'One special character',
        labelAr: 'رمز خاص واحد على الاقل',
        isMet: RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(password),
      ),
    ];
  }

  /// Calculate password strength
  PasswordStrength _calculatePasswordStrength(
    String password,
    List<PasswordRequirement> requirements,
  ) {
    if (password.isEmpty) return PasswordStrength.weak;

    final metCount = requirements.where((r) => r.isMet).length;
    final hasLength = password.length >= 12;

    if (metCount == 5 && hasLength) {
      return PasswordStrength.veryStrong;
    } else if (metCount >= 4) {
      return PasswordStrength.strong;
    } else if (metCount >= 3) {
      return PasswordStrength.good;
    } else if (metCount >= 2) {
      return PasswordStrength.fair;
    } else {
      return PasswordStrength.weak;
    }
  }

  /// Get strength progress value (0.0 - 1.0)
  double _getStrengthProgress(PasswordStrength strength) {
    switch (strength) {
      case PasswordStrength.weak:
        return 0.2;
      case PasswordStrength.fair:
        return 0.4;
      case PasswordStrength.good:
        return 0.6;
      case PasswordStrength.strong:
        return 0.8;
      case PasswordStrength.veryStrong:
        return 1.0;
    }
  }

  /// Get strength color
  Color _getStrengthColor(PasswordStrength strength) {
    switch (strength) {
      case PasswordStrength.weak:
        return SahoolColors.danger;
      case PasswordStrength.fair:
        return Colors.orange;
      case PasswordStrength.good:
        return SahoolColors.warning;
      case PasswordStrength.strong:
        return SahoolColors.success;
      case PasswordStrength.veryStrong:
        return SahoolColors.primary;
    }
  }

  /// Get strength label
  String _getStrengthLabel(PasswordStrength strength) {
    switch (strength) {
      case PasswordStrength.weak:
        return 'ضعيفة';
      case PasswordStrength.fair:
        return 'مقبولة';
      case PasswordStrength.good:
        return 'جيدة';
      case PasswordStrength.strong:
        return 'قوية';
      case PasswordStrength.veryStrong:
        return 'قوية جدا';
    }
  }

  /// Check if can submit
  bool _canSubmit() {
    final allRequirementsMet = _state.requirements.every((r) => r.isMet);
    return allRequirementsMet &&
        _state.passwordsMatch &&
        !_state.isLoading &&
        !_state.isSuccess;
  }

  /// Submit new password
  Future<void> _submitPassword() async {
    if (!_canSubmit()) return;

    setState(() {
      _state = _state.copyWith(isLoading: true, error: null);
    });

    try {
      // TODO: Call API to reset password
      // final response = await ref.read(authServiceProvider).resetPassword(
      //   token: widget.token,
      //   newPassword: _passwordController.text,
      // );

      // Simulate API call
      await Future.delayed(const Duration(seconds: 2));

      // Success
      setState(() {
        _state = _state.copyWith(isLoading: false, isSuccess: true);
      });

      // Play success animation
      HapticFeedback.mediumImpact();
      _successController.forward();

      // Schedule redirect to login
      _redirectTimer = Timer(const Duration(seconds: 3), () {
        if (mounted) {
          context.go('/login');
        }
      });

    } catch (e) {
      // Error
      HapticFeedback.heavyImpact();
      _shakeController.forward(from: 0);

      setState(() {
        _state = _state.copyWith(
          isLoading: false,
          error: 'فشل تغيير كلمة المرور. يرجى المحاولة مرة اخرى.',
        );
      });
    }
  }

  /// Toggle password visibility
  void _togglePasswordVisibility() {
    setState(() {
      _state = _state.copyWith(obscurePassword: !_state.obscurePassword);
    });
  }

  /// Toggle confirm password visibility
  void _toggleConfirmPasswordVisibility() {
    setState(() {
      _state = _state.copyWith(
        obscureConfirmPassword: !_state.obscureConfirmPassword,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: colorScheme.onSurface),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: _state.isSuccess
            ? _buildSuccessView(colorScheme, theme)
            : _buildFormView(colorScheme, theme),
      ),
    );
  }

  /// Build success view with animation
  Widget _buildSuccessView(ColorScheme colorScheme, ThemeData theme) {
    return Center(
      child: AnimatedBuilder(
        animation: _successController,
        builder: (context, child) {
          return Opacity(
            opacity: _successOpacityAnimation.value,
            child: Transform.scale(
              scale: _successScaleAnimation.value,
              child: child,
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Success icon with animated ring
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: SahoolColors.success.withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: SahoolColors.success.withOpacity(0.3),
                    width: 3,
                  ),
                ),
                child: const Icon(
                  Icons.check_circle,
                  size: 64,
                  color: SahoolColors.success,
                ),
              ),

              const SizedBox(height: 32),

              // Success title
              Text(
                'تم بنجاح!',
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.success,
                ),
              ),

              const SizedBox(height: 12),

              // Success message
              Text(
                'تم تغيير كلمة المرور بنجاح',
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: colorScheme.onSurface.withOpacity(0.8),
                ),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 8),

              Text(
                'سيتم توجيهك لتسجيل الدخول...',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onSurface.withOpacity(0.6),
                ),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 32),

              // Progress indicator for redirect
              SizedBox(
                width: 200,
                child: TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.0, end: 1.0),
                  duration: const Duration(seconds: 3),
                  builder: (context, value, child) {
                    return LinearProgressIndicator(
                      value: value,
                      backgroundColor: colorScheme.outline.withOpacity(0.2),
                      color: SahoolColors.success,
                      borderRadius: BorderRadius.circular(4),
                    );
                  },
                ),
              ),

              const SizedBox(height: 24),

              // Manual redirect button
              TextButton(
                onPressed: () => context.go('/login'),
                child: Text(
                  'الذهاب لتسجيل الدخول الان',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: colorScheme.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Build form view
  Widget _buildFormView(ColorScheme colorScheme, ThemeData theme) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 8),

          // Header
          _buildHeader(colorScheme, theme),

          const SizedBox(height: 40),

          // Password field
          AnimatedBuilder(
            animation: _shakeAnimation,
            builder: (context, child) {
              return Transform.translate(
                offset: Offset(_shakeAnimation.value, 0),
                child: child,
              );
            },
            child: _buildPasswordField(colorScheme, theme),
          ),

          const SizedBox(height: 16),

          // Password strength indicator
          _buildStrengthIndicator(colorScheme, theme),

          const SizedBox(height: 24),

          // Password requirements
          _buildRequirementsList(colorScheme, theme),

          const SizedBox(height: 24),

          // Confirm password field
          _buildConfirmPasswordField(colorScheme, theme),

          const SizedBox(height: 8),

          // Passwords match indicator
          if (_confirmPasswordController.text.isNotEmpty)
            _buildPasswordsMatchIndicator(colorScheme, theme),

          const SizedBox(height: 16),

          // Error message
          if (_state.error != null)
            _buildErrorMessage(colorScheme, theme),

          const SizedBox(height: 24),

          // Submit button
          _buildSubmitButton(colorScheme, theme),

          const SizedBox(height: 16),

          // Cancel button
          _buildCancelButton(colorScheme, theme),
        ],
      ),
    );
  }

  /// Build header section
  Widget _buildHeader(ColorScheme colorScheme, ThemeData theme) {
    return Center(
      child: Column(
        children: [
          // Lock icon
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: colorScheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.lock_reset,
              size: 40,
              color: colorScheme.primary,
            ),
          ),

          const SizedBox(height: 24),

          // Title
          Text(
            'كلمة مرور جديدة',
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: colorScheme.onSurface,
            ),
          ),

          const SizedBox(height: 8),

          // Subtitle
          Text(
            'ادخل كلمة مرور قوية وجديدة',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: colorScheme.onSurface.withOpacity(0.7),
            ),
            textAlign: TextAlign.center,
          ),

          // Show identifier if available
          if (widget.identifier != null) ...[
            const SizedBox(height: 4),
            Directionality(
              textDirection: TextDirection.ltr,
              child: Text(
                _maskIdentifier(widget.identifier!),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.primary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  /// Mask identifier for privacy
  String _maskIdentifier(String identifier) {
    if (identifier.contains('@')) {
      final parts = identifier.split('@');
      final local = parts[0];
      final domain = parts[1];
      final masked = local.length > 2
          ? '${local[0]}${'*' * (local.length - 2)}${local[local.length - 1]}'
          : local;
      return '$masked@$domain';
    } else {
      if (identifier.length > 4) {
        return '${'*' * (identifier.length - 4)}${identifier.substring(identifier.length - 4)}';
      }
      return identifier;
    }
  }

  /// Build password input field
  Widget _buildPasswordField(ColorScheme colorScheme, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'كلمة المرور الجديدة',
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
            color: colorScheme.onSurface,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _passwordController,
          focusNode: _passwordFocusNode,
          obscureText: _state.obscurePassword,
          textInputAction: TextInputAction.next,
          onSubmitted: (_) => _confirmPasswordFocusNode.requestFocus(),
          style: TextStyle(
            fontSize: 16,
            color: colorScheme.onSurface,
          ),
          decoration: InputDecoration(
            hintText: 'ادخل كلمة المرور',
            hintStyle: TextStyle(color: colorScheme.onSurface.withOpacity(0.4)),
            prefixIcon: Icon(
              Icons.lock_outline,
              color: colorScheme.primary.withOpacity(0.7),
            ),
            suffixIcon: IconButton(
              icon: Icon(
                _state.obscurePassword
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
                color: colorScheme.onSurface.withOpacity(0.5),
              ),
              onPressed: _togglePasswordVisibility,
            ),
            filled: true,
            fillColor: colorScheme.surface,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: colorScheme.outline.withOpacity(0.3)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: colorScheme.outline.withOpacity(0.3)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: colorScheme.primary, width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: colorScheme.error, width: 2),
            ),
          ),
          inputFormatters: [
            LengthLimitingTextInputFormatter(64),
            // Prevent spaces
            FilteringTextInputFormatter.deny(RegExp(r'\s')),
          ],
        ),
      ],
    );
  }

  /// Build password strength indicator
  Widget _buildStrengthIndicator(ColorScheme colorScheme, ThemeData theme) {
    if (_passwordController.text.isEmpty) return const SizedBox.shrink();

    final strengthColor = _getStrengthColor(_state.strength);
    final strengthLabel = _getStrengthLabel(_state.strength);
    final strengthProgress = _getStrengthProgress(_state.strength);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'قوة كلمة المرور',
              style: theme.textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: strengthColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                strengthLabel,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: strengthColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        // Animated strength bar
        Stack(
          children: [
            // Background
            Container(
              height: 6,
              decoration: BoxDecoration(
                color: colorScheme.outline.withOpacity(0.2),
                borderRadius: BorderRadius.circular(3),
              ),
            ),
            // Progress
            AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeOut,
              height: 6,
              width: MediaQuery.of(context).size.width * strengthProgress * 0.85,
              decoration: BoxDecoration(
                color: strengthColor,
                borderRadius: BorderRadius.circular(3),
                boxShadow: [
                  BoxShadow(
                    color: strengthColor.withOpacity(0.4),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        // Segment indicators
        Row(
          children: List.generate(5, (index) {
            final isActive = index < PasswordStrength.values.indexOf(_state.strength) + 1;
            return Expanded(
              child: Container(
                height: 3,
                margin: EdgeInsets.only(right: index < 4 ? 4 : 0),
                decoration: BoxDecoration(
                  color: isActive
                      ? strengthColor.withOpacity(0.6)
                      : colorScheme.outline.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(1.5),
                ),
              ),
            );
          }),
        ),
      ],
    );
  }

  /// Build password requirements list
  Widget _buildRequirementsList(ColorScheme colorScheme, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.primary.withOpacity(0.03),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme.primary.withOpacity(0.1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.info_outline,
                size: 18,
                color: colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                'متطلبات كلمة المرور',
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: colorScheme.onSurface,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...List.generate(_state.requirements.length, (index) {
            final requirement = _state.requirements[index];
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 20,
                    height: 20,
                    decoration: BoxDecoration(
                      color: requirement.isMet
                          ? SahoolColors.success.withOpacity(0.1)
                          : colorScheme.outline.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      requirement.isMet ? Icons.check : Icons.circle_outlined,
                      size: 14,
                      color: requirement.isMet
                          ? SahoolColors.success
                          : colorScheme.outline,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      requirement.labelAr,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: requirement.isMet
                            ? SahoolColors.success
                            : colorScheme.onSurface.withOpacity(0.6),
                        fontWeight: requirement.isMet
                            ? FontWeight.w500
                            : FontWeight.normal,
                        decoration: requirement.isMet
                            ? TextDecoration.lineThrough
                            : null,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  /// Build confirm password input field
  Widget _buildConfirmPasswordField(ColorScheme colorScheme, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'تاكيد كلمة المرور',
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
            color: colorScheme.onSurface,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _confirmPasswordController,
          focusNode: _confirmPasswordFocusNode,
          obscureText: _state.obscureConfirmPassword,
          textInputAction: TextInputAction.done,
          onSubmitted: (_) => _submitPassword(),
          style: TextStyle(
            fontSize: 16,
            color: colorScheme.onSurface,
          ),
          decoration: InputDecoration(
            hintText: 'اعد ادخال كلمة المرور',
            hintStyle: TextStyle(color: colorScheme.onSurface.withOpacity(0.4)),
            prefixIcon: Icon(
              Icons.lock_outline,
              color: colorScheme.primary.withOpacity(0.7),
            ),
            suffixIcon: IconButton(
              icon: Icon(
                _state.obscureConfirmPassword
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
                color: colorScheme.onSurface.withOpacity(0.5),
              ),
              onPressed: _toggleConfirmPasswordVisibility,
            ),
            filled: true,
            fillColor: colorScheme.surface,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: colorScheme.outline.withOpacity(0.3)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: _confirmPasswordController.text.isNotEmpty
                    ? (_state.passwordsMatch
                        ? SahoolColors.success
                        : colorScheme.error)
                    : colorScheme.outline.withOpacity(0.3),
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: colorScheme.primary, width: 2),
            ),
          ),
          inputFormatters: [
            LengthLimitingTextInputFormatter(64),
            FilteringTextInputFormatter.deny(RegExp(r'\s')),
          ],
        ),
      ],
    );
  }

  /// Build passwords match indicator
  Widget _buildPasswordsMatchIndicator(ColorScheme colorScheme, ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Row(
        children: [
          Icon(
            _state.passwordsMatch ? Icons.check_circle : Icons.cancel,
            size: 16,
            color: _state.passwordsMatch ? SahoolColors.success : colorScheme.error,
          ),
          const SizedBox(width: 8),
          Text(
            _state.passwordsMatch
                ? 'كلمتا المرور متطابقتان'
                : 'كلمتا المرور غير متطابقتين',
            style: theme.textTheme.bodySmall?.copyWith(
              color: _state.passwordsMatch ? SahoolColors.success : colorScheme.error,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  /// Build error message
  Widget _buildErrorMessage(ColorScheme colorScheme, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
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
    );
  }

  /// Build submit button
  Widget _buildSubmitButton(ColorScheme colorScheme, ThemeData theme) {
    final canSubmit = _canSubmit();

    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: canSubmit ? _submitPassword : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: colorScheme.primary,
          foregroundColor: Colors.white,
          disabledBackgroundColor: colorScheme.onSurface.withOpacity(0.1),
          disabledForegroundColor: colorScheme.onSurface.withOpacity(0.4),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: canSubmit ? 4 : 0,
          shadowColor: colorScheme.primary.withOpacity(0.4),
        ),
        child: _state.isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.check, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'تغيير كلمة المرور',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  /// Build cancel button
  Widget _buildCancelButton(ColorScheme colorScheme, ThemeData theme) {
    return SizedBox(
      width: double.infinity,
      child: TextButton(
        onPressed: () => Navigator.of(context).pop(),
        child: Text(
          'الغاء',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: colorScheme.onSurface.withOpacity(0.6),
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
}
