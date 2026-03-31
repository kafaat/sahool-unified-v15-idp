library;

/// Conversations Screen
/// شاشة قائمة المحادثات
///
/// Features:
/// - List of conversations
/// - Pull to refresh
/// - Unread badge in app bar
/// - Search conversations by contact name or last message
/// - Empty state

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/conversation_model.dart';
import '../providers/chat_provider.dart';
import '../../widgets/conversation_tile.dart';
import 'chat_screen.dart';

class ConversationsScreen extends ConsumerStatefulWidget {
  const ConversationsScreen({super.key});

  @override
  ConsumerState<ConversationsScreen> createState() =>
      _ConversationsScreenState();
}

class _ConversationsScreenState extends ConsumerState<ConversationsScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  bool _isSearching = false;

  @override
  void initState() {
    super.initState();
    // Load conversations on init
    Future.microtask(() {
      ref.read(chatProvider.notifier).loadConversations();
    });
    // Listen to search input changes
    _searchController.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _searchController.removeListener(_onSearchChanged);
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    setState(() {
      _searchQuery = _searchController.text.toLowerCase().trim();
    });
  }

  /// Filter conversations based on search query
  List<Conversation> _filterConversations(
    List<Conversation> conversations,
    String currentUserId,
  ) {
    if (_searchQuery.isEmpty) {
      return conversations;
    }

    return conversations.where((conversation) {
      // Search by contact name
      final displayName =
          conversation.getDisplayName(currentUserId).toLowerCase();
      if (displayName.contains(_searchQuery)) {
        return true;
      }

      // Search by participant names (including Arabic names)
      for (final participant in conversation.participants) {
        if (participant.name.toLowerCase().contains(_searchQuery)) {
          return true;
        }
        if (participant.nameAr?.toLowerCase().contains(_searchQuery) ?? false) {
          return true;
        }
      }

      // Search by last message content
      final lastMessagePreview = conversation.lastMessagePreview.toLowerCase();
      if (lastMessagePreview.contains(_searchQuery)) {
        return true;
      }

      return false;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(chatProvider);
    final currentUserId = ref.watch(chatUserIdProvider);
    final unreadCount = ref.watch(unreadCountProvider);

    return Scaffold(
      appBar: AppBar(
        title: _isSearching
            ? TextField(
                controller: _searchController,
                autofocus: true,
                decoration: const InputDecoration(
                  hintText: 'بحث باسم المستخدم أو الرسالة...',
                  border: InputBorder.none,
                  hintStyle: TextStyle(color: Colors.white70),
                ),
                style: const TextStyle(color: Colors.white),
                cursorColor: Colors.white,
              )
            : const Text('المحادثات'),
        centerTitle: !_isSearching,
        leading: _isSearching
            ? IconButton(
                onPressed: () {
                  setState(() {
                    _isSearching = false;
                    _searchController.clear();
                    _searchQuery = '';
                  });
                },
                icon: const Icon(Icons.arrow_back),
                tooltip: 'إلغاء البحث',
              )
            : null,
        actions: [
          // Unread badge (hide when searching)
          if (unreadCount > 0 && !_isSearching)
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

          // Search button / Clear button
          if (_isSearching)
            IconButton(
              onPressed: () {
                _searchController.clear();
              },
              icon: const Icon(Icons.close),
              tooltip: 'مسح',
            )
          else
            IconButton(
              onPressed: () {
                setState(() {
                  _isSearching = true;
                });
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
        child: _buildBody(state, currentUserId,
            _filterConversations(state.conversations, currentUserId)),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showNewConversationDialog(context),
        tooltip: 'محادثة جديدة',
        child: const Icon(Icons.message),
      ),
    );
  }

  Widget _buildBody(ChatState state, String currentUserId,
      List<Conversation> filteredConversations) {
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
                ref
                    .read(chatProvider.notifier)
                    .loadConversations(forceRefresh: true);
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

    // Handle empty search results
    if (_isSearching && filteredConversations.isEmpty) {
      return _buildEmptySearchResults();
    }

    return ListView.builder(
      itemCount: filteredConversations.length,
      itemBuilder: (context, index) {
        final conversation = filteredConversations[index];
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

  Widget _buildEmptySearchResults() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search_off,
            size: 80,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد نتائج',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'لم يتم العثور على محادثات تطابق "$_searchQuery"',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 16),
          TextButton(
            onPressed: () {
              _searchController.clear();
            },
            child: const Text('مسح البحث'),
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

  void _showNewConversationDialog(BuildContext context) {
    final userIdController = TextEditingController();
    final formKey = GlobalKey<FormState>();
    bool isLoading = false;
    String? errorText;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('محادثة جديدة'),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'أدخل معرف المستخدم الذي تريد التواصل معه',
                  style: TextStyle(fontSize: 14),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: userIdController,
                  enabled: !isLoading,
                  decoration: InputDecoration(
                    hintText: 'معرف المستخدم',
                    prefixIcon: const Icon(Icons.person),
                    errorText: errorText,
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'يرجى إدخال معرف المستخدم';
                    }
                    return null;
                  },
                  textInputAction: TextInputAction.done,
                  onFieldSubmitted: isLoading
                      ? null
                      : (_) => _startConversation(
                            dialogContext,
                            userIdController,
                            formKey,
                            setDialogState,
                            () => isLoading,
                            (value) => isLoading = value,
                            (value) => errorText = value,
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
                if (isLoading) ...[
                  const SizedBox(height: 16),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      SizedBox(width: 12),
                      Text('جاري إنشاء المحادثة...'),
                    ],
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: isLoading ? null : () => Navigator.pop(dialogContext),
              child: const Text('إلغاء'),
            ),
            ElevatedButton(
              onPressed: isLoading
                  ? null
                  : () => _startConversation(
                        dialogContext,
                        userIdController,
                        formKey,
                        setDialogState,
                        () => isLoading,
                        (value) => isLoading = value,
                        (value) => errorText = value,
                      ),
              child: const Text('بدء المحادثة'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _startConversation(
    BuildContext dialogContext,
    TextEditingController userIdController,
    GlobalKey<FormState> formKey,
    void Function(void Function()) setDialogState,
    bool Function() getIsLoading,
    void Function(bool) setIsLoading,
    void Function(String?) setErrorText,
  ) async {
    // Validate form
    if (!formKey.currentState!.validate()) {
      return;
    }

    final userId = userIdController.text.trim();

    // Set loading state
    setDialogState(() {
      setIsLoading(true);
      setErrorText(null);
    });

    try {
      // Create conversation
      final conversation = await ref
          .read(chatProvider.notifier)
          .createConversation(participantId: userId);

      if (!dialogContext.mounted) return;

      if (conversation != null) {
        // Close dialog and navigate to chat
        Navigator.pop(dialogContext);

        if (mounted) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ChatScreen(
                conversationId: conversation.id,
              ),
            ),
          );
        }
      } else {
        // Show error from provider state
        final error = ref.read(chatProvider).error;
        setDialogState(() {
          setIsLoading(false);
          setErrorText(error ?? 'فشل في إنشاء المحادثة');
        });
      }
    } catch (e) {
      if (!dialogContext.mounted) return;
      setDialogState(() {
        setIsLoading(false);
        setErrorText('حدث خطأ غير متوقع');
      });
    }
  }
}
