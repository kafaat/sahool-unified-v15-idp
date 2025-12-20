import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'voice_command_service.dart';

/// SAHOOL Voice Button Widget
/// زر الأوامر الصوتية
///
/// Features:
/// - Animated microphone button
/// - Visual feedback during listening
/// - Status indicators

class VoiceButtonWidget extends ConsumerStatefulWidget {
  final VoidCallback? onCommandReceived;
  final Function(VoiceCommand)? onCommand;
  final double size;
  final Color? activeColor;
  final Color? inactiveColor;

  const VoiceButtonWidget({
    super.key,
    this.onCommandReceived,
    this.onCommand,
    this.size = 56,
    this.activeColor,
    this.inactiveColor,
  });

  @override
  ConsumerState<VoiceButtonWidget> createState() => _VoiceButtonWidgetState();
}

class _VoiceButtonWidgetState extends ConsumerState<VoiceButtonWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.3).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final statusAsync = ref.watch(voiceStatusProvider);

    return statusAsync.when(
      data: (status) => _buildButton(context, status),
      loading: () => _buildButton(context, VoiceStatus.idle),
      error: (_, __) => _buildButton(context, VoiceStatus.error),
    );
  }

  Widget _buildButton(BuildContext context, VoiceStatus status) {
    final isListening = status == VoiceStatus.listening;
    final isProcessing = status == VoiceStatus.processing;
    final hasError = status == VoiceStatus.error;

    // Control animation
    if (isListening) {
      _animationController.repeat(reverse: true);
    } else {
      _animationController.stop();
      _animationController.reset();
    }

    final activeColor = widget.activeColor ?? Colors.red;
    final inactiveColor = widget.inactiveColor ?? Colors.green;

    return GestureDetector(
      onTap: () => _toggleListening(status),
      onLongPress: () => _showHelp(context),
      child: AnimatedBuilder(
        animation: _animationController,
        builder: (context, child) {
          return Transform.scale(
            scale: isListening ? _pulseAnimation.value : 1.0,
            child: Container(
              width: widget.size,
              height: widget.size,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isListening ? activeColor : inactiveColor,
                boxShadow: [
                  BoxShadow(
                    color: (isListening ? activeColor : inactiveColor)
                        .withOpacity(0.4),
                    blurRadius: isListening ? 20 : 8,
                    spreadRadius: isListening ? 5 : 2,
                  ),
                ],
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Ripple effect when listening
                  if (isListening)
                    ...List.generate(3, (index) {
                      return AnimatedBuilder(
                        animation: _animationController,
                        builder: (context, child) {
                          final delay = index * 0.2;
                          final value = (_animationController.value + delay) % 1.0;
                          return Container(
                            width: widget.size * (1 + value * 0.5),
                            height: widget.size * (1 + value * 0.5),
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: activeColor.withOpacity(1 - value),
                                width: 2,
                              ),
                            ),
                          );
                        },
                      );
                    }),

                  // Icon
                  Icon(
                    hasError
                        ? Icons.mic_off
                        : isProcessing
                            ? Icons.hourglass_empty
                            : Icons.mic,
                    color: Colors.white,
                    size: widget.size * 0.5,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  void _toggleListening(VoiceStatus status) async {
    final service = ref.read(voiceCommandServiceProvider);

    if (status == VoiceStatus.listening) {
      await service.stopListening();
    } else {
      await service.startListening();

      // Listen for result
      final subscription = service.resultStream.listen((result) {
        if (result.command != null) {
          widget.onCommand?.call(result.command!);
        }
        widget.onCommandReceived?.call();
      });

      // Auto-cancel after timeout
      Future.delayed(const Duration(seconds: 10), () {
        if (service.isListening) {
          service.stopListening();
        }
        subscription.cancel();
      });
    }
  }

  void _showHelp(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => const VoiceHelpSheet(),
    );
  }
}

/// Floating Voice Button
class FloatingVoiceButton extends ConsumerWidget {
  final Function(VoiceCommand)? onCommand;

  const FloatingVoiceButton({
    super.key,
    this.onCommand,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Positioned(
      bottom: 80,
      right: 16,
      child: VoiceButtonWidget(
        onCommand: onCommand,
        size: 64,
      ),
    );
  }
}

/// صفحة مساعدة الأوامر الصوتية
class VoiceHelpSheet extends ConsumerWidget {
  const VoiceHelpSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final helpItems = ref.watch(voiceHelpProvider);

    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.green.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.mic, color: Colors.green),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'الأوامر الصوتية',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'اضغط على زر الميكروفون وقل أي من هذه الأوامر:',
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.separated(
                controller: scrollController,
                itemCount: helpItems.length,
                separatorBuilder: (_, __) => const Divider(),
                itemBuilder: (context, index) {
                  final item = helpItems[index];
                  return _VoiceHelpCard(item: item);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// بطاقة مساعدة الأمر
class _VoiceHelpCard extends StatelessWidget {
  final VoiceHelpItem item;

  const _VoiceHelpCard({required this.item});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.record_voice_over, size: 20, color: Colors.green),
              const SizedBox(width: 8),
              Text(
                '"${item.command}"',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            item.description,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: item.examples.map((example) {
              return Chip(
                label: Text(
                  example,
                  style: const TextStyle(fontSize: 12),
                ),
                backgroundColor: Colors.grey.shade100,
                visualDensity: VisualDensity.compact,
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

/// Voice Status Indicator
class VoiceStatusIndicator extends ConsumerWidget {
  const VoiceStatusIndicator({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusAsync = ref.watch(voiceStatusProvider);

    return statusAsync.when(
      data: (status) => _buildIndicator(status),
      loading: () => const SizedBox.shrink(),
      error: (_, __) => _buildIndicator(VoiceStatus.error),
    );
  }

  Widget _buildIndicator(VoiceStatus status) {
    if (status == VoiceStatus.idle || status == VoiceStatus.ready) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: _getColor(status),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (status == VoiceStatus.listening)
            const _PulsingDot(color: Colors.white)
          else
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: const AlwaysStoppedAnimation(Colors.white),
              ),
            ),
          const SizedBox(width: 8),
          Text(
            _getText(status),
            style: const TextStyle(color: Colors.white),
          ),
        ],
      ),
    );
  }

  Color _getColor(VoiceStatus status) {
    return switch (status) {
      VoiceStatus.listening => Colors.red,
      VoiceStatus.processing => Colors.blue,
      VoiceStatus.error => Colors.orange,
      _ => Colors.grey,
    };
  }

  String _getText(VoiceStatus status) {
    return switch (status) {
      VoiceStatus.listening => 'جاري الاستماع...',
      VoiceStatus.processing => 'جاري المعالجة...',
      VoiceStatus.error => 'خطأ في الميكروفون',
      _ => '',
    };
  }
}

/// نقطة نابضة
class _PulsingDot extends StatefulWidget {
  final Color color;

  const _PulsingDot({required this.color});

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
      duration: const Duration(milliseconds: 500),
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
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: widget.color.withOpacity(0.5 + _controller.value * 0.5),
          ),
        );
      },
    );
  }
}
