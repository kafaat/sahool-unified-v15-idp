/// Chat Input Widget
/// حقل إدخال الرسائل
///
/// Features:
/// - Text input field
/// - Send button
/// - Typing indicator
/// - Attachment options (future)

import 'dart:async';
import 'package:flutter/material.dart';
import '../../../core/config/theme.dart';

class ChatInput extends StatefulWidget {
  final Function(String message) onSendMessage;
  final Function(bool isTyping) onTypingChanged;
  final String? hint;

  const ChatInput({
    super.key,
    required this.onSendMessage,
    required this.onTypingChanged,
    this.hint,
  });

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  bool _isTyping = false;
  Timer? _typingTimer;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _controller.removeListener(_onTextChanged);
    _controller.dispose();
    _focusNode.dispose();
    _typingTimer?.cancel();
    super.dispose();
  }

  void _onTextChanged() {
    final hasText = _controller.text.trim().isNotEmpty;

    // Send typing indicator
    if (hasText && !_isTyping) {
      _isTyping = true;
      widget.onTypingChanged(true);
    }

    // Cancel previous timer
    _typingTimer?.cancel();

    // Set new timer to stop typing after 2 seconds of inactivity
    if (hasText) {
      _typingTimer = Timer(const Duration(seconds: 2), () {
        if (_isTyping) {
          _isTyping = false;
          widget.onTypingChanged(false);
        }
      });
    } else {
      if (_isTyping) {
        _isTyping = false;
        widget.onTypingChanged(false);
      }
    }
  }

  void _handleSend() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    widget.onSendMessage(text);
    _controller.clear();

    // Stop typing indicator
    if (_isTyping) {
      _isTyping = false;
      widget.onTypingChanged(false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // Attachment button (future feature)
            IconButton(
              onPressed: () {
                // TODO: Implement attachment picker
                _showAttachmentOptions(context);
              },
              icon: Icon(
                Icons.add_circle_outline,
                color: SahoolTheme.primary,
              ),
              tooltip: 'إرفاق',
            ),

            // Text input
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(24),
                ),
                child: TextField(
                  controller: _controller,
                  focusNode: _focusNode,
                  textInputAction: TextInputAction.send,
                  onSubmitted: (_) => _handleSend(),
                  maxLines: null,
                  textAlignVertical: TextAlignVertical.center,
                  decoration: InputDecoration(
                    hintText: widget.hint ?? 'اكتب رسالة...',
                    hintStyle: TextStyle(
                      color: Colors.grey[500],
                      fontSize: 15,
                    ),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 10,
                    ),
                  ),
                  style: const TextStyle(
                    fontSize: 15,
                    height: 1.4,
                  ),
                ),
              ),
            ),

            const SizedBox(width: 4),

            // Send button
            ValueListenableBuilder<TextEditingValue>(
              valueListenable: _controller,
              builder: (context, value, child) {
                final hasText = value.text.trim().isNotEmpty;

                return AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  child: hasText
                      ? IconButton(
                          onPressed: _handleSend,
                          icon: Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: SahoolTheme.primary,
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.send,
                              color: Colors.white,
                              size: 20,
                            ),
                          ),
                          tooltip: 'إرسال',
                        )
                      : IconButton(
                          onPressed: () {
                            // TODO: Implement voice message
                          },
                          icon: Icon(
                            Icons.mic,
                            color: SahoolTheme.primary,
                          ),
                          tooltip: 'رسالة صوتية',
                        ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showAttachmentOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Handle bar
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(bottom: 20),
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Title
            const Text(
              'إرفاق',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 20),

            // Options
            GridView.count(
              shrinkWrap: true,
              crossAxisCount: 3,
              mainAxisSpacing: 16,
              crossAxisSpacing: 16,
              children: [
                _buildAttachmentOption(
                  icon: Icons.image,
                  label: 'صورة',
                  color: Colors.blue,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Implement image picker
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.camera_alt,
                  label: 'كاميرا',
                  color: Colors.purple,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Implement camera
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.location_on,
                  label: 'موقع',
                  color: Colors.red,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Implement location picker
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.shopping_bag,
                  label: 'منتج',
                  color: SahoolTheme.primary,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Implement product picker
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.receipt_long,
                  label: 'طلب',
                  color: Colors.orange,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Implement order picker
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.insert_drive_file,
                  label: 'ملف',
                  color: Colors.teal,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Implement file picker
                  },
                ),
              ],
            ),

            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildAttachmentOption({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: color,
              size: 28,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[700],
            ),
          ),
        ],
      ),
    );
  }
}
