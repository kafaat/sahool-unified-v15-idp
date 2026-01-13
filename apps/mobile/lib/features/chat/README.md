# Chat/Messaging Feature - SAHOOL Mobile App

# ميزة المحادثات والرسائل - تطبيق سهول للهاتف المحمول

## Overview | نظرة عامة

A comprehensive chat/messaging feature for the SAHOOL mobile app that enables real-time communication between buyers and sellers in the marketplace.

ميزة محادثات شاملة لتطبيق سهول للهاتف المحمول تتيح التواصل الفوري بين المشترين والبائعين في السوق.

## Features | الميزات

### ✅ Implemented Features | الميزات المنفذة

- **Conversations List** - قائمة المحادثات
  - Display all user conversations
  - Show last message preview
  - Unread message badge
  - Typing indicator
  - Online status indicator
  - Pull to refresh

- **Individual Chat** - المحادثة الفردية
  - Real-time messaging
  - Message bubbles (green for sent, gray for received)
  - Sender name and avatar
  - Timestamp for each message
  - Message status (sending/sent/delivered/read/failed)
  - Typing indicator
  - Load more messages (pagination)
  - Online/offline status

- **Message Types** - أنواع الرسائل
  - Text messages
  - Image messages
  - File attachments
  - Location sharing
  - Product links (from marketplace)
  - Order links (from marketplace)

- **Real-time Features** - الميزات الفورية
  - Socket.IO WebSocket connection
  - Instant message delivery
  - Typing indicators
  - Online status updates

- **UI/UX**
  - Arabic/English bilingual support
  - SAHOOL green theme (#367C2B)
  - IBM Plex Sans Arabic font
  - Responsive design
  - Pull to refresh
  - Empty states

### 🚧 Future Enhancements | التحسينات المستقبلية

- Search conversations
- Voice messages
- Message reactions
- Message forwarding
- Delete messages
- Block users
- Report inappropriate content
- Push notifications for new messages
- Read receipts
- Message encryption

## Directory Structure | هيكل المجلدات

```
chat/
├── data/
│   ├── models/
│   │   ├── conversation_model.dart    # Conversation data model
│   │   └── message_model.dart         # Message data model
│   ├── remote/
│   │   └── chat_api.dart             # REST API + WebSocket client
│   └── repositories/
│       └── chat_repository.dart      # Data repository with caching
├── presentation/
│   ├── providers/
│   │   └── chat_provider.dart        # Riverpod state management
│   └── screens/
│       ├── conversations_screen.dart # List of conversations
│       └── chat_screen.dart          # Individual chat
└── widgets/
    ├── message_bubble.dart           # Message bubble widget
    ├── chat_input.dart               # Message input field
    └── conversation_tile.dart        # Conversation list item
```

## Installation | التثبيت

### 1. Install Dependencies | تثبيت التبعيات

The required dependencies have already been added to `pubspec.yaml`:

```yaml
dependencies:
  socket_io_client: ^2.0.3+1 # For WebSocket/Socket.IO
  flutter_riverpod: ^2.6.1 # State management
  intl: ^0.19.0 # Date formatting
```

Run the following command to install:

```bash
flutter pub get
```

### 2. Configure API Endpoint | إعداد نقطة الاتصال

The chat service is configured to run on port **3011** in `api_config.dart`:

```dart
static const int chat = 3011; // Chat/Messaging Service
```

For production, update the base URL in the configuration.

### 3. Initialize Chat Provider | تهيئة مزود المحادثات

In your app initialization, set the current user ID:

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/chat/presentation/providers/chat_provider.dart';

// In your app initialization or after login
ref.read(chatUserIdProvider.notifier).state = 'your-user-id';
```

## Usage | الاستخدام

### Opening Conversations Screen | فتح شاشة المحادثات

```dart
import 'package:flutter/material.dart';
import 'features/chat/presentation/screens/conversations_screen.dart';

// Navigate to conversations
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const ConversationsScreen(),
  ),
);
```

### Creating a New Conversation | إنشاء محادثة جديدة

```dart
// From marketplace product page
final conversation = await ref.read(chatProvider.notifier).createConversation(
  participantId: sellerId,
  productId: productId,
  initialMessage: 'مرحباً، أنا مهتم بهذا المنتج',
);

if (conversation != null) {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => ChatScreen(conversationId: conversation.id),
    ),
  );
}
```

### Getting Unread Count | الحصول على عدد الرسائل غير المقروءة

```dart
// Use in badge on bottom navigation or app bar
final unreadCount = ref.watch(unreadCountProvider);

if (unreadCount > 0) {
  // Show badge
}
```

## API Integration | تكامل الواجهة البرمجية

### REST Endpoints | نقاط REST

The chat feature connects to the following endpoints:

- `GET /api/v1/conversations` - Get all conversations
- `GET /api/v1/conversations/:id` - Get conversation by ID
- `GET /api/v1/conversations/:id/messages` - Get messages
- `POST /api/v1/conversations/:id/messages` - Send message
- `POST /api/v1/conversations` - Create conversation
- `PUT /api/v1/conversations/:id/read` - Mark as read
- `GET /api/v1/conversations/unread-count` - Get unread count

### Socket.IO Events | أحداث Socket.IO

**Emitting (Client → Server):**

- `join_conversation` - Join conversation room
- `leave_conversation` - Leave conversation room
- `typing` - User is typing
- `stop_typing` - User stopped typing
- `send_message` - Send message via socket

**Listening (Server → Client):**

- `message` - New message received
- `typing` - Other user is typing
- `stop_typing` - Other user stopped typing
- `user_online` - User came online
- `user_offline` - User went offline

## State Management | إدارة الحالة

The chat feature uses **Riverpod** for state management:

### Providers

- `chatProvider` - Main chat state (conversations, messages, etc.)
- `chatUserIdProvider` - Current user ID
- `unreadCountProvider` - Total unread count
- `activeConversationProvider` - Currently open conversation
- `activeMessagesProvider` - Messages for active conversation
- `activeConversationTypingProvider` - Typing status for active conversation

### State Structure

```dart
class ChatState {
  final List<Conversation> conversations;
  final Map<String, List<Message>> messagesMap;
  final String? activeConversationId;
  final Map<String, bool> typingStatus;
  final int unreadCount;
  final bool isLoading;
  final String? error;
}
```

## Theming | التصميم

The chat UI follows the SAHOOL brand guidelines:

- **Primary Color**: `#367C2B` (SAHOOL Green)
- **Sent Messages**: Green bubble with white text
- **Received Messages**: Gray bubble with black text
- **Font**: IBM Plex Sans Arabic
- **Border Radius**: 16px for bubbles
- **Spacing**: Consistent 16px padding

## Performance Optimizations | تحسينات الأداء

1. **Local Caching**: Conversations and messages are cached in memory
2. **Pagination**: Messages are loaded in batches (20 at a time)
3. **Optimistic Updates**: Messages appear immediately before server confirmation
4. **WebSocket**: Real-time updates without polling
5. **ListView.builder**: Efficient list rendering

## Testing | الاختبار

### Manual Testing Checklist

- [ ] Send text message
- [ ] Receive message in real-time
- [ ] See typing indicator
- [ ] See online status
- [ ] Pull to refresh conversations
- [ ] Load more messages (scroll to top)
- [ ] Mark conversation as read
- [ ] Create new conversation
- [ ] Handle network errors gracefully
- [ ] Test on both Android and iOS

### Integration with Backend

Make sure the chat service is running on port **3011**:

```bash
# In chat-service directory
npm run dev
```

## Troubleshooting | استكشاف الأخطاء

### Socket Connection Issues

If WebSocket fails to connect:

1. Check if chat service is running on port 3011
2. Verify network connectivity
3. Check firewall settings
4. For Android emulator, use `10.0.2.2` instead of `localhost`
5. For iOS simulator, `localhost` should work
6. For physical devices, use your computer's IP address

### Messages Not Appearing

1. Check if user ID is set correctly
2. Verify authentication token is valid
3. Check network requests in console
4. Ensure conversation is joined (Socket.IO room)

### Performance Issues

1. Clear cache if too many conversations
2. Reduce pagination limit
3. Optimize images (compress before upload)
4. Check for memory leaks

## Next Steps | الخطوات التالية

To integrate this feature into your app:

1. **Add to Navigation**: Add chat icon to bottom navigation or main menu
2. **Link from Marketplace**: Add "Message Seller" button on product pages
3. **Set User ID**: Initialize chat provider with user ID after login
4. **Configure Notifications**: Set up push notifications for new messages
5. **Test Thoroughly**: Test all scenarios before production

## Support | الدعم

For questions or issues:

- Check the code comments in each file
- Review the API documentation
- Test with the mock chat service first
- Consult the SAHOOL development team

---

**Version**: 1.0.0
**Last Updated**: 2025-12-25
**Author**: Claude Code
**License**: Proprietary (SAHOOL)
