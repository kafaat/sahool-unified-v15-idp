/// Chat Screen
/// شاشة المحادثة الفردية
///
/// Features:
/// - Messages list (reversed)
/// - Real-time updates
/// - Typing indicator
/// - Message input
/// - Online status
/// - Load more messages (pagination)
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/theme.dart';
import '../../data/models/conversation_model.dart';
import '../../data/models/message_model.dart';
import '../providers/chat_provider.dart';
import '../../widgets/message_bubble.dart';
import '../../widgets/chat_input.dart';

class ChatScreen extends ConsumerStatefulWidget {
  final String conversationId;

  const ChatScreen({
    super.key,
    required this.conversationId,
  });

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final ScrollController _scrollController = ScrollController();
  bool _isLoadingMore = false;

  @override
  void initState() {
    super.initState();

    // Open conversation and load messages
    Future.microtask(() {
      ref.read(chatProvider.notifier).openConversation(widget.conversationId);
    });

    // Setup scroll listener for pagination
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();

    // Close conversation
    ref.read(chatProvider.notifier).closeConversation();

    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      if (!_isLoadingMore) {
        _loadMoreMessages();
      }
    }
  }

  Future<void> _loadMoreMessages() async {
    setState(() => _isLoadingMore = true);

    await ref
        .read(chatProvider.notifier)
        .loadMoreMessages(widget.conversationId);

    if (mounted) {
      setState(() => _isLoadingMore = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final conversation = ref.watch(activeConversationProvider);
    final messages = ref.watch(activeMessagesProvider);
    final currentUserId = ref.watch(chatUserIdProvider);
    final isTyping = ref.watch(activeConversationTypingProvider);

    if (conversation == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('محادثة'),
        ),
        body: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    final otherParticipant = conversation.getOtherParticipant(currentUserId);
    final displayName = conversation.getDisplayName(currentUserId);
    final isOnline = otherParticipant?.isOnline ?? false;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(displayName),
            if (isOnline)
              const Text(
                'متصل الآن',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.normal,
                ),
              )
            else if (otherParticipant?.lastSeen != null)
              Text(
                'آخر ظهور ${_formatLastSeen(otherParticipant!.lastSeen!)}',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.normal,
                ),
              ),
          ],
        ),
        actions: [
          // Avatar
          Padding(
            padding: const EdgeInsets.only(left: 16),
            child: CircleAvatar(
              radius: 18,
              backgroundColor: SahoolTheme.primary.withValues(alpha: 0.1),
              backgroundImage: otherParticipant?.avatarUrl != null
                  ? NetworkImage(otherParticipant!.avatarUrl!)
                  : null,
              child: otherParticipant?.avatarUrl == null
                  ? const Icon(
                      Icons.person,
                      size: 20,
                      color: SahoolTheme.primary,
                    )
                  : null,
            ),
          ),

          // More options
          PopupMenuButton(
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'view_profile',
                child: Row(
                  children: [
                    Icon(Icons.person),
                    SizedBox(width: 8),
                    Text('عرض الملف الشخصي'),
                  ],
                ),
              ),
              if (conversation.productId != null)
                const PopupMenuItem(
                  value: 'view_product',
                  child: Row(
                    children: [
                      Icon(Icons.shopping_bag),
                      SizedBox(width: 8),
                      Text('عرض المنتج'),
                    ],
                  ),
                ),
              if (conversation.orderId != null)
                const PopupMenuItem(
                  value: 'view_order',
                  child: Row(
                    children: [
                      Icon(Icons.receipt_long),
                      SizedBox(width: 8),
                      Text('عرض الطلب'),
                    ],
                  ),
                ),
              PopupMenuItem(
                value: 'mute',
                child: Row(
                  children: [
                    Icon(conversation.isMuted
                        ? Icons.notifications_active
                        : Icons.notifications_off),
                    const SizedBox(width: 8),
                    Text(conversation.isMuted ? 'إلغاء الكتم' : 'كتم المحادثة'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'clear_chat',
                child: Row(
                  children: [
                    Icon(Icons.delete_sweep),
                    SizedBox(width: 8),
                    Text('مسح المحادثة'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'report',
                child: Row(
                  children: [
                    Icon(Icons.flag, color: Colors.orange),
                    SizedBox(width: 8),
                    Text('إبلاغ', style: TextStyle(color: Colors.orange)),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'block',
                child: Row(
                  children: [
                    Icon(Icons.block, color: Colors.red),
                    SizedBox(width: 8),
                    Text('حظر', style: TextStyle(color: Colors.red)),
                  ],
                ),
              ),
            ],
            onSelected: (value) {
              _handleMenuAction(value, conversation);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Product/Order info banner (if applicable)
          if (conversation.productId != null || conversation.orderId != null)
            _buildInfoBanner(conversation),

          // Messages list
          Expanded(
            child: messages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    reverse: true,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    itemCount: messages.length + (_isLoadingMore ? 1 : 0),
                    itemBuilder: (context, index) {
                      // Loading indicator at the end
                      if (_isLoadingMore && index == messages.length) {
                        return const Center(
                          child: Padding(
                            padding: EdgeInsets.all(16),
                            child: CircularProgressIndicator(),
                          ),
                        );
                      }

                      final message = messages[index];
                      final showAvatar = index == 0 ||
                          messages[index - 1].senderId != message.senderId;
                      final showName = showAvatar && !message.isMine;

                      return MessageBubble(
                        message: message,
                        showAvatar: showAvatar,
                        showName: showName,
                      );
                    },
                  ),
          ),

          // Typing indicator
          if (isTyping)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              alignment: Alignment.centerRight,
              child: Row(
                children: [
                  const SizedBox(width: 60), // Space for avatar
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 10,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'جاري الكتابة',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                        const SizedBox(width: 8),
                        const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: SahoolTheme.primary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

          // Message input
          ChatInput(
            onSendMessage: (message) {
              ref.read(chatProvider.notifier).sendMessage(
                    widget.conversationId,
                    content: message,
                  );

              // Scroll to bottom
              _scrollToBottom();
            },
            onTypingChanged: (isTyping) {
              ref.read(chatProvider.notifier).sendTyping(
                    widget.conversationId,
                    isTyping: isTyping,
                  );
            },
            onFileSelected: (filePath, fileName, fileSize) {
              ref.read(chatProvider.notifier).sendMessage(
                widget.conversationId,
                content: fileName,
                type: MessageType.file,
                attachmentUrl: filePath,
                metadata: {
                  'fileName': fileName,
                  'fileSize': fileSize,
                  'filePath': filePath,
                },
              );

              // Scroll to bottom
              _scrollToBottom();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildInfoBanner(Conversation conversation) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: SahoolTheme.primary.withValues(alpha: 0.1),
        border: Border(
          bottom: BorderSide(
            color: SahoolTheme.primary.withValues(alpha: 0.3),
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          Icon(
            conversation.productId != null
                ? Icons.shopping_bag
                : Icons.receipt_long,
            color: SahoolTheme.primary,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              conversation.productId != null
                  ? 'محادثة حول منتج'
                  : 'محادثة حول طلب',
              style: const TextStyle(
                fontSize: 14,
                color: SahoolTheme.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              // Navigate to product or order details based on conversation context
              if (conversation.productId != null) {
                context.push('/product/${conversation.productId}');
              } else if (conversation.orderId != null) {
                context.push('/order/${conversation.orderId}');
              }
            },
            child: const Text('عرض'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            size: 64,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد رسائل بعد',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'ابدأ المحادثة بإرسال رسالة',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  String _formatLastSeen(DateTime lastSeen) {
    final now = DateTime.now();
    final diff = now.difference(lastSeen);

    if (diff.inMinutes < 1) {
      return 'منذ لحظات';
    } else if (diff.inMinutes < 60) {
      return 'منذ ${diff.inMinutes} دقيقة';
    } else if (diff.inHours < 24) {
      return 'منذ ${diff.inHours} ساعة';
    } else if (diff.inDays < 7) {
      return 'منذ ${diff.inDays} يوم';
    } else {
      return '${lastSeen.day}/${lastSeen.month}/${lastSeen.year}';
    }
  }

  void _handleMenuAction(String action, Conversation conversation) {
    switch (action) {
      case 'view_profile':
        // Navigate to user profile
        final currentUserId = ref.read(chatUserIdProvider);
        final otherParticipant =
            conversation.getOtherParticipant(currentUserId);
        if (otherParticipant != null) {
          context.push(
            '/user/${otherParticipant.userId}',
            extra: {
              'userId': otherParticipant.userId,
              'name': otherParticipant.name,
              'nameAr': otherParticipant.nameAr,
              'avatarUrl': otherParticipant.avatarUrl,
              'role': otherParticipant.role,
            },
          );
        }
        break;

      case 'view_product':
        if (conversation.productId != null) {
          context.push('/product/${conversation.productId}');
        }
        break;

      case 'view_order':
        if (conversation.orderId != null) {
          context.push('/order/${conversation.orderId}');
        }
        break;

      case 'mute':
        _handleMuteConversation(conversation);
        break;

      case 'clear_chat':
        _showClearChatConfirmation(conversation);
        break;

      case 'report':
        _showReportDialog(conversation);
        break;

      case 'block':
        _showBlockConfirmation(conversation);
        break;
    }
  }

  void _showBlockConfirmation(Conversation conversation) {
    final currentUserId = ref.read(chatUserIdProvider);
    final otherParticipant = conversation.getOtherParticipant(currentUserId);

    if (otherParticipant == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('لا يمكن حظر هذا المستخدم'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('حظر المستخدم'),
        content: Text(
          'هل أنت متأكد أنك تريد حظر ${otherParticipant.displayName}؟\n\n'
          'لن تتمكن من تلقي رسائل من هذا المستخدم بعد الآن.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(dialogContext);

              // Show loading indicator
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Row(
                    children: [
                      SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(width: 16),
                      Text('جاري حظر المستخدم...'),
                    ],
                  ),
                  duration: Duration(seconds: 30),
                ),
              );

              // Call block user API
              final success = await ref.read(chatProvider.notifier).blockUser(
                    otherParticipant.userId,
                    conversation.id,
                  );

              if (!mounted) return;

              // Hide loading snackbar
              ScaffoldMessenger.of(context).hideCurrentSnackBar();

              if (success) {
                // Show success message
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('تم حظر ${otherParticipant.displayName}'),
                    backgroundColor: Colors.green,
                  ),
                );

                // Navigate back to conversations list
                Navigator.pop(context);
              } else {
                // Show error message
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content:
                        Text('فشل في حظر المستخدم. يرجى المحاولة مرة أخرى.'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('حظر'),
          ),
        ],
      ),
    );
  }

  Future<void> _handleMuteConversation(Conversation conversation) async {
    final isMuted = conversation.isMuted;
    final newMuteState = !isMuted;

    // Show loading indicator
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 16),
            Text(newMuteState
                ? 'جاري كتم المحادثة...'
                : 'جاري إلغاء كتم المحادثة...'),
          ],
        ),
        duration: const Duration(seconds: 30),
      ),
    );

    final success = await ref.read(chatProvider.notifier).muteConversation(
          conversation.id,
          mute: newMuteState,
        );

    if (!mounted) return;

    // Hide loading snackbar
    ScaffoldMessenger.of(context).hideCurrentSnackBar();

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content:
              Text(newMuteState ? 'تم كتم المحادثة' : 'تم إلغاء كتم المحادثة'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(newMuteState
              ? 'فشل في كتم المحادثة. يرجى المحاولة مرة أخرى.'
              : 'فشل في إلغاء كتم المحادثة. يرجى المحاولة مرة أخرى.'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showClearChatConfirmation(Conversation conversation) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('مسح المحادثة'),
        content: const Text(
          'هل أنت متأكد أنك تريد مسح جميع الرسائل في هذه المحادثة؟\n\n'
          'لا يمكن التراجع عن هذا الإجراء.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(dialogContext);

              // Show loading indicator
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Row(
                    children: [
                      SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(width: 16),
                      Text('جاري مسح المحادثة...'),
                    ],
                  ),
                  duration: Duration(seconds: 30),
                ),
              );

              final success = await ref
                  .read(chatProvider.notifier)
                  .clearChatHistory(conversation.id);

              if (!mounted) return;

              // Hide loading snackbar
              ScaffoldMessenger.of(context).hideCurrentSnackBar();

              if (success) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم مسح المحادثة بنجاح'),
                    backgroundColor: Colors.green,
                  ),
                );
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content:
                        Text('فشل في مسح المحادثة. يرجى المحاولة مرة أخرى.'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('مسح'),
          ),
        ],
      ),
    );
  }

  void _showReportDialog(Conversation conversation) {
    String? selectedReason;
    final descriptionController = TextEditingController();

    final reportReasons = [
      {'value': 'spam', 'label': 'رسائل مزعجة (سبام)'},
      {'value': 'harassment', 'label': 'مضايقة أو تحرش'},
      {'value': 'fraud', 'label': 'احتيال أو نصب'},
      {'value': 'inappropriate', 'label': 'محتوى غير لائق'},
      {'value': 'fake_account', 'label': 'حساب مزيف'},
      {'value': 'other', 'label': 'سبب آخر'},
    ];

    showDialog(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('إبلاغ عن المحادثة'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'اختر سبب الإبلاغ:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                ...reportReasons.map((reason) => RadioListTile<String>(
                      title: Text(reason['label']!),
                      value: reason['value']!,
                      groupValue: selectedReason,
                      onChanged: (value) {
                        setDialogState(() {
                          selectedReason = value;
                        });
                      },
                      contentPadding: EdgeInsets.zero,
                      dense: true,
                    )),
                const SizedBox(height: 16),
                const Text(
                  'تفاصيل إضافية (اختياري):',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: descriptionController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    hintText: 'اكتب تفاصيل إضافية...',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                descriptionController.dispose();
                Navigator.pop(dialogContext);
              },
              child: const Text('إلغاء'),
            ),
            ElevatedButton(
              onPressed: selectedReason == null
                  ? null
                  : () async {
                      Navigator.pop(dialogContext);

                      // Show loading indicator
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Row(
                            children: [
                              SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              ),
                              SizedBox(width: 16),
                              Text('جاري إرسال البلاغ...'),
                            ],
                          ),
                          duration: Duration(seconds: 30),
                        ),
                      );

                      final success = await ref
                          .read(chatProvider.notifier)
                          .reportConversation(
                            conversation.id,
                            reason: selectedReason!,
                            description: descriptionController.text.isNotEmpty
                                ? descriptionController.text
                                : null,
                          );

                      descriptionController.dispose();

                      if (!mounted) return;

                      // Hide loading snackbar
                      ScaffoldMessenger.of(context).hideCurrentSnackBar();

                      if (success) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content:
                                Text('تم إرسال البلاغ بنجاح. شكرا لمساعدتك.'),
                            backgroundColor: Colors.green,
                          ),
                        );
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text(
                                'فشل في إرسال البلاغ. يرجى المحاولة مرة أخرى.'),
                            backgroundColor: Colors.red,
                          ),
                        );
                      }
                    },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
              ),
              child: const Text('إرسال البلاغ'),
            ),
          ],
        ),
      ),
    );
  }
}
