/// Chart Configuration Models - نماذج تكوين الرسوم البيانية
/// Configuration for various chart types used in reports
library;

/// Chart type enum - أنواع الرسوم البيانية
enum ChartType {
  /// Line chart - رسم بياني خطي
  line,

  /// Bar chart - رسم بياني شريطي
  bar,

  /// Pie chart - رسم دائري
  pie,

  /// Area chart - رسم بياني مساحي
  area,

  /// Doughnut chart - رسم حلقي
  doughnut,

  /// Scatter chart - رسم بياني نقطي
  scatter,

  /// Radar chart - رسم راداري
  radar,

  /// Stacked bar chart - رسم شريطي متراكم
  stackedBar,

  /// Combined chart (line + bar) - رسم مدمج
  combined,
}

/// Chart legend position - موضع الأسطورة
enum LegendPosition {
  top,
  bottom,
  left,
  right,
  none,
}

/// Chart data point - نقطة بيانات
class ChartDataPoint {
  /// X value (can be DateTime, String, or number)
  final dynamic x;

  /// Y value
  final double y;

  /// Label (optional)
  final String? label;

  /// Label (Arabic)
  final String? labelAr;

  /// Color hex (optional)
  final String? colorHex;

  const ChartDataPoint({
    required this.x,
    required this.y,
    this.label,
    this.labelAr,
    this.colorHex,
  });

  factory ChartDataPoint.fromJson(Map<String, dynamic> json) {
    return ChartDataPoint(
      x: json['x'],
      y: (json['y'] as num).toDouble(),
      label: json['label'] as String?,
      labelAr: json['label_ar'] as String?,
      colorHex: json['color_hex'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'x': x is DateTime ? (x as DateTime).toIso8601String() : x,
        'y': y,
        'label': label,
        'label_ar': labelAr,
        'color_hex': colorHex,
      };
}

/// Chart data series - سلسلة بيانات
class ChartDataSeries {
  /// Series ID
  final String id;

  /// Series name (English)
  final String name;

  /// Series name (Arabic)
  final String nameAr;

  /// Data points
  final List<ChartDataPoint> dataPoints;

  /// Series color hex
  final String colorHex;

  /// Is dashed line (for line charts)
  final bool isDashed;

  /// Fill area (for line/area charts)
  final bool fillArea;

  /// Stack group (for stacked charts)
  final String? stackGroup;

  const ChartDataSeries({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.dataPoints,
    required this.colorHex,
    this.isDashed = false,
    this.fillArea = false,
    this.stackGroup,
  });

  factory ChartDataSeries.fromJson(Map<String, dynamic> json) {
    return ChartDataSeries(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String? ?? json['name'] as String,
      dataPoints: (json['data_points'] as List<dynamic>)
          .map((e) => ChartDataPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      colorHex: json['color_hex'] as String? ?? '#1B5E20',
      isDashed: json['is_dashed'] as bool? ?? false,
      fillArea: json['fill_area'] as bool? ?? false,
      stackGroup: json['stack_group'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'name_ar': nameAr,
        'data_points': dataPoints.map((p) => p.toJson()).toList(),
        'color_hex': colorHex,
        'is_dashed': isDashed,
        'fill_area': fillArea,
        'stack_group': stackGroup,
      };
}

/// Axis configuration - تكوين المحور
class AxisConfig {
  /// Axis title (English)
  final String? title;

  /// Axis title (Arabic)
  final String? titleAr;

  /// Minimum value
  final double? min;

  /// Maximum value
  final double? max;

  /// Interval
  final double? interval;

  /// Show grid lines
  final bool showGridLines;

  /// Format pattern (e.g., "#,##0.0", "MM/dd")
  final String? formatPattern;

  /// Unit label
  final String? unit;

  const AxisConfig({
    this.title,
    this.titleAr,
    this.min,
    this.max,
    this.interval,
    this.showGridLines = true,
    this.formatPattern,
    this.unit,
  });

  factory AxisConfig.fromJson(Map<String, dynamic> json) {
    return AxisConfig(
      title: json['title'] as String?,
      titleAr: json['title_ar'] as String?,
      min: (json['min'] as num?)?.toDouble(),
      max: (json['max'] as num?)?.toDouble(),
      interval: (json['interval'] as num?)?.toDouble(),
      showGridLines: json['show_grid_lines'] as bool? ?? true,
      formatPattern: json['format_pattern'] as String?,
      unit: json['unit'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'title': title,
        'title_ar': titleAr,
        'min': min,
        'max': max,
        'interval': interval,
        'show_grid_lines': showGridLines,
        'format_pattern': formatPattern,
        'unit': unit,
      };
}

/// Chart configuration model - نموذج تكوين الرسم البياني
class ChartConfig {
  /// Chart type
  final ChartType type;

  /// Chart title (English)
  final String title;

  /// Chart title (Arabic)
  final String titleAr;

  /// Chart subtitle (optional)
  final String? subtitle;

  /// Chart subtitle (Arabic)
  final String? subtitleAr;

  /// Data series
  final List<ChartDataSeries> series;

  /// X axis configuration
  final AxisConfig? xAxis;

  /// Y axis configuration
  final AxisConfig? yAxis;

  /// Secondary Y axis (for combined charts)
  final AxisConfig? secondaryYAxis;

  /// Legend position
  final LegendPosition legendPosition;

  /// Show legend
  final bool showLegend;

  /// Show tooltips
  final bool showTooltips;

  /// Enable animations
  final bool enableAnimations;

  /// Animation duration in ms
  final int animationDuration;

  /// Chart aspect ratio
  final double aspectRatio;

  /// Background color hex
  final String? backgroundColorHex;

  /// Custom color palette
  final List<String> colorPalette;

  /// Show data labels
  final bool showDataLabels;

  /// Is interactive (allows tapping on chart)
  final bool isInteractive;

  const ChartConfig({
    required this.type,
    required this.title,
    required this.titleAr,
    this.subtitle,
    this.subtitleAr,
    this.series = const [],
    this.xAxis,
    this.yAxis,
    this.secondaryYAxis,
    this.legendPosition = LegendPosition.bottom,
    this.showLegend = true,
    this.showTooltips = true,
    this.enableAnimations = true,
    this.animationDuration = 300,
    this.aspectRatio = 1.7,
    this.backgroundColorHex,
    this.colorPalette = const [],
    this.showDataLabels = false,
    this.isInteractive = true,
  });

  /// Has data
  bool get hasData => series.any((s) => s.dataPoints.isNotEmpty);

  /// Total data points
  int get totalDataPoints =>
      series.fold(0, (sum, s) => sum + s.dataPoints.length);

  factory ChartConfig.fromJson(Map<String, dynamic> json) {
    return ChartConfig(
      type: ChartType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => ChartType.line,
      ),
      title: json['title'] as String,
      titleAr: json['title_ar'] as String? ?? json['title'] as String,
      subtitle: json['subtitle'] as String?,
      subtitleAr: json['subtitle_ar'] as String?,
      series: (json['series'] as List<dynamic>?)
              ?.map((e) => ChartDataSeries.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      xAxis: json['x_axis'] != null
          ? AxisConfig.fromJson(json['x_axis'] as Map<String, dynamic>)
          : null,
      yAxis: json['y_axis'] != null
          ? AxisConfig.fromJson(json['y_axis'] as Map<String, dynamic>)
          : null,
      secondaryYAxis: json['secondary_y_axis'] != null
          ? AxisConfig.fromJson(json['secondary_y_axis'] as Map<String, dynamic>)
          : null,
      legendPosition: LegendPosition.values.firstWhere(
        (e) => e.name == json['legend_position'],
        orElse: () => LegendPosition.bottom,
      ),
      showLegend: json['show_legend'] as bool? ?? true,
      showTooltips: json['show_tooltips'] as bool? ?? true,
      enableAnimations: json['enable_animations'] as bool? ?? true,
      animationDuration: json['animation_duration'] as int? ?? 300,
      aspectRatio: (json['aspect_ratio'] as num?)?.toDouble() ?? 1.7,
      backgroundColorHex: json['background_color_hex'] as String?,
      colorPalette: (json['color_palette'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      showDataLabels: json['show_data_labels'] as bool? ?? false,
      isInteractive: json['is_interactive'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'type': type.name,
        'title': title,
        'title_ar': titleAr,
        'subtitle': subtitle,
        'subtitle_ar': subtitleAr,
        'series': series.map((s) => s.toJson()).toList(),
        'x_axis': xAxis?.toJson(),
        'y_axis': yAxis?.toJson(),
        'secondary_y_axis': secondaryYAxis?.toJson(),
        'legend_position': legendPosition.name,
        'show_legend': showLegend,
        'show_tooltips': showTooltips,
        'enable_animations': enableAnimations,
        'animation_duration': animationDuration,
        'aspect_ratio': aspectRatio,
        'background_color_hex': backgroundColorHex,
        'color_palette': colorPalette,
        'show_data_labels': showDataLabels,
        'is_interactive': isInteractive,
      };

  ChartConfig copyWith({
    ChartType? type,
    String? title,
    String? titleAr,
    String? subtitle,
    String? subtitleAr,
    List<ChartDataSeries>? series,
    AxisConfig? xAxis,
    AxisConfig? yAxis,
    AxisConfig? secondaryYAxis,
    LegendPosition? legendPosition,
    bool? showLegend,
    bool? showTooltips,
    bool? enableAnimations,
    int? animationDuration,
    double? aspectRatio,
    String? backgroundColorHex,
    List<String>? colorPalette,
    bool? showDataLabels,
    bool? isInteractive,
  }) {
    return ChartConfig(
      type: type ?? this.type,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      subtitle: subtitle ?? this.subtitle,
      subtitleAr: subtitleAr ?? this.subtitleAr,
      series: series ?? this.series,
      xAxis: xAxis ?? this.xAxis,
      yAxis: yAxis ?? this.yAxis,
      secondaryYAxis: secondaryYAxis ?? this.secondaryYAxis,
      legendPosition: legendPosition ?? this.legendPosition,
      showLegend: showLegend ?? this.showLegend,
      showTooltips: showTooltips ?? this.showTooltips,
      enableAnimations: enableAnimations ?? this.enableAnimations,
      animationDuration: animationDuration ?? this.animationDuration,
      aspectRatio: aspectRatio ?? this.aspectRatio,
      backgroundColorHex: backgroundColorHex ?? this.backgroundColorHex,
      colorPalette: colorPalette ?? this.colorPalette,
      showDataLabels: showDataLabels ?? this.showDataLabels,
      isInteractive: isInteractive ?? this.isInteractive,
    );
  }
}

/// Default chart color palettes - لوحات الألوان الافتراضية
class ChartColorPalettes {
  /// SAHOOL theme colors
  static const sahool = [
    '#1B5E20', // Primary green
    '#4CAF50', // Secondary green
    '#367C2B', // SAHOOL green
    '#D4A84B', // Harvest gold
    '#87A878', // Sage green
    '#8B7355', // Earth brown
  ];

  /// Agriculture themed
  static const agriculture = [
    '#2E7D32', // Green
    '#FF8F00', // Amber
    '#1565C0', // Blue
    '#6A1B9A', // Purple
    '#C62828', // Red
    '#00695C', // Teal
  ];

  /// Pastel colors
  static const pastel = [
    '#A5D6A7', // Light green
    '#81D4FA', // Light blue
    '#F8BBD0', // Light pink
    '#FFE082', // Light amber
    '#B39DDB', // Light purple
    '#80CBC4', // Light teal
  ];

  /// Monochrome green
  static const monochromeGreen = [
    '#1B5E20',
    '#2E7D32',
    '#388E3C',
    '#43A047',
    '#4CAF50',
    '#66BB6A',
    '#81C784',
    '#A5D6A7',
  ];

  /// Status colors
  static const status = [
    '#2E7D32', // Success
    '#FF8F00', // Warning
    '#C62828', // Error
    '#1565C0', // Info
    '#757575', // Neutral
  ];
}
