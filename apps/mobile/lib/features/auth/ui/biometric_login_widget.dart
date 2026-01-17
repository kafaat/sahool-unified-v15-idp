import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';

import '../../../core/auth/biometric_service.dart';
import '../../../core/theme/sahool_theme.dart';

/// SAHOOL Biometric Login Widget
/// ودجت تسجيل الدخول بالبصمة
///
/// Displays a fingerprint/face ID button when biometric is available and enabled.
/// Integrates with BiometricService for authentication.

class BiometricLoginWidget extends ConsumerStatefulWidget {
  /// Callback when biometric authentication succeeds
  final VoidCallback onSuccess;

  /// Callback when biometric authentication fails
  final VoidCallback? onError;

  /// Whether to show as a large button or small icon
  final bool compact;

  const BiometricLoginWidget({
    super.key,
    required this.onSuccess,
    this.onError,
    this.compact = false,
  });

  @override
  ConsumerState<BiometricLoginWidget> createState() =>
      _BiometricLoginWidgetState();
}

class _BiometricLoginWidgetState extends ConsumerState<BiometricLoginWidget>
    with SingleTickerProviderStateMixin {
  bool _isAvailable = false;
  bool _isEnabled = false;
  bool _isAuthenticating = false;
  String _biometricName = 'البصمة';
  BiometricType? _primaryBiometricType;

  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();

    // Setup pulse animation
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.15).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    // Check biometric availability
    _checkBiometricStatus();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _checkBiometricStatus() async {
    final biometricService = ref.read(biometricServiceProvider);

    final available = await biometricService.isAvailable();
    final enabled = await biometricService.isEnabled();
    final name = await biometricService.getPrimaryBiometricName();
    final biometrics = await biometricService.getAvailableBiometrics();

    if (mounted) {
      setState(() {
        _isAvailable = available;
        _isEnabled = enabled;
        _biometricName = name;
        _primaryBiometricType = biometrics.isNotEmpty ? biometrics.first : null;
      });

      // Start pulse animation if biometric is ready
      if (available && enabled) {
        _pulseController.repeat(reverse: true);
      }
    }
  }

  Future<void> _authenticate() async {
    if (_isAuthenticating) return;

    setState(() => _isAuthenticating = true);
    _pulseController.stop();

    try {
      final biometricService = ref.read(biometricServiceProvider);
      final authenticated = await biometricService.authenticate(
        reason: 'قم بالتحقق لتسجيل الدخول إلى سهول',
      );

      if (authenticated) {
        widget.onSuccess();
      } else {
        widget.onError?.call();
      }
    } on BiometricException catch (e) {
      _showErrorSnackBar(e.message);
      widget.onError?.call();
    } catch (e) {
      _showErrorSnackBar('حدث خطأ في التحقق من البصمة');
      widget.onError?.call();
    } finally {
      if (mounted) {
        setState(() => _isAuthenticating = false);
        if (_isAvailable && _isEnabled) {
          _pulseController.repeat(reverse: true);
        }
      }
    }
  }

  void _showErrorSnackBar(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  IconData _getBiometricIcon() {
    if (_primaryBiometricType == BiometricType.face) {
      return Icons.face;
    }
    return Icons.fingerprint;
  }

  @override
  Widget build(BuildContext context) {
    // Don't show if biometric is not available or not enabled
    if (!_isAvailable || !_isEnabled) {
      return const SizedBox.shrink();
    }

    if (widget.compact) {
      return _buildCompactButton();
    }

    return _buildFullButton();
  }

  /// Build compact icon button
  Widget _buildCompactButton() {
    return AnimatedBuilder(
      animation: _pulseAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _isAuthenticating ? 1.0 : _pulseAnimation.value,
          child: child,
        );
      },
      child: IconButton(
        onPressed: _isAuthenticating ? null : _authenticate,
        icon: _isAuthenticating
            ? SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: SahoolColors.primary,
                ),
              )
            : Icon(
                _getBiometricIcon(),
                size: 32,
                color: SahoolColors.primary,
              ),
        style: IconButton.styleFrom(
          backgroundColor: SahoolColors.primary.withOpacity(0.1),
          padding: const EdgeInsets.all(12),
        ),
      ),
    );
  }

  /// Build full button with text
  Widget _buildFullButton() {
    return AnimatedBuilder(
      animation: _pulseAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _isAuthenticating ? 1.0 : _pulseAnimation.value,
          child: child,
        );
      },
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: SahoolColors.primary.withOpacity(0.2),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: _isAuthenticating ? null : _authenticate,
            borderRadius: BorderRadius.circular(16),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 32),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    SahoolColors.primary,
                    SahoolColors.primary.withOpacity(0.8),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (_isAuthenticating)
                    const SizedBox(
                      width: 28,
                      height: 28,
                      child: CircularProgressIndicator(
                        strokeWidth: 3,
                        color: Colors.white,
                      ),
                    )
                  else
                    Icon(
                      _getBiometricIcon(),
                      size: 32,
                      color: Colors.white,
                    ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'تسجيل الدخول بـ$_biometricName',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'انقر للمتابعة',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Biometric Quick Login Button for app bar or floating button
class BiometricQuickButton extends ConsumerStatefulWidget {
  final VoidCallback onSuccess;
  final double size;

  const BiometricQuickButton({
    super.key,
    required this.onSuccess,
    this.size = 56,
  });

  @override
  ConsumerState<BiometricQuickButton> createState() =>
      _BiometricQuickButtonState();
}

class _BiometricQuickButtonState extends ConsumerState<BiometricQuickButton> {
  bool _isAvailable = false;
  bool _isEnabled = false;

  @override
  void initState() {
    super.initState();
    _checkStatus();
  }

  Future<void> _checkStatus() async {
    final biometricService = ref.read(biometricServiceProvider);
    final available = await biometricService.isAvailable();
    final enabled = await biometricService.isEnabled();

    if (mounted) {
      setState(() {
        _isAvailable = available;
        _isEnabled = enabled;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isAvailable || !_isEnabled) {
      return const SizedBox.shrink();
    }

    return BiometricLoginWidget(
      onSuccess: widget.onSuccess,
      compact: true,
    );
  }
}
