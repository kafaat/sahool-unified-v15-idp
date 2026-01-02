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
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/atmosphere_theme.dart';

class VoiceControlButton extends StatefulWidget {
  const VoiceControlButton({super.key});

  @override
  State<VoiceControlButton> createState() => _VoiceControlButtonState();
}

class _VoiceControlButtonState extends State<VoiceControlButton>
    with SingleTickerProviderStateMixin {
  bool _isListening = false;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
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
    super.dispose();
  }

  void _toggleListening() {
    setState(() {
      _isListening = !_isListening;
    });

    if (_isListening) {
      // Water flow haptic pattern
      HapticFeedback.heavyImpact();
      _pulseController.forward();
      _startListening();
    } else {
      HapticFeedback.lightImpact();
      _pulseController.stop();
      _stopListening();
    }
  }

  void _startListening() {
    // In real implementation, use speech_to_text package
    // Example voice commands:
    // "كيف حالة الحقل رقم 4؟" -> Show Field 4 status
    // "شغل الري في الحقل 7" -> Start irrigation
    // "أظهر التنبيهات" -> Show alerts

    // Simulate listening for demo
    Future.delayed(const Duration(seconds: 3), () {
      if (_isListening) {
        _showVoiceResponse();
      }
    });
  }

  void _stopListening() {
    // Stop speech recognition
  }

  void _showVoiceResponse() {
    HapticFeedback.mediumImpact();
    setState(() {
      _isListening = false;
    });
    _pulseController.stop();

    // Show response dialog
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AtmosphereColors.bgSecondary,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
          side: BorderSide(color: AtmosphereColors.glassBorder),
        ),
        title: Row(
          children: [
            Icon(Icons.mic, color: AtmosphereColors.success),
            const SizedBox(width: AtmosphereSpacing.sm),
            Text(
              'التحكم الصوتي',
              style: AtmosphereTypography.headlineLarge,
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'سمعت: "كيف حالة الحقل رقم 4؟"',
              style: AtmosphereTypography.bodyMedium,
            ),
            const SizedBox(height: AtmosphereSpacing.md),
            Container(
              padding: const EdgeInsets.all(AtmosphereSpacing.md),
              decoration: BoxDecoration(
                color: AtmosphereColors.successGlow,
                borderRadius: BorderRadius.circular(AtmosphereRadius.md),
                border: Border.all(color: AtmosphereColors.success),
              ),
              child: Text(
                'الحقل سليم ✓\n'
                'رطوبة التربة: 64%\n'
                'الحرارة: 28°C\n'
                'التوصية: سقاية خفيفة اليوم',
                style: AtmosphereTypography.bodyLarge.copyWith(
                  color: AtmosphereColors.success,
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'حسناً',
              style: TextStyle(color: AtmosphereColors.success),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Hint Text
        AnimatedOpacity(
          opacity: _isListening ? 0.0 : 1.0,
          duration: const Duration(milliseconds: 300),
          child: Text(
            'اضغط للتحكم الصوتي',
            style: AtmosphereTypography.bodySmall,
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
                        : AtmosphereColors.successGradient,
                    boxShadow: [
                      BoxShadow(
                        color: AtmosphereColors.successGlow,
                        blurRadius: _isListening ? 40 : 20,
                        spreadRadius: _isListening ? 4 : 2,
                      ),
                    ],
                  ),
                  child: Icon(
                    _isListening ? Icons.graphic_eq : Icons.mic,
                    color: AtmosphereColors.bgPrimary,
                    size: 28,
                  ),
                ),
              );
            },
          ),
        ),

        // Listening Indicator
        AnimatedOpacity(
          opacity: _isListening ? 1.0 : 0.0,
          duration: const Duration(milliseconds: 300),
          child: Column(
            children: [
              const SizedBox(height: AtmosphereSpacing.sm),
              Text(
                'أستمع...',
                style: AtmosphereTypography.bodySmall.copyWith(
                  color: AtmosphereColors.success,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
