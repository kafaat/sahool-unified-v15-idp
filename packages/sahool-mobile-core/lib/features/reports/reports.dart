/// SAHOOL Reports Feature
/// ميزة التقارير في سهول
///
/// Report builder, viewer, and sharing
/// منشئ التقارير والعارض والمشاركة
library;

// Data
export 'data/report_generator.dart';
export 'data/reports_api.dart';
export 'data/reports_repository.dart';

// Domain
export 'domain/models/chart_config.dart';
export 'domain/models/report_data.dart';
export 'domain/models/report_filter.dart';
export 'domain/models/report_template.dart';

// Presentation - Screens
export 'presentation/screens/report_builder_screen.dart';
export 'presentation/screens/report_share_screen.dart';
export 'presentation/screens/report_viewer_screen.dart';
export 'presentation/screens/reports_dashboard_screen.dart';

// Presentation - Widgets
export 'presentation/widgets/chart_widget.dart';
export 'presentation/widgets/date_range_picker_widget.dart';
export 'presentation/widgets/export_button.dart';
export 'presentation/widgets/filter_chips_widget.dart';
export 'presentation/widgets/report_card.dart';
export 'presentation/widgets/report_data_table.dart';

// State
export 'state/report_builder_controller.dart';
export 'state/reports_providers.dart';
