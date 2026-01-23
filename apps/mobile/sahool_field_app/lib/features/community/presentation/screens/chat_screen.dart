// Sahool Community Chat Screen
// شاشة الدردشة لمجتمع سهول

import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
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
  final ImagePicker _imagePicker = ImagePicker();

  StreamSubscription? _messageSubscription;
  StreamSubscription? _typingSubscription;
  StreamSubscription? _expertJoinedSubscription;

  bool _isTyping = false;
  String? _typingUser;
  bool _expertJoined = false;
  File? _selectedImage;

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
        _isTyping = data['isTyping'] ?? false;
        _typingUser = data['userName'];
      });
    });

    // Listen for expert joining
    _expertJoinedSubscription = chatRepo.expertJoinedStream.listen((data) {
      setState(() {
        _expertJoined = true;
      });
      _showExpertJoinedSnackbar(data['expertName'] ?? 'خبير');
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

  /// Show attachment options bottom sheet
  /// عرض خيارات المرفقات
  void _showAttachmentOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const CircleAvatar(
                backgroundColor: Color(0xFF16A34A),
                child: Icon(Icons.camera_alt, color: Colors.white),
              ),
              title: const Text('التقاط صورة'),
              subtitle: const Text('فتح الكاميرا'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const CircleAvatar(
                backgroundColor: Color(0xFF2563EB),
                child: Icon(Icons.photo_library, color: Colors.white),
              ),
              title: const Text('اختيار من المعرض'),
              subtitle: const Text('صورة من الجهاز'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  /// Pick image from camera or gallery
  /// اختيار صورة من الكاميرا أو المعرض
  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? pickedFile = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        setState(() {
          _selectedImage = File(pickedFile.path);
        });

        // Show preview and send option
        if (mounted) {
          _showImagePreview();
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ في اختيار الصورة: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Show image preview before sending
  /// عرض معاينة الصورة قبل الإرسال
  void _showImagePreview() {
    if (_selectedImage == null) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('معاينة الصورة', textDirection: TextDirection.rtl),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.file(
                _selectedImage!,
                height: 200,
                fit: BoxFit.cover,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'هل تريد إرسال هذه الصورة؟',
              textDirection: TextDirection.rtl,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() => _selectedImage = null);
            },
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _sendImageMessage();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF16A34A),
            ),
            child: const Text('إرسال', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  /// Send image message
  /// إرسال رسالة صورة
  void _sendImageMessage() {
    if (_selectedImage == null) return;

    // Add image message to chat
    final imageMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      roomId: widget.roomId,
      author: widget.userName,
      authorType: 'farmer',
      message: '📷 صورة مرفقة',
      timestamp: DateTime.now(),
      attachmentUrl: _selectedImage!.path,
      attachmentType: 'image',
    );

    setState(() {
      _messages.add(imageMessage);
      _selectedImage = null;
    });

    _scrollToBottom();

    // Show success message
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم إرسال الصورة'),
        backgroundColor: Color(0xFF16A34A),
        duration: Duration(seconds: 1),
      ),
    );

    // Mock expert response for image
    if (_expertJoined) {
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          _addMockExpertMessage('شكراً على الصورة. دعني أفحصها وأعطيك رأيي خلال لحظات...');
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
                final message = _messages[index];
                return _buildMessageBubble(message);
              },
              // Use message.id as key for proper diffing during list updates
              findChildIndexCallback: (key) {
                final messageKey = key as ValueKey<String>;
                final index = _messages.indexWhere((m) => m.id == messageKey.value);
                return index >= 0 ? index : null;
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
                  IconButton(
                    icon: const Icon(Icons.attach_file),
                    color: Colors.grey[600],
                    onPressed: _showAttachmentOptions,
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
        key: ValueKey<String>(message.id),
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
      key: ValueKey<String>(message.id),
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
}
