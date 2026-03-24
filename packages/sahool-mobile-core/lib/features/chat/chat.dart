/// SAHOOL Chat Feature
/// ميزة المحادثة في سهول
///
/// Real-time messaging with location sharing
/// المراسلة الفورية مع مشاركة الموقع
library;

// Data
export 'data/models/conversation_model.dart';
export 'data/models/message_model.dart';
export 'data/remote/chat_api.dart';
export 'data/repositories/chat_repository.dart';

// Presentation
export 'presentation/providers/chat_provider.dart';
export 'presentation/screens/chat_screen.dart';
export 'presentation/screens/conversations_screen.dart';

// Widgets
export 'widgets/chat_input.dart';
export 'widgets/conversation_tile.dart';
export 'widgets/location_picker.dart';
export 'widgets/message_bubble.dart';
