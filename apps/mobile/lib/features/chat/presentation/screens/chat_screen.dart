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

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
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

    await ref.read(chatProvider.notifier).loadMoreMessages(widget.conversationId);

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
              backgroundColor: SahoolTheme.primary.withOpacity(0.1),
              backgroundImage: otherParticipant?.avatarUrl != null
                  ? NetworkImage(otherParticipant!.avatarUrl!)
                  : null,
              child: otherParticipant?.avatarUrl == null
                  ? Icon(
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
              // TODO: Handle menu actions
              _handleMenuAction(value as String, conversation);
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
                        SizedBox(
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
          ),
        ],
      ),
    );
  }

  Widget _buildInfoBanner(conversation) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: SahoolTheme.primary.withOpacity(0.1),
        border: Border(
          bottom: BorderSide(
            color: SahoolTheme.primary.withOpacity(0.3),
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
              style: TextStyle(
                fontSize: 14,
                color: SahoolTheme.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              // TODO: Navigate to product/order
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

  void _handleMenuAction(String action, conversation) {
    switch (action) {
      case 'view_profile':
        // TODO: Navigate to user profile
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('عرض الملف الشخصي - قيد التطوير')),
        );
        break;

      case 'view_product':
        // TODO: Navigate to product
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('عرض المنتج - قيد التطوير')),
        );
        break;

      case 'view_order':
        // TODO: Navigate to order
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('عرض الطلب - قيد التطوير')),
        );
        break;

      case 'block':
        // TODO: Implement block user
        _showBlockConfirmation();
        break;
    }
  }

  void _showBlockConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حظر المستخدم'),
        content: const Text('هل أنت متأكد أنك تريد حظر هذا المستخدم؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Implement block
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('تم حظر المستخدم')),
              );
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
}
