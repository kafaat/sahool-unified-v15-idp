/// SAHOOL Irrigation Feature
/// ميزة الري في سهول
///
/// Irrigation scheduling, dashboard, and water balance
/// جدولة الري ولوحة التحكم وميزان المياه
library;

// Data
export 'data/remote/irrigation_api.dart';
export 'data/repository/irrigation_repository.dart';

// Presentation
export 'presentation/providers/irrigation_provider.dart';
export 'presentation/screens/irrigation_dashboard_screen.dart';
export 'presentation/screens/irrigation_schedule_screen.dart';
export 'presentation/widgets/irrigation_method_selector.dart';
export 'presentation/widgets/water_balance_card.dart';
