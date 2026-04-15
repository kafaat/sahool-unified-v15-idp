/// SAHOOL CRM Feature
/// ميزة إدارة علاقات المزارعين في سهول
///
/// Farmer relationship management with profiles and interactions
/// إدارة علاقات المزارعين مع الملفات الشخصية والتفاعلات
library;

// Data
export 'data/crm_api.dart';
export 'data/crm_local_database.dart';
export 'data/crm_repository.dart';

// Domain
export 'domain/models/activity_log.dart';
export 'domain/models/farmer_profile.dart';
export 'domain/models/interaction.dart';
export 'domain/models/opportunity.dart';

// Presentation - Screens
export 'presentation/screens/add_interaction_screen.dart';
export 'presentation/screens/farmer_analytics_screen.dart';
export 'presentation/screens/farmer_profile_screen.dart';
export 'presentation/screens/farmers_list_screen.dart';
export 'presentation/screens/interaction_history_screen.dart';

// Presentation - Widgets
export 'presentation/widgets/activity_chart.dart';
export 'presentation/widgets/contact_actions.dart';
export 'presentation/widgets/farmer_card.dart';
export 'presentation/widgets/interaction_timeline.dart';

// State
export 'state/crm_controller.dart';
export 'state/crm_providers.dart';
