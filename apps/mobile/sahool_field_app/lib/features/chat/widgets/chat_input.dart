/// Chat Input Widget
/// حقل إدخال الرسائل
///
/// Features:
/// - Text input field with send button
/// - Voice recording with duration indicator
/// - Typing indicator
/// - Attachment options:
///   - Image picker (gallery/camera)
///   - File picker (documents)
///   - Location picker
///   - Product picker (marketplace)
///   - Order picker (user orders)
library;

import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import '../../../core/config/theme.dart';
import '../../marketplace/marketplace_provider.dart';
import 'location_picker.dart';

class ChatInput extends StatefulWidget {
  final Function(String message) onSendMessage;
  final Function(bool isTyping) onTypingChanged;
  final Function(String imagePath)? onImageCaptured;
  final Function(String filePath, String fileName, int fileSize)?
      onFileSelected;
  final Function(String audioPath, Duration duration)? onVoiceMessageRecorded;
  final Function(double latitude, double longitude)? onLocationSelected;
  final Function(Product product)? onProductSelected;
  final Function(Order order)? onOrderSelected;
  final List<Product>? availableProducts;
  final List<Order>? userOrders;
  final String? hint;

  const ChatInput({
    super.key,
    required this.onSendMessage,
    required this.onTypingChanged,
    this.onImageCaptured,
    this.onFileSelected,
    this.onVoiceMessageRecorded,
    this.onLocationSelected,
    this.onProductSelected,
    this.onOrderSelected,
    this.availableProducts,
    this.userOrders,
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

  /// Show product picker bottom sheet
  /// عرض نافذة اختيار المنتج
  void _showProductPicker() {
    final products = widget.availableProducts ?? [];

    if (products.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('لا توجد منتجات متاحة للمشاركة'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => _ProductPickerSheet(
        products: products,
        onProductSelected: (product) {
          Navigator.pop(context);
          widget.onProductSelected?.call(product);
        },
      ),
    );
  }

  /// Show order picker bottom sheet
  /// عرض نافذة اختيار الطلب
  void _showOrderPicker() {
    final orders = widget.userOrders ?? [];

    if (orders.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('لا توجد طلبات للمشاركة'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => _OrderPickerSheet(
        orders: orders,
        onOrderSelected: (order) {
          Navigator.pop(context);
          widget.onOrderSelected?.call(order);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
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
        // Attachment button
        IconButton(
          onPressed: () {
            _showAttachmentOptions(context);
          },
          icon: const Icon(
            Icons.add_circle_outline,
            color: SahoolTheme.primary,
          ),
          tooltip: 'إرفاق',
        ),

        // Text input
        Expanded(
          child: DecoratedBox(
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
                        decoration: const BoxDecoration(
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
                      icon: const Icon(
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
              color: Colors.red.withValues(alpha: 0.1),
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
              color: Colors.red.withValues(alpha: 0.05),
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
                        color: Colors.red.withValues(alpha: value),
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
            decoration: const BoxDecoration(
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
                    _showProductPicker();
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.receipt_long,
                  label: 'طلب',
                  color: Colors.orange,
                  onTap: () {
                    Navigator.pop(context);
                    _showOrderPicker();
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
              color: color.withValues(alpha: 0.1),
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

/// Product Picker Bottom Sheet
/// نافذة اختيار المنتج
class _ProductPickerSheet extends StatefulWidget {
  final List<Product> products;
  final Function(Product) onProductSelected;

  const _ProductPickerSheet({
    required this.products,
    required this.onProductSelected,
  });

  @override
  State<_ProductPickerSheet> createState() => _ProductPickerSheetState();
}

class _ProductPickerSheetState extends State<_ProductPickerSheet> {
  final TextEditingController _searchController = TextEditingController();
  ProductCategory? _selectedCategory;
  List<Product> _filteredProducts = [];

  @override
  void initState() {
    super.initState();
    _filteredProducts = widget.products;
    _searchController.addListener(_filterProducts);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _filterProducts() {
    final query = _searchController.text.toLowerCase().trim();
    setState(() {
      _filteredProducts = widget.products.where((product) {
        // Filter by search query
        final matchesQuery = query.isEmpty ||
            product.name.toLowerCase().contains(query) ||
            product.nameAr.contains(query) ||
            (product.description?.toLowerCase().contains(query) ?? false) ||
            (product.descriptionAr?.contains(query) ?? false);

        // Filter by category
        final matchesCategory =
            _selectedCategory == null || product.category == _selectedCategory;

        return matchesQuery && matchesCategory;
      }).toList();
    });
  }

  void _selectCategory(ProductCategory? category) {
    setState(() {
      _selectedCategory = category;
    });
    _filterProducts();
  }

  /// Get icon for product category
  /// الحصول على أيقونة تصنيف المنتج
  IconData _getCategoryIcon(ProductCategory category) {
    switch (category) {
      case ProductCategory.harvest:
        return Icons.agriculture;
      case ProductCategory.seeds:
        return Icons.grass;
      case ProductCategory.fertilizer:
        return Icons.science;
      case ProductCategory.pesticide:
        return Icons.bug_report;
      case ProductCategory.equipment:
        return Icons.construction;
      case ProductCategory.irrigation:
        return Icons.water_drop;
      case ProductCategory.other:
        return Icons.inventory_2;
    }
  }

  /// Get Arabic name for category
  /// الحصول على الاسم العربي للتصنيف
  String _getCategoryNameAr(ProductCategory category) {
    switch (category) {
      case ProductCategory.harvest:
        return 'محاصيل';
      case ProductCategory.seeds:
        return 'بذور';
      case ProductCategory.fertilizer:
        return 'أسمدة';
      case ProductCategory.pesticide:
        return 'مبيدات';
      case ProductCategory.equipment:
        return 'معدات';
      case ProductCategory.irrigation:
        return 'ري';
      case ProductCategory.other:
        return 'أخرى';
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, scrollController) => DecoratedBox(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            // Handle bar
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(top: 12, bottom: 8),
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Title
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  Icon(Icons.shopping_bag, color: SahoolTheme.primary),
                  SizedBox(width: 8),
                  Text(
                    'اختر منتج للمشاركة',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),

            // Search field
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'البحث عن منتج...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _searchController.text.isNotEmpty
                      ? IconButton(
                          onPressed: () {
                            _searchController.clear();
                          },
                          icon: const Icon(Icons.clear),
                        )
                      : null,
                  filled: true,
                  fillColor: Colors.grey[100],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
              ),
            ),

            // Category filter chips
            SizedBox(
              height: 48,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 12),
                children: [
                  // All categories chip
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: FilterChip(
                      label: const Text('الكل'),
                      selected: _selectedCategory == null,
                      onSelected: (_) => _selectCategory(null),
                      selectedColor: SahoolTheme.primary.withValues(alpha: 0.2),
                      checkmarkColor: SahoolTheme.primary,
                    ),
                  ),
                  // Category chips
                  ...ProductCategory.values.map((category) => Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4),
                        child: FilterChip(
                          avatar: Icon(
                            _getCategoryIcon(category),
                            size: 18,
                            color: _selectedCategory == category
                                ? SahoolTheme.primary
                                : Colors.grey[600],
                          ),
                          label: Text(_getCategoryNameAr(category)),
                          selected: _selectedCategory == category,
                          onSelected: (_) => _selectCategory(category),
                          selectedColor: SahoolTheme.primary.withValues(alpha: 0.2),
                          checkmarkColor: SahoolTheme.primary,
                        ),
                      )),
                ],
              ),
            ),

            const SizedBox(height: 8),

            // Products list
            Expanded(
              child: _filteredProducts.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.search_off,
                            size: 64,
                            color: Colors.grey[400],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'لم يتم العثور على منتجات',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      controller: scrollController,
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: _filteredProducts.length,
                      itemBuilder: (context, index) {
                        final product = _filteredProducts[index];
                        return _ProductListTile(
                          product: product,
                          onTap: () => widget.onProductSelected(product),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Product List Tile Widget
/// عنصر قائمة المنتج
class _ProductListTile extends StatelessWidget {
  final Product product;
  final VoidCallback onTap;

  const _ProductListTile({
    required this.product,
    required this.onTap,
  });

  /// Get icon for product category
  IconData _getCategoryIcon(ProductCategory category) {
    switch (category) {
      case ProductCategory.harvest:
        return Icons.agriculture;
      case ProductCategory.seeds:
        return Icons.grass;
      case ProductCategory.fertilizer:
        return Icons.science;
      case ProductCategory.pesticide:
        return Icons.bug_report;
      case ProductCategory.equipment:
        return Icons.construction;
      case ProductCategory.irrigation:
        return Icons.water_drop;
      case ProductCategory.other:
        return Icons.inventory_2;
    }
  }

  /// Get color for product category
  Color _getCategoryColor(ProductCategory category) {
    switch (category) {
      case ProductCategory.harvest:
        return Colors.amber;
      case ProductCategory.seeds:
        return Colors.green;
      case ProductCategory.fertilizer:
        return Colors.blue;
      case ProductCategory.pesticide:
        return Colors.red;
      case ProductCategory.equipment:
        return Colors.brown;
      case ProductCategory.irrigation:
        return Colors.cyan;
      case ProductCategory.other:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final categoryColor = _getCategoryColor(product.category);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // Product image or category icon
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: categoryColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: product.imageUrl != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(
                          product.imageUrl!,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Icon(
                            _getCategoryIcon(product.category),
                            color: categoryColor,
                            size: 28,
                          ),
                        ),
                      )
                    : Icon(
                        _getCategoryIcon(product.category),
                        color: categoryColor,
                        size: 28,
                      ),
              ),

              const SizedBox(width: 12),

              // Product details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.nameAr,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      product.categoryNameAr,
                      style: TextStyle(
                        fontSize: 12,
                        color: categoryColor,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Text(
                          '${product.price.toStringAsFixed(0)} ريال',
                          style: const TextStyle(
                            fontSize: 13,
                            color: SahoolTheme.primary,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          ' / ${product.unitAr}',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                        const Spacer(),
                        if (product.stock > 0)
                          Text(
                            'متوفر: ${product.stock.toStringAsFixed(0)}',
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey[500],
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),

              // Selection indicator
              Icon(
                Icons.chevron_left,
                color: Colors.grey[400],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Order Picker Bottom Sheet
/// نافذة اختيار الطلب
class _OrderPickerSheet extends StatefulWidget {
  final List<Order> orders;
  final Function(Order) onOrderSelected;

  const _OrderPickerSheet({
    required this.orders,
    required this.onOrderSelected,
  });

  @override
  State<_OrderPickerSheet> createState() => _OrderPickerSheetState();
}

class _OrderPickerSheetState extends State<_OrderPickerSheet> {
  String? _selectedStatus;
  List<Order> _filteredOrders = [];

  @override
  void initState() {
    super.initState();
    _filteredOrders = widget.orders;
  }

  void _filterByStatus(String? status) {
    setState(() {
      _selectedStatus = status;
      if (status == null) {
        _filteredOrders = widget.orders;
      } else {
        _filteredOrders = widget.orders
            .where((order) => order.status.toUpperCase() == status)
            .toList();
      }
    });
  }

  /// Get color for order status
  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case 'PENDING':
        return Colors.orange;
      case 'CONFIRMED':
        return Colors.blue;
      case 'PROCESSING':
        return Colors.purple;
      case 'SHIPPED':
        return Colors.indigo;
      case 'DELIVERED':
        return Colors.green;
      case 'CANCELLED':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  /// Get icon for order status
  IconData _getStatusIcon(String status) {
    switch (status.toUpperCase()) {
      case 'PENDING':
        return Icons.hourglass_empty;
      case 'CONFIRMED':
        return Icons.check_circle_outline;
      case 'PROCESSING':
        return Icons.autorenew;
      case 'SHIPPED':
        return Icons.local_shipping;
      case 'DELIVERED':
        return Icons.done_all;
      case 'CANCELLED':
        return Icons.cancel_outlined;
      default:
        return Icons.help_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.6,
      minChildSize: 0.4,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) => DecoratedBox(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            // Handle bar
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(top: 12, bottom: 8),
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Title
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  Icon(Icons.receipt_long, color: Colors.orange),
                  SizedBox(width: 8),
                  Text(
                    'اختر طلب للمشاركة',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),

            // Status filter chips
            SizedBox(
              height: 48,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 12),
                children: [
                  // All orders chip
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: FilterChip(
                      label: const Text('الكل'),
                      selected: _selectedStatus == null,
                      onSelected: (_) => _filterByStatus(null),
                      selectedColor: Colors.orange.withValues(alpha: 0.2),
                      checkmarkColor: Colors.orange,
                    ),
                  ),
                  // Status filter chips
                  ...[
                    ('PENDING', 'قيد الانتظار'),
                    ('CONFIRMED', 'مؤكد'),
                    ('PROCESSING', 'جاري التجهيز'),
                    ('SHIPPED', 'تم الشحن'),
                    ('DELIVERED', 'تم التسليم'),
                  ].map((statusPair) => Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4),
                        child: FilterChip(
                          avatar: Icon(
                            _getStatusIcon(statusPair.$1),
                            size: 18,
                            color: _selectedStatus == statusPair.$1
                                ? _getStatusColor(statusPair.$1)
                                : Colors.grey[600],
                          ),
                          label: Text(statusPair.$2),
                          selected: _selectedStatus == statusPair.$1,
                          onSelected: (_) => _filterByStatus(statusPair.$1),
                          selectedColor:
                              _getStatusColor(statusPair.$1).withValues(alpha: 0.2),
                          checkmarkColor: _getStatusColor(statusPair.$1),
                        ),
                      )),
                ],
              ),
            ),

            const SizedBox(height: 8),

            // Orders list
            Expanded(
              child: _filteredOrders.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.receipt_long_outlined,
                            size: 64,
                            color: Colors.grey[400],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'لم يتم العثور على طلبات',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      controller: scrollController,
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: _filteredOrders.length,
                      itemBuilder: (context, index) {
                        final order = _filteredOrders[index];
                        return _OrderListTile(
                          order: order,
                          statusColor: _getStatusColor(order.status),
                          statusIcon: _getStatusIcon(order.status),
                          onTap: () => widget.onOrderSelected(order),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Order List Tile Widget
/// عنصر قائمة الطلب
class _OrderListTile extends StatelessWidget {
  final Order order;
  final Color statusColor;
  final IconData statusIcon;
  final VoidCallback onTap;

  const _OrderListTile({
    required this.order,
    required this.statusColor,
    required this.statusIcon,
    required this.onTap,
  });

  /// Format date in Arabic style
  String _formatDate(DateTime date) {
    final months = [
      'يناير',
      'فبراير',
      'مارس',
      'أبريل',
      'مايو',
      'يونيو',
      'يوليو',
      'أغسطس',
      'سبتمبر',
      'أكتوبر',
      'نوفمبر',
      'ديسمبر',
    ];
    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // Order status icon
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  statusIcon,
                  color: statusColor,
                  size: 24,
                ),
              ),

              const SizedBox(width: 12),

              // Order details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          'طلب #${order.orderNumber}',
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: statusColor.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            order.statusAr,
                            style: TextStyle(
                              fontSize: 11,
                              color: statusColor,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        Icon(
                          Icons.calendar_today,
                          size: 14,
                          color: Colors.grey[500],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _formatDate(order.createdAt),
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                        const Spacer(),
                        Text(
                          '${order.totalAmount.toStringAsFixed(0)} ريال',
                          style: const TextStyle(
                            fontSize: 14,
                            color: SahoolTheme.primary,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(width: 8),

              // Selection indicator
              Icon(
                Icons.chevron_left,
                color: Colors.grey[400],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
