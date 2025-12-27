/// Conversations Screen
/// شاشة قائمة المحادثات
///
/// Features:
/// - List of conversations
/// - Pull to refresh
/// - Unread badge in app bar
/// - Search conversations (future)
/// - Empty state

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../providers/chat_provider.dart';
import '../../widgets/conversation_tile.dart';
import 'chat_screen.dart';

class ConversationsScreen extends ConsumerStatefulWidget {
  const ConversationsScreen({super.key});

  @override
  ConsumerState<ConversationsScreen> createState() => _ConversationsScreenState();
}

class _ConversationsScreenState extends ConsumerState<ConversationsScreen> {
  @override
  void initState() {
    super.initState();
    // Load conversations on init
    Future.microtask(() {
      ref.read(chatProvider.notifier).loadConversations();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(chatProvider);
    final currentUserId = ref.watch(chatUserIdProvider);
    final unreadCount = ref.watch(unreadCountProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('المحادثات'),
        centerTitle: true,
        actions: [
          // Unread badge
          if (unreadCount > 0)
            Padding(
              padding: const EdgeInsets.only(left: 16),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    unreadCount > 99 ? '99+' : unreadCount.toString(),
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),

          // Search button (future feature)
          IconButton(
            onPressed: () {
              // TODO: Implement search
              _showSearchDialog(context);
            },
            icon: const Icon(Icons.search),
            tooltip: 'بحث',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await ref.read(chatProvider.notifier).refreshConversations();
        },
        child: _buildBody(state, currentUserId),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: Implement new conversation
          _showNewConversationDialog(context);
        },
        child: const Icon(Icons.message),
        tooltip: 'محادثة جديدة',
      ),
    );
  }

  Widget _buildBody(ChatState state, String currentUserId) {
    if (state.isLoading && state.conversations.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (state.error != null && state.conversations.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              state.error!,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                ref.read(chatProvider.notifier).loadConversations(forceRefresh: true);
              },
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      );
    }

    if (state.conversations.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.builder(
      itemCount: state.conversations.length,
      itemBuilder: (context, index) {
        final conversation = state.conversations[index];
        return ConversationTile(
          conversation: conversation,
          currentUserId: currentUserId,
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => ChatScreen(
                  conversationId: conversation.id,
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            size: 80,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد محادثات',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'ابدأ محادثة جديدة مع البائعين أو المشترين',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              _showNewConversationDialog(context);
            },
            icon: const Icon(Icons.add),
            label: const Text('محادثة جديدة'),
          ),
        ],
      ),
    );
  }

  void _showSearchDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('بحث في المحادثات'),
        content: const TextField(
          decoration: InputDecoration(
            hintText: 'اكتب اسم المستخدم...',
            prefixIcon: Icon(Icons.search),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              // TODO: Implement search
              Navigator.pop(context);
            },
            child: const Text('بحث'),
          ),
        ],
      ),
    );
  }

  void _showNewConversationDialog(BuildContext context) {
    final userIdController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('محادثة جديدة'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'أدخل معرف المستخدم الذي تريد التواصل معه',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: userIdController,
              decoration: const InputDecoration(
                hintText: 'معرف المستخدم',
                prefixIcon: Icon(Icons.person),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'أو ابحث عن المستخدم من قائمة البائعين في السوق',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () async {
              final userId = userIdController.text.trim();
              if (userId.isEmpty) return;

              Navigator.pop(context);

              // Create conversation
              final conversation = await ref
                  .read(chatProvider.notifier)
                  .createConversation(participantId: userId);

              if (conversation != null && context.mounted) {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ChatScreen(
                      conversationId: conversation.id,
                    ),
                  ),
                );
              }
            },
            child: const Text('بدء المحادثة'),
          ),
        ],
      ),
    );
  }
}
