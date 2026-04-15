/// SAHOOL Tasks Feature
/// ميزة المهام في سهول
///
/// Task management with creation, details, and astronomical integration
/// إدارة المهام مع الإنشاء والتفاصيل والتكامل الفلكي
library;

// Data
export 'data/remote/tasks_api.dart';
export 'data/repo/tasks_repo.dart';

// Domain
export 'domain/entities/field_task.dart';
export 'domain/entities/task.dart';

// Presentation - Screens
export 'presentation/complete_task_screen.dart';
export 'presentation/create_task_screen.dart';
export 'presentation/task_details_screen.dart';
export 'presentation/tasks_list_screen.dart';

// Presentation - Widgets
export 'presentation/widgets/astronomical_task_widget.dart';
export 'presentation/widgets/task_card.dart';

// Providers
export 'providers/tasks_provider.dart';

// UI
export 'ui/tasks_screen.dart';
export 'ui/widgets/daily_tasks_sheet.dart';
export 'ui/widgets/task_tile.dart';
