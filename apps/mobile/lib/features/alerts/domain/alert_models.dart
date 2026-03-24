/// Alert domain models
/// نماذج مجال التنبيهات

import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';

/// Alert type enum with associated icon and color
/// نوع التنبيه مع الأيقونة واللون المرتبطين
enum AlertType {
  info(Icons.info, SahoolColors.info),
  warning(Icons.warning_amber, SahoolColors.warning),
  danger(Icons.error, SahoolColors.danger),
  success(Icons.check_circle, SahoolColors.success);

  final IconData icon;
  final Color color;

  const AlertType(this.icon, this.color);
}
