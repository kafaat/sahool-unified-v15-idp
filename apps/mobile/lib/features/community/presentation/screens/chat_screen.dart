// Sahool Community Chat Screen
// شاشة الدردشة لمجتمع سهول

import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../data/models/chat_models.dart';
import '../../data/repositories/chat_repository.dart';

/// شاشة الدردشة مع الخبراء
class ChatScreen extends ConsumerStatefulWidget {
  final String userName;
  final String userNameAr;
  final String roomId;
  final String? topic;

  const ChatScreen({
    super.key,
    required this.userName,
    this.userNameAr = '',
    required this.roomId,
    this.topic,
  });

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];

  StreamSubscription? _messageSubscription;
  StreamSubscription? _typingSubscription;
  StreamSubscription? _expertJoinedSubscription;

  bool _isTyping = false;
  String? _typingUser;
  bool _expertJoined = false;

  // Attachment picker state
  // حالة منتقي المرفقات
  final ImagePicker _imagePicker = ImagePicker();
  bool _isCapturingImage = false;

  /// Maximum file size: 10 MB
  /// الحد الأقصى لحجم الملف: 10 ميجابايت
  static const int _maxFileSizeBytes = 10 * 1024 * 1024;

  @override
  void initState() {
    super.initState();
    _initializeChat();
  }

  void _initializeChat() {
    final chatRepo = ref.read(chatRepositoryProvider);

    // Connect and join room
    chatRepo.connect(
      userId: 'user_${DateTime.now().millisecondsSinceEpoch}',
      userName: widget.userName,
      userType: 'farmer',
    );

    chatRepo.joinRoom(
      roomId: widget.roomId,
      userName: widget.userName,
      userType: 'farmer',
    );

    // Listen for messages
    _messageSubscription = chatRepo.messageStream.listen((message) {
      setState(() {
        _messages.add(message);
      });
      _scrollToBottom();
    });

    // Listen for typing indicators
    _typingSubscription = chatRepo.typingStream.listen((data) {
      setState(() {
        _isTyping = (data['isTyping'] ?? false) as bool;
        _typingUser = data['userName'] as String?;
      });
    });

    // Listen for expert joining
    _expertJoinedSubscription = chatRepo.expertJoinedStream.listen((data) {
      setState(() {
        _expertJoined = true;
      });
      _showExpertJoinedSnackbar((data['expertName'] ?? 'خبير') as String);
    });

    // Add welcome message
    _addSystemMessage('مرحباً بك في محادثة الخبراء. سيتم توصيلك بخبير زراعي قريباً...');

    // Mock: Simulate expert joining after 2 seconds
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() => _expertJoined = true);
        _addSystemMessage('انضم المهندس سالم للمحادثة');
        _addMockExpertMessage('أهلاً بك، كيف يمكنني مساعدتك اليوم؟');
      }
    });
  }

  void _addSystemMessage(String text) {
    final message = ChatMessage(
      id: 'system_${DateTime.now().millisecondsSinceEpoch}',
      roomId: widget.roomId,
      author: 'النظام',
      authorType: 'system',
      message: text,
      timestamp: DateTime.now(),
    );
    setState(() => _messages.add(message));
    _scrollToBottom();
  }

  void _addMockExpertMessage(String text) {
    final message = ChatMessage(
      id: 'expert_${DateTime.now().millisecondsSinceEpoch}',
      roomId: widget.roomId,
      author: 'المهندس سالم',
      authorType: 'expert',
      message: text,
      timestamp: DateTime.now(),
    );
    setState(() => _messages.add(message));
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _showExpertJoinedSnackbar(String expertName) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$expertName انضم للمحادثة'),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _sendMessage() {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    final chatRepo = ref.read(chatRepositoryProvider);
    chatRepo.sendMessage(
      roomId: widget.roomId,
      author: widget.userName,
      authorType: 'farmer',
      message: text,
    );

    _messageController.clear();

    // Mock: Simulate expert response
    if (_expertJoined) {
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          _addMockExpertMessage(_getMockExpertResponse(text));
        }
      });
    }
  }

  String _getMockExpertResponse(String userMessage) {
    final lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.contains('مرض') || lowerMessage.contains('آفة') || lowerMessage.contains('مشكلة')) {
      return 'هل يمكنك إرسال صورة للنبات المصاب؟ سيساعدني ذلك في تشخيص المشكلة بدقة أكبر.';
    } else if (lowerMessage.contains('سقي') || lowerMessage.contains('ري') || lowerMessage.contains('ماء')) {
      return 'ما هو نوع المحصول وما هي طريقة الري المستخدمة حالياً؟';
    } else if (lowerMessage.contains('سماد') || lowerMessage.contains('تسميد')) {
      return 'يعتمد التسميد على نوع التربة والمحصول. ما هو المحصول المزروع ومرحلة النمو الحالية؟';
    } else if (lowerMessage.contains('شكر')) {
      return 'عفواً! لا تتردد في التواصل معنا في أي وقت. نتمنى لك موسماً زراعياً موفقاً 🌱';
    } else {
      return 'حسناً، دعني أفهم مشكلتك بشكل أفضل. هل يمكنك تزويدي بمزيد من التفاصيل؟';
    }
  }

  @override
  void dispose() {
    _messageSubscription?.cancel();
    _typingSubscription?.cancel();
    _expertJoinedSubscription?.cancel();
    _messageController.dispose();
    _scrollController.dispose();
    ref.read(chatRepositoryProvider).leaveRoom(
      roomId: widget.roomId,
      userName: widget.userName,
    );
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('محادثة الخبراء'),
            if (_expertJoined)
              const Text(
                'متصل مع المهندس سالم',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
              ),
          ],
        ),
        backgroundColor: const Color(0xFF16A34A),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () => _showInfoDialog(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Topic banner if provided
          if (widget.topic != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: const Color(0xFF16A34A).withOpacity(0.1),
              child: Row(
                children: [
                  const Icon(Icons.topic, size: 18, color: Color(0xFF16A34A)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      widget.topic!,
                      style: const TextStyle(
                        color: Color(0xFF16A34A),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // Messages list
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return _buildMessageBubble(_messages[index]);
              },
            ),
          ),

          // Typing indicator
          if (_isTyping && _typingUser != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                children: [
                  Text(
                    '$_typingUser يكتب...',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),

          // Input field
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -5),
                ),
              ],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  // Attachment button
                  // زر إرفاق الملفات
                  IconButton(
                    icon: const Icon(Icons.attach_file),
                    color: Colors.grey[600],
                    onPressed: _showAttachmentPicker,
                  ),

                  // Text input
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      textDirection: TextDirection.rtl,
                      decoration: InputDecoration(
                        hintText: 'اكتب رسالتك هنا...',
                        hintTextDirection: TextDirection.rtl,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(25),
                          borderSide: BorderSide.none,
                        ),
                        filled: true,
                        fillColor: Colors.grey[100],
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 10,
                        ),
                      ),
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),

                  const SizedBox(width: 8),

                  // Send button
                  CircleAvatar(
                    radius: 24,
                    backgroundColor: const Color(0xFF16A34A),
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white, size: 20),
                      onPressed: _sendMessage,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    final isMe = message.authorType == 'farmer';
    final isSystem = message.authorType == 'system';

    if (isSystem) {
      return Center(
        child: Container(
          margin: const EdgeInsets.symmetric(vertical: 8),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            message.message,
            style: TextStyle(
              color: Colors.grey[700],
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    return Align(
      alignment: isMe ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        child: Column(
          crossAxisAlignment: isMe ? CrossAxisAlignment.start : CrossAxisAlignment.end,
          children: [
            // Author name (for experts)
            if (!isMe)
              Padding(
                padding: const EdgeInsets.only(bottom: 4, right: 8),
                child: Text(
                  message.author,
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),

            // Message bubble
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: isMe ? const Color(0xFF16A34A) : Colors.grey[200],
                borderRadius: BorderRadius.circular(20).copyWith(
                  bottomLeft: isMe ? Radius.zero : null,
                  bottomRight: !isMe ? Radius.zero : null,
                ),
              ),
              child: Text(
                message.message,
                style: TextStyle(
                  color: isMe ? Colors.white : Colors.black87,
                  fontSize: 15,
                ),
                textDirection: TextDirection.rtl,
              ),
            ),

            // Timestamp
            Padding(
              padding: const EdgeInsets.only(top: 2, left: 8, right: 8),
              child: Text(
                _formatTime(message.timestamp),
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.grey[500],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  void _showInfoDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('معلومات المحادثة'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoRow('رقم الغرفة', widget.roomId.split('_').last),
            const SizedBox(height: 8),
            _buildInfoRow('الموضوع', widget.topic ?? 'استشارة عامة'),
            const SizedBox(height: 8),
            _buildInfoRow('الحالة', _expertJoined ? 'متصل بخبير' : 'في انتظار خبير'),
            const SizedBox(height: 8),
            _buildInfoRow('عدد الرسائل', _messages.length.toString()),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إغلاق'),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
      ],
    );
  }

  // ========== Attachment Picker Methods ==========
  // ========== طرق منتقي المرفقات ==========

  /// Show attachment picker bottom sheet
  /// عرض قائمة خيارات المرفقات
  void _showAttachmentPicker() {
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
              'إرفاق ملف',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 20),

            // Attachment options grid
            GridView.count(
              shrinkWrap: true,
              crossAxisCount: 3,
              mainAxisSpacing: 16,
              crossAxisSpacing: 16,
              children: [
                _buildAttachmentOption(
                  icon: Icons.image,
                  label: 'صورة من المعرض',
                  color: Colors.blue,
                  onTap: () {
                    Navigator.pop(context);
                    _pickImageFromGallery();
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.camera_alt,
                  label: 'التقاط صورة',
                  color: Colors.purple,
                  onTap: () {
                    Navigator.pop(context);
                    _captureFromCamera();
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.insert_drive_file,
                  label: 'ملف مستند',
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

  /// Build a single attachment option widget
  /// بناء عنصر خيار مرفق واحد
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
              fontSize: 11,
              color: Colors.grey[700],
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  /// Pick image from gallery
  /// اختيار صورة من المعرض
  Future<void> _pickImageFromGallery() async {
    if (_isCapturingImage) return;

    setState(() {
      _isCapturingImage = true;
    });

    try {
      // Request photos permission on iOS
      if (Platform.isIOS) {
        final status = await Permission.photos.request();
        if (!status.isGranted && !status.isLimited) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('يرجى السماح بالوصول إلى الصور من الإعدادات'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }
      }

      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
        maxWidth: 1920,
        maxHeight: 1080,
      );

      if (image != null && mounted) {
        _sendAttachmentMessage(image.path, _getFileNameFromPath(image.path));
      }
    } catch (e) {
      if (mounted) {
        final errorMessage = e.toString().contains('photo_access_denied') ||
                e.toString().contains('permission')
            ? 'يرجى السماح بالوصول إلى الصور من الإعدادات'
            : 'حدث خطأ أثناء اختيار الصورة';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
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
      // Request camera permission
      final cameraStatus = await Permission.camera.request();
      if (!cameraStatus.isGranted) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('يرجى السماح بالوصول إلى الكاميرا من الإعدادات'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }

      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85,
        maxWidth: 1920,
        maxHeight: 1080,
      );

      if (image != null && mounted) {
        _sendAttachmentMessage(image.path, _getFileNameFromPath(image.path));
      }
    } catch (e) {
      if (mounted) {
        final errorMessage = e.toString().contains('camera_access_denied') ||
                e.toString().contains('permission')
            ? 'يرجى السماح بالوصول إلى الكاميرا من الإعدادات'
            : 'حدث خطأ أثناء التقاط الصورة';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
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

  /// Pick document file
  /// اختيار ملف مستند
  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv', 'jpg', 'jpeg', 'png'],
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

        _sendAttachmentMessage(filePath, fileName);
      }
    } catch (e) {
      if (mounted) {
        final errorMessage = e.toString().contains('permission')
            ? 'يرجى السماح بالوصول إلى الملفات من الإعدادات'
            : 'حدث خطأ أثناء اختيار الملف';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Extract file name from path
  /// استخراج اسم الملف من المسار
  String _getFileNameFromPath(String path) {
    return path.split('/').last;
  }

  /// Send message with attachment
  /// إرسال رسالة مع مرفق
  void _sendAttachmentMessage(String filePath, String fileName) {
    final chatRepo = ref.read(chatRepositoryProvider);

    // Send message with attachment
    chatRepo.sendMessage(
      roomId: widget.roomId,
      author: widget.userName,
      authorType: 'farmer',
      message: 'مرفق: $fileName',
      attachments: [filePath],
    );

    // Mock: Simulate expert response for image attachments
    if (_expertJoined && _isImageFile(fileName)) {
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          _addMockExpertMessage('شكراً لإرسال الصورة. سأقوم بفحصها وأرد عليك في أقرب وقت.');
        }
      });
    }
  }

  /// Check if file is an image
  /// التحقق مما إذا كان الملف صورة
  bool _isImageFile(String fileName) {
    final extension = fileName.toLowerCase().split('.').last;
    return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'heic'].contains(extension);
  }
}
