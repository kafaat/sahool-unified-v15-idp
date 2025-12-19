/// SAHOOL Conflict Resolution Policy
/// سياسة حل التعارضات

enum ConflictResolution {
  serverWins,
  clientWins,
  mergeIfPossible,
}

class ConflictPolicy {
  ConflictResolution forCommandType(String type) {
    // تحديثات الحقل: محاولة الدمج
    if (type.startsWith('field.')) {
      return ConflictResolution.mergeIfPossible;
    }

    // التدقيق/السجلات: العميل يربح دائمًا (إضافة فقط)
    if (type.startsWith('audit.') || type.startsWith('log.')) {
      return ConflictResolution.clientWins;
    }

    // الحذف: الخادم يربح
    if (type.contains('.delete')) {
      return ConflictResolution.serverWins;
    }

    // الإنشاء: محاولة الدمج
    if (type.contains('.create')) {
      return ConflictResolution.mergeIfPossible;
    }

    // الافتراضي: الخادم يربح
    return ConflictResolution.serverWins;
  }

  bool shouldRetry(String type, int retryCount) {
    // لا إعادة محاولة للحذف
    if (type.contains('.delete') && retryCount > 0) {
      return false;
    }

    // الحد الأقصى للمحاولات
    return retryCount < 3;
  }
}
