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

// ---------------------------------------------------------------------------
// State & Notifier
// حالة الدردشة ومدير الحالة
// ---------------------------------------------------------------------------

/// Immutable chat state managed by [ChatNotifier].
/// حالة الدردشة غير القابلة للتعديل يديرها [ChatNotifier].
class ChatState {
  final List<ChatMessage> messages;
  final bool expertJoined;
  final bool isTyping;
  final String? typingUser;
  final bool isLoading;

  const ChatState({
    this.messages = const [],
    this.expertJoined = false,
    this.isTyping = false,
    this.typingUser,
    this.isLoading = false,
  });

  ChatState copyWith({
    List<ChatMessage>? messages,
    bool? expertJoined,
    bool? isTyping,
    String? typingUser,
    bool? isLoading,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      expertJoined: expertJoined ?? this.expertJoined,
      isTyping: isTyping ?? this.isTyping,
      typingUser: typingUser ?? this.typingUser,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

/// Manages chat state via Riverpod [StateNotifier].
/// يدير حالة الدردشة عبر [StateNotifier] من Riverpod.
class ChatNotifier extends StateNotifier<ChatState> {
  final ChatRepository _chatRepo;
  final String roomId;
  final String userName;

  StreamSubscription? _messageSubscription;
  StreamSubscription? _typingSubscription;
  StreamSubscription? _expertJoinedSubscription;

  ChatNotifier({
    required ChatRepository chatRepo,
    required this.roomId,
    required this.userName,
  })  : _chatRepo = chatRepo,
        super(const ChatState());

  /// Initialize chat connection and stream listeners.
  /// تهيئة اتصال الدردشة ومستمعي التدفق.
  void initialize() {
    _chatRepo.connect(
      userId: 'user_${DateTime.now().millisecondsSinceEpoch}',
      userName: userName,
      userType: 'farmer',
    );

    _chatRepo.joinRoom(
      roomId: roomId,
      userName: userName,
      userType: 'farmer',
    );

    // Listen for incoming messages from WebSocket / repository
    // الاستماع للرسائل الواردة من WebSocket / المستودع
    _messageSubscription = _chatRepo.messageStream.listen((message) {
      state = state.copyWith(messages: [...state.messages, message]);
    });

    // Listen for typing indicators
    // الاستماع لمؤشرات الكتابة
    _typingSubscription = _chatRepo.typingStream.listen((data) {
      state = state.copyWith(
        isTyping: (data['isTyping'] ?? false) as bool,
        typingUser: data['userName'] as String?,
      );
    });

    // Listen for expert joining via WebSocket
    // الاستماع لانضمام الخبير عبر WebSocket
    _expertJoinedSubscription = _chatRepo.expertJoinedStream.listen((data) {
      state = state.copyWith(expertJoined: true);
      _addSystemMessage(
        data['expertName'] as String? ?? 'Expert',
        isJoinEvent: true,
      );
    });

    // Add welcome message
    // إضافة رسالة ترحيب
    addSystemMessage(
      'Welcome to expert chat. You will be connected to an agricultural expert shortly...',
      textAr: 'مرحباً بك في محادثة الخبراء. سيتم توصيلك بخبير زراعي قريباً...',
    );
  }

  /// Add a system message to the chat.
  /// إضافة رسالة نظام إلى الدردشة.
  void addSystemMessage(String text, {String? textAr}) {
    final displayText = textAr != null ? '$text\n$textAr' : text;
    final message = ChatMessage(
      id: 'system_${DateTime.now().millisecondsSinceEpoch}',
      roomId: roomId,
      author: 'System | النظام',
      authorType: 'system',
      message: displayText,
      timestamp: DateTime.now(),
    );
    state = state.copyWith(messages: [...state.messages, message]);
  }

  void _addSystemMessage(String expertName, {bool isJoinEvent = false}) {
    if (isJoinEvent) {
      addSystemMessage(
        '$expertName joined the conversation',
        textAr: 'انضم $expertName للمحادثة',
      );
    }
  }

  /// Send a user message via the repository.
  /// إرسال رسالة المستخدم عبر المستودع.
  void sendMessage(String text) {
    if (text.trim().isEmpty) return;
    _chatRepo.sendMessage(
      roomId: roomId,
      author: userName,
      authorType: 'farmer',
      message: text.trim(),
    );
  }

  /// Send an attachment message via the repository.
  /// إرسال رسالة مرفقة عبر المستودع.
  void sendAttachment(String filePath, String fileName) {
    _chatRepo.sendMessage(
      roomId: roomId,
      author: userName,
      authorType: 'farmer',
      message: 'Attachment | مرفق: $fileName',
      attachments: [filePath],
    );
  }

  /// Reload / refresh messages (placeholder for API-backed history).
  /// تحديث الرسائل (عنصر نائب لسجل المحادثات المدعوم بالخادم).
  Future<void> refresh() async {
    state = state.copyWith(isLoading: true);
    // TODO: Wire to chatRepo.fetchMessageHistory(roomId) when backend ready
    await Future<void>.delayed(const Duration(milliseconds: 400));
    state = state.copyWith(isLoading: false);
  }

  /// Mark expert as joined (for external / WebSocket trigger).
  /// تحديد انضمام الخبير (للمشغل الخارجي / WebSocket).
  void markExpertJoined(String expertName) {
    state = state.copyWith(expertJoined: true);
    _addSystemMessage(expertName, isJoinEvent: true);
  }

  @override
  void dispose() {
    _messageSubscription?.cancel();
    _typingSubscription?.cancel();
    _expertJoinedSubscription?.cancel();
    _chatRepo.leaveRoom(roomId: roomId, userName: userName);
    super.dispose();
  }
}

/// Family provider keyed on roomId so each room gets its own notifier.
/// مزود عائلي مفتاح برقم الغرفة بحيث تحصل كل غرفة على مدير خاص بها.
final chatNotifierProvider =
    StateNotifierProvider.autoDispose.family<ChatNotifier, ChatState, ({String roomId, String userName})>(
  (ref, params) {
    final chatRepo = ref.watch(chatRepositoryProvider);
    final notifier = ChatNotifier(
      chatRepo: chatRepo,
      roomId: params.roomId,
      userName: params.userName,
    );
    notifier.initialize();
    return notifier;
  },
);

// ---------------------------------------------------------------------------
// Chat Screen Widget
// عنصر شاشة الدردشة
// ---------------------------------------------------------------------------

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

  // Attachment picker state
  // حالة منتقي المرفقات
  final ImagePicker _imagePicker = ImagePicker();
  bool _isCapturingImage = false;

  /// Maximum file size: 10 MB
  /// الحد الأقصى لحجم الملف: 10 ميجابايت
  static const int _maxFileSizeBytes = 10 * 1024 * 1024;

  /// Provider params derived from widget properties.
  ({String roomId, String userName}) get _providerKey =>
      (roomId: widget.roomId, userName: widget.userName);

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

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

  void _sendMessage() {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    ref.read(chatNotifierProvider(_providerKey).notifier).sendMessage(text);
    _messageController.clear();
    _scrollToBottom();
  }

  String _formatTime(DateTime time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  // ---------------------------------------------------------------------------
  // Build
  // ---------------------------------------------------------------------------

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatNotifierProvider(_providerKey));

    // Auto-scroll when new messages arrive
    ref.listen<ChatState>(chatNotifierProvider(_providerKey), (prev, next) {
      if ((prev?.messages.length ?? 0) < next.messages.length) {
        _scrollToBottom();
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Expert Chat | محادثة الخبراء'),
            if (chatState.expertJoined)
              Text(
                'Connected to expert | متصل مع خبير',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
              )
            else
              Text(
                'Waiting for expert... | في انتظار خبير...',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.normal, color: Colors.white70),
              ),
          ],
        ),
        backgroundColor: const Color(0xFF16A34A),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            tooltip: 'Chat info | معلومات المحادثة',
            onPressed: () => _showInfoDialog(chatState),
          ),
        ],
      ),
      body: Column(
        children: [
          // Topic banner if provided
          // شريط الموضوع إذا وجد
          if (widget.topic != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: const Color(0xFF16A34A).withValues(alpha: 0.1),
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

          // Messages list with pull-to-refresh
          // قائمة الرسائل مع السحب للتحديث
          Expanded(
            child: RefreshIndicator(
              onRefresh: () => ref.read(chatNotifierProvider(_providerKey).notifier).refresh(),
              color: const Color(0xFF16A34A),
              child: chatState.messages.isEmpty
                  ? _buildEmptyState()
                  : ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.all(16),
                      itemCount: chatState.messages.length,
                      itemBuilder: (context, index) {
                        return _buildMessageBubble(chatState.messages[index]);
                      },
                    ),
            ),
          ),

          // Typing indicator
          // مؤشر الكتابة
          if (chatState.isTyping && chatState.typingUser != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                children: [
                  Text(
                    '${chatState.typingUser} is typing... | ${chatState.typingUser} يكتب...',
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
          // حقل الإدخال
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
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
                    tooltip: 'Attach file | إرفاق ملف',
                    onPressed: _showAttachmentPicker,
                  ),

                  // Text input
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      textDirection: TextDirection.rtl,
                      decoration: InputDecoration(
                        hintText: 'Type your message... | اكتب رسالتك هنا...',
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
                      tooltip: 'Send | إرسال',
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

  // ---------------------------------------------------------------------------
  // Empty State
  // حالة عدم وجود رسائل
  // ---------------------------------------------------------------------------

  Widget _buildEmptyState() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.chat_bubble_outline, size: 72, color: Colors.grey[300]),
                    const SizedBox(height: 16),
                    Text(
                      'No messages yet',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.grey[600]),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'لا توجد رسائل بعد',
                      style: TextStyle(fontSize: 16, color: Colors.grey[500]),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Start the conversation by typing a message below.',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: Colors.grey[400]),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'ابدأ المحادثة بكتابة رسالة أدناه.',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: Colors.grey[400]),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  // ---------------------------------------------------------------------------
  // Message Bubble
  // فقاعة الرسالة
  // ---------------------------------------------------------------------------

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
            // اسم المؤلف (للخبراء)
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
            // فقاعة الرسالة
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
            // الوقت
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

  // ---------------------------------------------------------------------------
  // Info Dialog
  // حوار المعلومات
  // ---------------------------------------------------------------------------

  void _showInfoDialog(ChatState chatState) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Chat Info | معلومات المحادثة'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoRow(
              'Room | رقم الغرفة',
              widget.roomId.split('_').last,
            ),
            const SizedBox(height: 8),
            _buildInfoRow(
              'Topic | الموضوع',
              widget.topic ?? 'General consultation | استشارة عامة',
            ),
            const SizedBox(height: 8),
            _buildInfoRow(
              'Status | الحالة',
              chatState.expertJoined
                  ? 'Connected to expert | متصل بخبير'
                  : 'Waiting for expert | في انتظار خبير',
            ),
            const SizedBox(height: 8),
            _buildInfoRow(
              'Messages | عدد الرسائل',
              chatState.messages.length.toString(),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close | إغلاق'),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Flexible(child: Text(label, style: const TextStyle(color: Colors.grey))),
        const SizedBox(width: 8),
        Flexible(child: Text(value, style: const TextStyle(fontWeight: FontWeight.w500))),
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
              'Attach File | إرفاق ملف',
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
                  label: 'Gallery | صورة من المعرض',
                  color: Colors.blue,
                  onTap: () {
                    Navigator.pop(context);
                    _pickImageFromGallery();
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.camera_alt,
                  label: 'Camera | التقاط صورة',
                  color: Colors.purple,
                  onTap: () {
                    Navigator.pop(context);
                    _captureFromCamera();
                  },
                ),
                _buildAttachmentOption(
                  icon: Icons.insert_drive_file,
                  label: 'Document | ملف مستند',
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
                content: Text('Please allow photo access in Settings | يرجى السماح بالوصول إلى الصور من الإعدادات'),
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
        ref.read(chatNotifierProvider(_providerKey).notifier).sendAttachment(
              image.path,
              _getFileNameFromPath(image.path),
            );
      }
    } catch (e) {
      if (mounted) {
        final errorMessage = e.toString().contains('photo_access_denied') ||
                e.toString().contains('permission')
            ? 'Please allow photo access in Settings | يرجى السماح بالوصول إلى الصور من الإعدادات'
            : 'Error selecting image | حدث خطأ أثناء اختيار الصورة';
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
              content: Text('Please allow camera access in Settings | يرجى السماح بالوصول إلى الكاميرا من الإعدادات'),
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
        ref.read(chatNotifierProvider(_providerKey).notifier).sendAttachment(
              image.path,
              _getFileNameFromPath(image.path),
            );
      }
    } catch (e) {
      if (mounted) {
        final errorMessage = e.toString().contains('camera_access_denied') ||
                e.toString().contains('permission')
            ? 'Please allow camera access in Settings | يرجى السماح بالوصول إلى الكاميرا من الإعدادات'
            : 'Error capturing image | حدث خطأ أثناء التقاط الصورة';
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
              content: Text('Cannot access file | لا يمكن الوصول إلى الملف'),
              backgroundColor: Colors.red,
            ),
          );
          return;
        }

        // Check file size limit
        if (fileSize > _maxFileSizeBytes) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('File exceeds 10 MB limit | حجم الملف يتجاوز الحد الأقصى (10 ميجابايت)'),
              backgroundColor: Colors.red,
            ),
          );
          return;
        }

        ref.read(chatNotifierProvider(_providerKey).notifier).sendAttachment(filePath, fileName);
      }
    } catch (e) {
      if (mounted) {
        final errorMessage = e.toString().contains('permission')
            ? 'Please allow file access in Settings | يرجى السماح بالوصول إلى الملفات من الإعدادات'
            : 'Error selecting file | حدث خطأ أثناء اختيار الملف';
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
}
