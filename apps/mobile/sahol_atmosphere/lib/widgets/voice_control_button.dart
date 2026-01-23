// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Voice Control Button
// زر التحكم الصوتي
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Voice-First Interface for Arabic Support
// واجهة الصوت أولاً مع دعم العربية
//
// Features:
// - Animated glow effect
// - Haptic feedback patterns
// - Pulse animation when listening
// - Error handling for speech recognition
// - Full accessibility support
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/atmosphere_theme.dart';

/// Voice control states for the button
enum VoiceControlState {
  /// Idle state - ready to listen
  idle,

  /// Actively listening for voice input
  listening,

  /// Processing the voice input
  processing,

  /// Error occurred during voice operation
  error,
}

/// Voice control button for hands-free farm management
///
/// Provides voice-first interface with Arabic language support.
/// Uses speech recognition to accept commands like:
/// - "How is field 4?" / "كيف حالة الحقل رقم 4؟"
/// - "Start irrigation in field 7" / "شغل الري في الحقل 7"
/// - "Show alerts" / "أظهر التنبيهات"
class VoiceControlButton extends StatefulWidget {
  /// Callback when a voice command is recognized
  final void Function(String command)? onCommand;

  /// Callback when an error occurs
  final void Function(String error)? onError;

  const VoiceControlButton({
    super.key,
    this.onCommand,
    this.onError,
  });

  @override
  State<VoiceControlButton> createState() => _VoiceControlButtonState();
}

class _VoiceControlButtonState extends State<VoiceControlButton>
    with SingleTickerProviderStateMixin {
  VoiceControlState _state = VoiceControlState.idle;
  String? _errorMessage;
  Timer? _listeningTimeout;

  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  /// Maximum listening duration before auto-stop (in seconds)
  static const int _maxListeningDuration = 10;

  bool get _isListening => _state == VoiceControlState.listening;
  bool get _isProcessing => _state == VoiceControlState.processing;
  bool get _hasError => _state == VoiceControlState.error;

  @override
  void initState() {
    super.initState();
    _initializeAnimation();
  }

  /// Initialize pulse animation for listening state
  void _initializeAnimation() {
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _pulseController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _pulseController.reverse();
      } else if (status == AnimationStatus.dismissed && _isListening) {
        _pulseController.forward();
      }
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _listeningTimeout?.cancel();
    super.dispose();
  }

  /// Toggle voice control state
  void _toggleListening() {
    if (_isListening || _isProcessing) {
      _stopListening();
    } else {
      _startListening();
    }
  }

  /// Start listening for voice input
  void _startListening() {
    setState(() {
      _state = VoiceControlState.listening;
      _errorMessage = null;
    });

    // Provide haptic feedback
    HapticFeedback.heavyImpact();
    _pulseController.forward();

    // Set timeout to prevent indefinite listening
    _listeningTimeout?.cancel();
    _listeningTimeout = Timer(
      Duration(seconds: _maxListeningDuration),
      () {
        if (_isListening && mounted) {
          _handleTimeout();
        }
      },
    );

    // In real implementation, use speech_to_text package:
    // try {
    //   await _speechToText.listen(
    //     onResult: _onSpeechResult,
    //     localeId: 'ar_SA', // Arabic Saudi Arabia
    //     listenMode: ListenMode.confirmation,
    //   );
    // } catch (e) {
    //   _handleError('Failed to start speech recognition');
    // }

    // Simulate listening for demo
    Future.delayed(const Duration(seconds: 3), () {
      if (_isListening && mounted) {
        _processVoiceInput('كيف حالة الحقل رقم 4؟');
      }
    });
  }

  /// Stop listening for voice input
  void _stopListening() {
    _listeningTimeout?.cancel();
    _pulseController.stop();

    if (mounted) {
      setState(() {
        if (_state == VoiceControlState.listening) {
          _state = VoiceControlState.idle;
        }
      });
    }

    HapticFeedback.lightImpact();

    // In real implementation:
    // await _speechToText.stop();
  }

  /// Handle listening timeout
  void _handleTimeout() {
    _stopListening();
    _handleError('No voice input detected. Please try again.');
  }

  /// Handle voice recognition error
  void _handleError(String message) {
    if (mounted) {
      setState(() {
        _state = VoiceControlState.error;
        _errorMessage = message;
      });

      widget.onError?.call(message);

      // Reset to idle after showing error
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted && _hasError) {
          setState(() {
            _state = VoiceControlState.idle;
            _errorMessage = null;
          });
        }
      });
    }

    if (kDebugMode) {
      debugPrint('VoiceControl Error: $message');
    }
  }

  /// Process recognized voice input
  void _processVoiceInput(String text) {
    _listeningTimeout?.cancel();
    _pulseController.stop();

    if (mounted) {
      setState(() {
        _state = VoiceControlState.processing;
      });
    }

    HapticFeedback.mediumImpact();
    widget.onCommand?.call(text);

    // Show response
    _showVoiceResponse(text);
  }

  /// Show voice response dialog
  void _showVoiceResponse(String recognizedText) {
    if (!mounted) return;

    setState(() {
      _state = VoiceControlState.idle;
    });

    // Show response dialog
    showDialog(
      context: context,
      builder: (dialogContext) => Semantics(
        label: 'Voice command response',
        child: AlertDialog(
          backgroundColor: AtmosphereColors.bgSecondary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
            side: const BorderSide(color: AtmosphereColors.glassBorder),
          ),
          title: Row(
            children: [
              Icon(
                Icons.mic,
                color: AtmosphereColors.success,
                semanticLabel: 'Voice control',
              ),
              const SizedBox(width: AtmosphereSpacing.sm),
              Expanded(
                child: Text(
                  'التحكم الصوتي',
                  style: AtmosphereTypography.headlineLarge,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Semantics(
                label: 'Recognized command: $recognizedText',
                child: Text(
                  'سمعت: "$recognizedText"',
                  style: AtmosphereTypography.bodyMedium,
                ),
              ),
              const SizedBox(height: AtmosphereSpacing.md),
              _buildResponseCard(),
            ],
          ),
          actions: [
            Semantics(
              label: 'Dismiss dialog',
              button: true,
              child: TextButton(
                onPressed: () => Navigator.pop(dialogContext),
                child: Text(
                  'حسناً',
                  style: TextStyle(color: AtmosphereColors.success),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Build the response card showing field status
  Widget _buildResponseCard() {
    return Container(
      padding: const EdgeInsets.all(AtmosphereSpacing.md),
      decoration: BoxDecoration(
        color: AtmosphereColors.successGlow,
        borderRadius: BorderRadius.circular(AtmosphereRadius.md),
        border: Border.all(color: AtmosphereColors.success),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status row with icon instead of emoji
          Row(
            children: [
              Icon(
                Icons.check_circle,
                color: AtmosphereColors.success,
                size: 18,
                semanticLabel: 'Field is healthy',
              ),
              const SizedBox(width: AtmosphereSpacing.sm),
              Text(
                'الحقل سليم',
                style: AtmosphereTypography.bodyLarge.copyWith(
                  color: AtmosphereColors.success,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: AtmosphereSpacing.sm),
          // Metrics
          Text(
            'رطوبة التربة: 64%',
            style: AtmosphereTypography.bodyMedium.copyWith(
              color: AtmosphereColors.success,
            ),
          ),
          Text(
            'الحرارة: 28 درجة مئوية',
            style: AtmosphereTypography.bodyMedium.copyWith(
              color: AtmosphereColors.success,
            ),
          ),
          const SizedBox(height: AtmosphereSpacing.sm),
          // Recommendation
          Text(
            'التوصية: سقاية خفيفة اليوم',
            style: AtmosphereTypography.bodyMedium.copyWith(
              color: AtmosphereColors.success,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  /// Get the current status text for accessibility
  String get _statusText {
    switch (_state) {
      case VoiceControlState.idle:
        return 'Press to start voice control';
      case VoiceControlState.listening:
        return 'Listening for voice command';
      case VoiceControlState.processing:
        return 'Processing voice command';
      case VoiceControlState.error:
        return 'Error: ${_errorMessage ?? "Unknown error"}';
    }
  }

  /// Get the Arabic status text
  String get _statusTextAr {
    switch (_state) {
      case VoiceControlState.idle:
        return 'اضغط للتحكم الصوتي';
      case VoiceControlState.listening:
        return 'أستمع...';
      case VoiceControlState.processing:
        return 'جاري المعالجة...';
      case VoiceControlState.error:
        return 'خطأ';
    }
  }

  /// Get button color based on state
  Color get _buttonColor {
    if (_hasError) return AtmosphereColors.alert;
    return AtmosphereColors.success;
  }

  /// Get button glow color based on state
  Color get _buttonGlowColor {
    if (_hasError) return AtmosphereColors.alertGlow;
    return AtmosphereColors.successGlow;
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Voice control button',
      hint: _statusText,
      button: true,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Hint Text (shown when idle)
          AnimatedOpacity(
            opacity: _state == VoiceControlState.idle ? 1.0 : 0.0,
            duration: const Duration(milliseconds: 300),
            child: ExcludeSemantics(
              child: Text(
                'اضغط للتحكم الصوتي',
                style: AtmosphereTypography.bodySmall,
              ),
            ),
          ),
          const SizedBox(height: AtmosphereSpacing.sm),

          // Main Button
          GestureDetector(
            onTap: _toggleListening,
            child: AnimatedBuilder(
              animation: _pulseAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: _isListening ? _pulseAnimation.value : 1.0,
                  child: Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: _isListening
                          ? const LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: [
                                Color(0xFF22C55E),
                                Color(0xFF16A34A),
                              ],
                            )
                          : _hasError
                              ? const LinearGradient(
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                  colors: [
                                    Color(0xFFF87171),
                                    Color(0xFFDC2626),
                                  ],
                                )
                              : AtmosphereColors.successGradient,
                      boxShadow: [
                        BoxShadow(
                          color: _buttonGlowColor,
                          blurRadius: _isListening ? 40 : 20,
                          spreadRadius: _isListening ? 4 : 2,
                        ),
                      ],
                    ),
                    child: Icon(
                      _getButtonIcon(),
                      color: AtmosphereColors.bgPrimary,
                      size: 28,
                      semanticLabel: _statusText,
                    ),
                  ),
                );
              },
            ),
          ),

          // Status Indicator
          AnimatedOpacity(
            opacity: _state != VoiceControlState.idle ? 1.0 : 0.0,
            duration: const Duration(milliseconds: 300),
            child: Column(
              children: [
                const SizedBox(height: AtmosphereSpacing.sm),
                ExcludeSemantics(
                  child: Text(
                    _statusTextAr,
                    style: AtmosphereTypography.bodySmall.copyWith(
                      color: _buttonColor,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Get the appropriate icon based on current state
  IconData _getButtonIcon() {
    switch (_state) {
      case VoiceControlState.idle:
        return Icons.mic;
      case VoiceControlState.listening:
        return Icons.graphic_eq;
      case VoiceControlState.processing:
        return Icons.hourglass_empty;
      case VoiceControlState.error:
        return Icons.error_outline;
    }
  }
}
