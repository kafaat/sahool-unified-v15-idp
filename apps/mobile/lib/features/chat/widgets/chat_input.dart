/// Chat Input Widget
/// حقل إدخال الرسائل
///
/// Features:
/// - Text input field
/// - Send button
/// - Typing indicator
/// - Attachment options (future)

import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import '../../../core/config/theme.dart';
import 'location_picker.dart';

class ChatInput extends StatefulWidget {
  final Function(String message) onSendMessage;
  final Function(bool isTyping) onTypingChanged;
  final Function(String imagePath)? onImageCaptured;
  final Function(String filePath, String fileName, int fileSize)? onFileSelected;
  final Function(String audioPath, Duration duration)? onVoiceMessageRecorded;
  final Function(double latitude, double longitude)? onLocationSelected;
  final String? hint;

  const ChatInput({
    super.key,
    required this.onSendMessage,
    required this.onTypingChanged,
    this.onImageCaptured,
    this.onFileSelected,
    this.onVoiceMessageRecorded,
    this.onLocationSelected,
    this.hint,
  });

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  final ImagePicker _imagePicker = ImagePicker();
  bool _isTyping = false;
  Timer? _typingTimer;
  bool _isCapturingImage = false;

  // Voice recording state
  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  Duration _recordDuration = Duration.zero;
  Timer? _recordTimer;
  String? _recordingPath;

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
    _recordTimer?.cancel();
    _audioRecorder.dispose();
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

  /// Start voice recording
  /// بدء تسجيل الرسالة الصوتية
  Future<void> _startRecording() async {
    try {
      // Check and request microphone permission
      final status = await Permission.microphone.request();
      if (!status.isGranted) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('يرجى السماح بالوصول إلى الميكروفون من الإعدادات'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }

      // Check if recorder is available
      if (!await _audioRecorder.hasPermission()) {
        return;
      }

      // Generate unique file path for recording
      final directory = await getTemporaryDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      _recordingPath = '${directory.path}/voice_message_$timestamp.m4a';

      // Configure recording settings (AAC format for better compatibility)
      const config = RecordConfig(
        encoder: AudioEncoder.aacLc,
        bitRate: 128000,
        sampleRate: 44100,
      );

      // Start recording
      await _audioRecorder.start(config, path: _recordingPath!);

      setState(() {
        _isRecording = true;
        _recordDuration = Duration.zero;
      });

      // Start duration timer
      _recordTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
        if (mounted) {
          setState(() {
            _recordDuration = Duration(seconds: timer.tick);
          });
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('حدث خطأ أثناء بدء التسجيل'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Stop recording and send voice message
  /// إيقاف التسجيل وإرسال الرسالة الصوتية
  Future<void> _stopRecordingAndSend() async {
    if (!_isRecording) return;

    try {
      _recordTimer?.cancel();
      _recordTimer = null;

      final path = await _audioRecorder.stop();

      if (path != null && _recordDuration.inSeconds >= 1) {
        // Only send if recording is at least 1 second
        widget.onVoiceMessageRecorded?.call(path, _recordDuration);
      } else if (path != null) {
        // Delete short recordings
        final file = File(path);
        if (await file.exists()) {
          await file.delete();
        }
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('الرسالة الصوتية قصيرة جداً'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('حدث خطأ أثناء إيقاف التسجيل'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isRecording = false;
        _recordDuration = Duration.zero;
        _recordingPath = null;
      });
    }
  }

  /// Cancel recording and discard
  /// إلغاء التسجيل وحذفه
  Future<void> _cancelRecording() async {
    if (!_isRecording) return;

    try {
      _recordTimer?.cancel();
      _recordTimer = null;

      final path = await _audioRecorder.stop();

      // Delete the recording file
      if (path != null) {
        final file = File(path);
        if (await file.exists()) {
          await file.delete();
        }
      }
    } catch (e) {
      // Silently fail on cancel
    } finally {
      setState(() {
        _isRecording = false;
        _recordDuration = Duration.zero;
        _recordingPath = null;
      });
    }
  }

  /// Format duration as mm:ss
  /// تنسيق المدة بالدقائق والثواني
  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  /// Pick image from gallery
  /// اختيار صورة من المعرض
  Future<void> _pickImageFromGallery() async {
    if (_isCapturingImage) return;

    setState(() {
      _isCapturingImage = true;
    });

    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
        maxWidth: 1920,
        maxHeight: 1080,
      );

      if (image != null && mounted) {
        widget.onImageCaptured?.call(image.path);
      }
    } catch (e) {
      if (mounted) {
        // Show error message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              e.toString().contains('photo_access_denied')
                  ? 'يرجى السماح بالوصول إلى الصور من الإعدادات'
                  : 'حدث خطأ أثناء اختيار الصورة',
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isCapturingImage = false;
        });
      }
    }
  }

  /// Capture photo from camera
  /// التقاط صورة من الكاميرا
  Future<void> _captureFromCamera() async {
    if (_isCapturingImage) return;

    setState(() {
      _isCapturingImage = true;
    });

    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85,
        maxWidth: 1920,
        maxHeight: 1080,
      );

      if (image != null && mounted) {
        widget.onImageCaptured?.call(image.path);
      }
    } catch (e) {
      if (mounted) {
        // Show error message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              e.toString().contains('camera_access_denied')
                  ? 'يرجى السماح بالوصول إلى الكاميرا من الإعدادات'
                  : 'حدث خطأ أثناء التقاط الصورة',
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isCapturingImage = false;
        });
      }
    }
  }

  /// Maximum file size: 10 MB
  /// الحد الأقصى لحجم الملف: 10 ميجابايت
  static const int _maxFileSizeBytes = 10 * 1024 * 1024;

  /// Pick file from device
  /// اختيار ملف من الجهاز
  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'],
        withData: false,
        withReadStream: false,
      );

      if (result != null && result.files.isNotEmpty && mounted) {
        final file = result.files.first;
        final filePath = file.path;
        final fileName = file.name;
        final fileSize = file.size;

        // Validate file path
        if (filePath == null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('لا يمكن الوصول إلى الملف'),
              backgroundColor: Colors.red,
            ),
          );
          return;
        }

        // Check file size limit
        if (fileSize > _maxFileSizeBytes) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('حجم الملف يتجاوز الحد الأقصى (10 ميجابايت)'),
              backgroundColor: Colors.red,
            ),
          );
          return;
        }

        // Call the callback with file details
        widget.onFileSelected?.call(filePath, fileName, fileSize);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              e.toString().contains('permission')
                  ? 'يرجى السماح بالوصول إلى الملفات من الإعدادات'
                  : 'حدث خطأ أثناء اختيار الملف',
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Pick location using location picker screen
  /// اختيار الموقع باستخدام شاشة اختيار الموقع
  Future<void> _pickLocation() async {
    try {
      final LocationData? locationData = await Navigator.push<LocationData>(
        context,
        MaterialPageRoute(
          builder: (context) => const LocationPickerScreen(),
        ),
      );

      if (locationData != null && mounted) {
        widget.onLocationSelected?.call(
          locationData.latitude,
          locationData.longitude,
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('حدث خطأ أثناء اختيار الموقع'),
            backgroundColor: Colors.red,
          ),
        );
      }
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
        child: _isRecording ? _buildRecordingIndicator() : _buildInputRow(),
      ),
    );
  }

  /// Build the normal text input row
  /// بناء صف إدخال النص العادي
  Widget _buildInputRow() {
    return Row(
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
                      onPressed: _startRecording,
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
    );
  }

  /// Build the recording indicator UI
  /// بناء واجهة مؤشر التسجيل
  Widget _buildRecordingIndicator() {
    return Row(
      children: [
        // Cancel button
        IconButton(
          onPressed: _cancelRecording,
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.red.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.delete_outline,
              color: Colors.red,
              size: 20,
            ),
          ),
          tooltip: 'إلغاء',
        ),

        // Recording indicator with duration
        Expanded(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.red.withOpacity(0.05),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Animated recording dot
                TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.5, end: 1.0),
                  duration: const Duration(milliseconds: 500),
                  builder: (context, value, child) {
                    return Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(value),
                        shape: BoxShape.circle,
                      ),
                    );
                  },
                  onEnd: () {
                    // Loop animation by rebuilding
                    if (_isRecording && mounted) {
                      setState(() {});
                    }
                  },
                ),
                const SizedBox(width: 12),
                // Duration text
                Text(
                  _formatDuration(_recordDuration),
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: Colors.red,
                  ),
                ),
                const SizedBox(width: 12),
                // Recording label
                Text(
                  'جاري التسجيل...',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(width: 4),

        // Send button
        IconButton(
          onPressed: _stopRecordingAndSend,
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
        ),
      ],
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
                    _pickImageFromGallery();
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.camera_alt,
                  label: 'كاميرا',
                  color: Colors.purple,
                  onTap: () {
                    Navigator.pop(context);
                    _captureFromCamera();
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.location_on,
                  label: 'موقع',
                  color: Colors.red,
                  onTap: () {
                    Navigator.pop(context);
                    _pickLocation();
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
                    _pickFile();
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
