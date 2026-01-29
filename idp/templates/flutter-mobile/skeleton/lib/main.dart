/// ${{ values.name }} - SAHOOL Mobile Module
/// ${{ values.description }}
/// ${{ values.description_ar }}
///
/// Layer: ${{ values.layer }}
/// Owner: ${{ values.owner }}
/// Team: ${{ values.team }}

library ${{ values.name }};

// Exports
export 'src/providers/providers.dart';
export 'src/models/models.dart';
{%- if values.has_api_integration %}
export 'src/services/api_service.dart';
{%- endif %}
{%- if values.has_offline_support %}
export 'src/database/database.dart';
{%- endif %}
export 'src/screens/screens.dart';
export 'src/widgets/widgets.dart';
