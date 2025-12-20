/// SAHOOL Credit Tier Model
/// نموذج التصنيف الائتماني الموحد
///
/// يستخدم في:
/// - features/wallet/
/// - features/market/
/// - features/marketplace/

import 'package:flutter/material.dart';

/// تصنيف الائتمان
enum CreditTier {
  bronze('BRONZE', 'برونزي', Color(0xFFCD7F32)),
  silver('SILVER', 'فضي', Color(0xFFC0C0C0)),
  gold('GOLD', 'ذهبي', Color(0xFFFFD700)),
  platinum('PLATINUM', 'بلاتيني', Color(0xFFE5E4E2));

  final String value;
  final String arabicName;
  final Color color;

  const CreditTier(this.value, this.arabicName, this.color);

  /// الحصول على لون التصنيف كـ Hex String
  String get colorHex {
    return '#${color.value.toRadixString(16).substring(2).toUpperCase()}';
  }

  /// تحويل من نص إلى enum
  static CreditTier fromString(String? tier) {
    switch (tier?.toUpperCase()) {
      case 'PLATINUM':
        return CreditTier.platinum;
      case 'GOLD':
        return CreditTier.gold;
      case 'SILVER':
        return CreditTier.silver;
      default:
        return CreditTier.bronze;
    }
  }

  /// الحد الأدنى للتصنيف
  int get minScore {
    switch (this) {
      case CreditTier.bronze:
        return 300;
      case CreditTier.silver:
        return 500;
      case CreditTier.gold:
        return 650;
      case CreditTier.platinum:
        return 750;
    }
  }

  /// حد التمويل كنسبة مئوية
  double get loanLimitPercentage {
    switch (this) {
      case CreditTier.bronze:
        return 0.3; // 30%
      case CreditTier.silver:
        return 0.5; // 50%
      case CreditTier.gold:
        return 0.7; // 70%
      case CreditTier.platinum:
        return 1.0; // 100%
    }
  }
}
