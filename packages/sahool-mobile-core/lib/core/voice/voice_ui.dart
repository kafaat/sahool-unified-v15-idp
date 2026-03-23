import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'voice_service.dart';
import 'voice_commands.dart';
import 'voice_command_handler.dart';

/// SAHOOL Voice UI Components
/// مكونات واجهة الأوامر الصوتية
///
/// Includes:
/// - VoiceButton: Floating microphone button
/// - VoiceOverlay: Listening indicator overlay
/// - VoiceCommandSuggestions: Command suggestions widget
/// - VoiceTranscriptDisplay: Real-time transcript display
/// - VoiceHelpDialog: Help dialog for available commands

// ═══════════════════════════════════════════════════════════════════════════
// Voice Button Widget
// ═══════════════════════════════════════════════════════════════════════════

/// Floating microphone button for voice commands
class VoiceButton extends ConsumerStatefulWidget {
  final double size;
  final Color? activeColor;
  final Color? inactiveColor;
  final bool showPulse;
  final bool mini;
  final VoidCallback? onListeningStarted;
  final VoidCallback? onListeningStopped;
  final Function(ParsedVoiceCommand)? onCommandRecognized;

  const VoiceButton({
    super.key,
    this.size = 56,
    this.activeColor,
    this.inactiveColor,
    this.showPulse = true,
    this.mini = false,
    this.onListeningStarted,
    this.onListeningStopped,
    this.onCommandRecognized,
  });

  @override
  ConsumerState<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends ConsumerState<VoiceButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final statusAsync = ref.watch(voiceServiceStatusProvider);
    final theme = Theme.of(context);

    return statusAsync.when(
      data: (status) => _buildButton(context, status, theme),
      loading: () => _buildButton(context, VoiceServiceStatus.uninitialized, theme),
      error: (_, __) => _buildButton(context, VoiceServiceStatus.error, theme),
    );
  }

  Widget _buildButton(BuildContext context, VoiceServiceStatus status, ThemeData theme) {
    final isListening = status == VoiceServiceStatus.listening;
    final isProcessing = status == VoiceServiceStatus.processing;
    final hasError = status == VoiceServiceStatus.error;
    final isUnavailable = status == VoiceServiceStatus.unavailable;

    // Control animation
    if (isListening && widget.showPulse) {
      _pulseController.repeat(reverse: true);
    } else {
      _pulseController.stop();
      _pulseController.reset();
    }

    final activeColor = widget.activeColor ?? Colors.red.shade600;
    final inactiveColor = widget.inactiveColor ?? theme.colorScheme.primary;
    final errorColor = Colors.orange.shade600;
    final disabledColor = Colors.grey.shade400;

    final buttonColor = hasError
        ? errorColor
        : isUnavailable
            ? disabledColor
            : isListening
                ? activeColor
                : inactiveColor;

    final buttonSize = widget.mini ? widget.size * 0.75 : widget.size;

    return GestureDetector(
      onTap: isUnavailable ? null : () => _toggleListening(status),
      onLongPress: () => _showHelp(context),
      child: AnimatedBuilder(
        animation: _pulseController,
        builder: (context, child) {
          return Transform.scale(
            scale: isListening && widget.showPulse ? _pulseAnimation.value : 1.0,
            child: Container(
              width: buttonSize,
              height: buttonSize,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: buttonColor,
                boxShadow: [
                  BoxShadow(
                    color: buttonColor.withOpacity(0.4),
                    blurRadius: isListening ? 20 : 8,
                    spreadRadius: isListening ? 4 : 1,
                  ),
                ],
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Ripple rings when listening
                  if (isListening && widget.showPulse)
                    ..._buildRippleRings(buttonSize, activeColor),

                  // Main icon
                  _buildIcon(status, buttonSize),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  List<Widget> _buildRippleRings(double size, Color color) {
    return List.generate(3, (index) {
      return AnimatedBuilder(
        animation: _pulseController,
        builder: (context, child) {
          final delay = index * 0.2;
          final value = (_pulseController.value + delay) % 1.0;
          return Container(
            width: size * (1 + value * 0.6),
            height: size * (1 + value * 0.6),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: color.withOpacity((1 - value) * 0.6),
                width: 2,
              ),
            ),
          );
        },
      );
    });
  }

  Widget _buildIcon(VoiceServiceStatus status, double size) {
    final iconSize = size * 0.5;

    IconData icon;
    switch (status) {
      case VoiceServiceStatus.listening:
        icon = Icons.mic;
        break;
      case VoiceServiceStatus.processing:
        return SizedBox(
          width: iconSize,
          height: iconSize,
          child: const CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation(Colors.white),
          ),
        );
      case VoiceServiceStatus.error:
        icon = Icons.mic_off;
        break;
      case VoiceServiceStatus.unavailable:
        icon = Icons.mic_off_outlined;
        break;
      default:
        icon = Icons.mic_none;
    }

    return Icon(icon, color: Colors.white, size: iconSize);
  }

  Future<void> _toggleListening(VoiceServiceStatus status) async {
    final voiceService = ref.read(voiceServiceProvider);

    if (status == VoiceServiceStatus.listening) {
      await voiceService.stopListening();
      widget.onListeningStopped?.call();
    } else {
      await voiceService.startListening();
      widget.onListeningStarted?.call();
    }
  }

  void _showHelp(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const VoiceHelpSheet(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Floating Voice Button (FAB style)
// ═══════════════════════════════════════════════════════════════════════════

/// Positioned floating voice button
class FloatingVoiceButton extends StatelessWidget {
  final Function(ParsedVoiceCommand)? onCommand;
  final double? bottom;
  final double? right;
  final double? left;
  final double? top;

  const FloatingVoiceButton({
    super.key,
    this.onCommand,
    this.bottom = 80,
    this.right = 16,
    this.left,
    this.top,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned(
      bottom: bottom,
      right: right,
      left: left,
      top: top,
      child: VoiceButton(
        size: 64,
        onCommandRecognized: onCommand,
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Overlay Widget
// ═══════════════════════════════════════════════════════════════════════════

/// Full-screen overlay when voice is active
class VoiceOverlay extends ConsumerWidget {
  final bool showTranscript;
  final bool showSuggestions;
  final VoidCallback? onClose;

  const VoiceOverlay({
    super.key,
    this.showTranscript = true,
    this.showSuggestions = true,
    this.onClose,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusAsync = ref.watch(voiceServiceStatusProvider);
    final soundLevelAsync = ref.watch(voiceSoundLevelProvider);

    return statusAsync.when(
      data: (status) {
        if (status != VoiceServiceStatus.listening &&
            status != VoiceServiceStatus.processing) {
          return const SizedBox.shrink();
        }

        return Material(
          color: Colors.black.withOpacity(0.85),
          child: SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Close button
                Align(
                  alignment: Alignment.topRight,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: IconButton(
                      onPressed: () {
                        ref.read(voiceServiceProvider).cancelListening();
                        onClose?.call();
                      },
                      icon: const Icon(Icons.close, color: Colors.white70, size: 32),
                    ),
                  ),
                ),

                const Spacer(),

                // Listening indicator
                _VoiceWaveform(
                  soundLevel: soundLevelAsync.valueOrNull ?? 0,
                  isListening: status == VoiceServiceStatus.listening,
                ),

                const SizedBox(height: 32),

                // Status text
                Text(
                  status == VoiceServiceStatus.listening
                      ? 'جاري الاستماع...'
                      : 'جاري المعالجة...',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.w500,
                  ),
                ),

                const SizedBox(height: 8),

                Text(
                  status == VoiceServiceStatus.listening
                      ? 'Listening...'
                      : 'Processing...',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 16,
                  ),
                ),

                const SizedBox(height: 48),

                // Transcript
                if (showTranscript) const VoiceTranscriptDisplay(),

                const Spacer(),

                // Suggestions
                if (showSuggestions) const VoiceCommandSuggestions(),

                const SizedBox(height: 32),

                // Cancel button
                TextButton.icon(
                  onPressed: () {
                    ref.read(voiceServiceProvider).cancelListening();
                    onClose?.call();
                  },
                  icon: const Icon(Icons.close, color: Colors.white70),
                  label: const Text(
                    'إلغاء / Cancel',
                    style: TextStyle(color: Colors.white70),
                  ),
                ),

                const SizedBox(height: 24),
              ],
            ),
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }
}

/// Voice waveform visualization
class _VoiceWaveform extends StatefulWidget {
  final double soundLevel;
  final bool isListening;

  const _VoiceWaveform({
    required this.soundLevel,
    required this.isListening,
  });

  @override
  State<_VoiceWaveform> createState() => _VoiceWaveformState();
}

class _VoiceWaveformState extends State<_VoiceWaveform>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return SizedBox(
          width: 200,
          height: 100,
          child: CustomPaint(
            painter: _WaveformPainter(
              soundLevel: widget.soundLevel,
              animationValue: _controller.value,
              isListening: widget.isListening,
            ),
          ),
        );
      },
    );
  }
}

class _WaveformPainter extends CustomPainter {
  final double soundLevel;
  final double animationValue;
  final bool isListening;

  _WaveformPainter({
    required this.soundLevel,
    required this.animationValue,
    required this.isListening,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = isListening ? Colors.green.shade400 : Colors.grey
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final centerY = size.height / 2;
    const barCount = 9;
    final barWidth = size.width / (barCount * 2);

    for (int i = 0; i < barCount; i++) {
      final x = (i + 0.5) * size.width / barCount;
      final phase = (animationValue + i * 0.1) * 2 * pi;
      final amplitude = isListening
          ? 10 + (soundLevel.clamp(0, 10) * 3) + sin(phase) * 15
          : 5 + sin(phase) * 5;

      canvas.drawLine(
        Offset(x, centerY - amplitude),
        Offset(x, centerY + amplitude),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(_WaveformPainter oldDelegate) => true;
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Transcript Display
// ═══════════════════════════════════════════════════════════════════════════

/// Real-time speech transcript display
class VoiceTranscriptDisplay extends ConsumerWidget {
  final TextStyle? textStyle;
  final int maxLines;

  const VoiceTranscriptDisplay({
    super.key,
    this.textStyle,
    this.maxLines = 3,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final resultAsync = ref.watch(speechResultProvider);

    return resultAsync.when(
      data: (result) {
        if (result.recognizedText.isEmpty) {
          return const SizedBox.shrink();
        }

        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 24),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: result.isFinal
                  ? Colors.green.withOpacity(0.5)
                  : Colors.white.withOpacity(0.2),
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Icon(
                    result.isFinal ? Icons.check_circle : Icons.pending,
                    color: result.isFinal ? Colors.green : Colors.white54,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    result.isFinal ? 'تم التعرف' : 'جاري التعرف...',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.6),
                      fontSize: 12,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    '${(result.confidence * 100).toStringAsFixed(0)}%',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.6),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                '"${result.recognizedText}"',
                style: textStyle ??
                    const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.w500,
                    ),
                textAlign: TextAlign.center,
                maxLines: maxLines,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Command Suggestions
// ═══════════════════════════════════════════════════════════════════════════

/// Widget showing command suggestions
class VoiceCommandSuggestions extends ConsumerWidget {
  final int maxSuggestions;
  final Function(VoiceCommandDefinition)? onSuggestionTapped;

  const VoiceCommandSuggestions({
    super.key,
    this.maxSuggestions = 4,
    this.onSuggestionTapped,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final suggestionsAsync = ref.watch(commandSuggestionsProvider);

    return suggestionsAsync.when(
      data: (suggestions) {
        if (suggestions.isEmpty) {
          // Show default suggestions
          return _buildDefaultSuggestions(context);
        }

        return _buildSuggestionsList(context, suggestions.take(maxSuggestions).toList());
      },
      loading: () => _buildDefaultSuggestions(context),
      error: (_, __) => const SizedBox.shrink(),
    );
  }

  Widget _buildDefaultSuggestions(BuildContext context) {
    final defaults = [
      VoiceCommandRegistry.getCommand(VoiceCommandType.openFields),
      VoiceCommandRegistry.getCommand(VoiceCommandType.openWeather),
      VoiceCommandRegistry.getCommand(VoiceCommandType.openTasks),
      VoiceCommandRegistry.getCommand(VoiceCommandType.help),
    ].whereType<VoiceCommandDefinition>().toList();

    return _buildSuggestionsList(context, defaults);
  }

  Widget _buildSuggestionsList(BuildContext context, List<VoiceCommandDefinition> suggestions) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          'جرب أن تقول / Try saying:',
          style: TextStyle(
            color: Colors.white.withOpacity(0.5),
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          alignment: WrapAlignment.center,
          children: suggestions.map((cmd) {
            return _SuggestionChip(
              command: cmd,
              onTap: onSuggestionTapped != null ? () => onSuggestionTapped!(cmd) : null,
            );
          }).toList(),
        ),
      ],
    );
  }
}

class _SuggestionChip extends StatelessWidget {
  final VoiceCommandDefinition command;
  final VoidCallback? onTap;

  const _SuggestionChip({
    required this.command,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white.withOpacity(0.2)),
        ),
        child: Text(
          '"${command.nameAr}"',
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 14,
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Status Indicator
// ═══════════════════════════════════════════════════════════════════════════

/// Compact status indicator for app bar or other locations
class VoiceStatusIndicator extends ConsumerWidget {
  final bool showText;

  const VoiceStatusIndicator({
    super.key,
    this.showText = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusAsync = ref.watch(voiceServiceStatusProvider);

    return statusAsync.when(
      data: (status) => _buildIndicator(context, status),
      loading: () => const SizedBox.shrink(),
      error: (_, __) => _buildIndicator(context, VoiceServiceStatus.error),
    );
  }

  Widget _buildIndicator(BuildContext context, VoiceServiceStatus status) {
    if (status == VoiceServiceStatus.ready ||
        status == VoiceServiceStatus.uninitialized) {
      return const SizedBox.shrink();
    }

    final (color, textAr, textEn) = switch (status) {
      VoiceServiceStatus.listening => (Colors.red, 'جاري الاستماع', 'Listening'),
      VoiceServiceStatus.processing => (Colors.blue, 'جاري المعالجة', 'Processing'),
      VoiceServiceStatus.error => (Colors.orange, 'خطأ', 'Error'),
      VoiceServiceStatus.unavailable => (Colors.grey, 'غير متاح', 'Unavailable'),
      _ => (Colors.grey, '', ''),
    };

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (status == VoiceServiceStatus.listening)
            const _PulsingDot(color: Colors.white)
          else if (status == VoiceServiceStatus.processing)
            const SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation(Colors.white),
              ),
            )
          else
            Icon(
              status == VoiceServiceStatus.error ? Icons.error_outline : Icons.mic_off,
              color: Colors.white,
              size: 14,
            ),
          if (showText) ...[
            const SizedBox(width: 8),
            Text(
              textAr,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

/// Pulsing dot indicator
class _PulsingDot extends StatefulWidget {
  final Color color;
  final double size;

  const _PulsingDot({
    required this.color,
    this.size = 12.0,
  });

  @override
  State<_PulsingDot> createState() => _PulsingDotState();
}

class _PulsingDotState extends State<_PulsingDot>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Container(
          width: widget.size,
          height: widget.size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: widget.color.withOpacity(0.5 + _controller.value * 0.5),
          ),
        );
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Help Sheet
// ═══════════════════════════════════════════════════════════════════════════

/// Bottom sheet showing available voice commands
class VoiceHelpSheet extends ConsumerWidget {
  const VoiceHelpSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final commands = ref.watch(voiceCommandDefinitionsProvider);
    final categories = ref.watch(voiceCommandCategoriesProvider);

    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.4,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, scrollController) {
        return DecoratedBox(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            children: [
              // Handle
              Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(top: 12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),

              // Header
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(Icons.mic, color: Colors.green.shade600, size: 24),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'الأوامر الصوتية',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            'Voice Commands',
                            style: TextStyle(
                              color: Colors.grey.shade600,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                    ),
                  ],
                ),
              ),

              // Instructions
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Text(
                  'اضغط على زر الميكروفون وقل أي من هذه الأوامر',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ),

              const SizedBox(height: 16),

              // Commands list
              Expanded(
                child: ListView.builder(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: categories.length,
                  itemBuilder: (context, index) {
                    final category = categories[index];
                    final categoryCommands = commands
                        .where((c) => c.type.categoryEn == category && c.type != VoiceCommandType.unknown)
                        .toList();

                    if (categoryCommands.isEmpty) {
                      return const SizedBox.shrink();
                    }

                    return _CommandCategorySection(
                      category: category,
                      commands: categoryCommands,
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _CommandCategorySection extends StatelessWidget {
  final String category;
  final List<VoiceCommandDefinition> commands;

  const _CommandCategorySection({
    required this.category,
    required this.commands,
  });

  @override
  Widget build(BuildContext context) {
    final categoryAr = commands.firstOrNull?.type.categoryAr ?? category;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Row(
            children: [
              Text(
                categoryAr,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.green.shade700,
                ),
              ),
              Text(
                ' / $category',
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
        ...commands.map((cmd) => _CommandHelpTile(command: cmd)),
        const SizedBox(height: 8),
      ],
    );
  }
}

class _CommandHelpTile extends StatelessWidget {
  final VoiceCommandDefinition command;

  const _CommandHelpTile({required this.command});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Command name
          Row(
            children: [
              const Icon(Icons.record_voice_over, size: 16, color: Colors.green),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '"${command.nameAr}"',
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 15,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 4),

          // English name
          Text(
            '"${command.nameEn}"',
            style: TextStyle(
              color: Colors.grey.shade600,
              fontSize: 13,
            ),
          ),

          const SizedBox(height: 8),

          // Description
          Text(
            command.descriptionAr,
            style: TextStyle(
              color: Colors.grey.shade700,
              fontSize: 13,
            ),
          ),

          // Examples
          if (command.examplesAr.isNotEmpty) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: command.examplesAr.map((example) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    example,
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.green.shade700,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Control Mixin
// ═══════════════════════════════════════════════════════════════════════════

/// Mixin to add voice control to any screen
mixin VoiceControlMixin<T extends ConsumerStatefulWidget> on ConsumerState<T> {
  VoiceCommandHandler? _voiceHandler;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initVoiceControl();
    });
  }

  void _initVoiceControl() {
    _voiceHandler = ref.read(voiceCommandHandlerProvider);
    _voiceHandler?.setBuildContext(context);

    // Override with screen-specific handlers if needed
    setupVoiceHandlers();
  }

  /// Override to set up screen-specific voice handlers
  void setupVoiceHandlers() {}

  /// Register a custom handler for this screen
  void registerVoiceHandler(
    VoiceCommandType type,
    Future<CommandHandlerResult> Function(ParsedVoiceCommand, CommandContext) handler,
  ) {
    _voiceHandler?.registerHandler(type, handler);
  }

  /// Update voice context (call when route changes)
  void updateVoiceContext({String? route, String? fieldId}) {
    _voiceHandler?.updateContext(
      CommandContext(
        buildContext: context,
        currentRoute: route,
        currentFieldId: fieldId,
      ),
    );
  }
}
