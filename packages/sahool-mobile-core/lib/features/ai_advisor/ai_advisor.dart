/// SAHOOL AI Advisor Feature
/// ميزة المستشار الذكي في سهول
///
/// AI-powered agricultural advisory with chat interface
/// استشارات زراعية مدعومة بالذكاء الاصطناعي
library;

// Data
export 'data/cache/advisory_cache.dart';
export 'data/remote/ai_advisor_api.dart';
export 'data/repositories/ai_advisor_repository.dart';

// Domain
export 'domain/models/advisory.dart';
export 'domain/models/advisory_context.dart';
export 'domain/models/advisory_feedback.dart';
export 'domain/models/advisory_request.dart';

// Presentation - Screens
export 'presentation/screens/advisory_details_screen.dart';
export 'presentation/screens/advisory_history_screen.dart';
export 'presentation/screens/ai_advisor_screen.dart';

// Presentation - Widgets
export 'presentation/widgets/advisory_card.dart';
export 'presentation/widgets/chat_bubble.dart';
export 'presentation/widgets/context_indicator.dart';
export 'presentation/widgets/feedback_buttons.dart';
export 'presentation/widgets/quick_question_chips.dart';
export 'presentation/widgets/typing_indicator.dart';

// State
export 'state/ai_advisor_providers.dart';
export 'state/chat_controller.dart';
