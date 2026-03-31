/// SAHOOL Version Comparator
/// مقارن الإصدارات
///
/// Provides semantic version parsing and comparison utilities
/// for determining if app updates are available.
library;

/// Represents a semantic version with major.minor.patch format
/// يمثل إصدار دلالي بصيغة رئيسي.ثانوي.تصحيحي
class SemanticVersion implements Comparable<SemanticVersion> {
  final int major;
  final int minor;
  final int patch;
  final String? preRelease;
  final String? buildMetadata;

  const SemanticVersion({
    required this.major,
    required this.minor,
    required this.patch,
    this.preRelease,
    this.buildMetadata,
  });

  /// Parse version string like "16.0.0", "1.2.3-beta", "1.2.3+build123"
  /// تحليل نص الإصدار
  factory SemanticVersion.parse(String version) {
    // Remove 'v' prefix if present
    var cleanVersion = version.trim();
    if (cleanVersion.startsWith('v') || cleanVersion.startsWith('V')) {
      cleanVersion = cleanVersion.substring(1);
    }

    // Extract build metadata (+)
    String? buildMetadata;
    final buildSplit = cleanVersion.split('+');
    if (buildSplit.length > 1) {
      buildMetadata = buildSplit.sublist(1).join('+');
      cleanVersion = buildSplit[0];
    }

    // Extract pre-release (-)
    String? preRelease;
    final preReleaseSplit = cleanVersion.split('-');
    if (preReleaseSplit.length > 1) {
      preRelease = preReleaseSplit.sublist(1).join('-');
      cleanVersion = preReleaseSplit[0];
    }

    // Parse major.minor.patch
    final parts = cleanVersion.split('.');
    if (parts.isEmpty) {
      throw FormatException('Invalid version format: $version');
    }

    final major = int.tryParse(parts[0]) ?? 0;
    final minor = parts.length > 1 ? (int.tryParse(parts[1]) ?? 0) : 0;
    final patch = parts.length > 2 ? (int.tryParse(parts[2]) ?? 0) : 0;

    return SemanticVersion(
      major: major,
      minor: minor,
      patch: patch,
      preRelease: preRelease,
      buildMetadata: buildMetadata,
    );
  }

  /// Try to parse a version string, returning null if invalid
  /// محاولة تحليل نص الإصدار مع إرجاع null في حالة الفشل
  static SemanticVersion? tryParse(String version) {
    try {
      return SemanticVersion.parse(version);
    } catch (e) {
      return null;
    }
  }

  /// Returns the version as a string
  /// إرجاع الإصدار كنص
  @override
  String toString() {
    var result = '$major.$minor.$patch';
    if (preRelease != null) {
      result += '-$preRelease';
    }
    if (buildMetadata != null) {
      result += '+$buildMetadata';
    }
    return result;
  }

  /// Returns short version string (major.minor.patch)
  /// إرجاع نص الإصدار المختصر
  String toShortString() => '$major.$minor.$patch';

  @override
  int compareTo(SemanticVersion other) {
    // Compare major version
    if (major != other.major) {
      return major.compareTo(other.major);
    }

    // Compare minor version
    if (minor != other.minor) {
      return minor.compareTo(other.minor);
    }

    // Compare patch version
    if (patch != other.patch) {
      return patch.compareTo(other.patch);
    }

    // Pre-release versions have lower precedence than normal versions
    // 1.0.0-alpha < 1.0.0
    if (preRelease != null && other.preRelease == null) {
      return -1;
    }
    if (preRelease == null && other.preRelease != null) {
      return 1;
    }
    if (preRelease != null && other.preRelease != null) {
      return preRelease!.compareTo(other.preRelease!);
    }

    return 0;
  }

  @override
  bool operator ==(Object other) =>
      other is SemanticVersion &&
      major == other.major &&
      minor == other.minor &&
      patch == other.patch &&
      preRelease == other.preRelease;

  @override
  int get hashCode => Object.hash(major, minor, patch, preRelease);

  bool operator <(SemanticVersion other) => compareTo(other) < 0;
  bool operator <=(SemanticVersion other) => compareTo(other) <= 0;
  bool operator >(SemanticVersion other) => compareTo(other) > 0;
  bool operator >=(SemanticVersion other) => compareTo(other) >= 0;
}

/// Type of update available
/// نوع التحديث المتاح
enum UpdateType {
  /// No update needed
  /// لا يوجد تحديث
  none,

  /// Patch update (bug fixes) - optional
  /// تحديث تصحيحي (إصلاح أخطاء) - اختياري
  patch,

  /// Minor update (new features) - optional
  /// تحديث ثانوي (ميزات جديدة) - اختياري
  minor,

  /// Major update (breaking changes) - force update
  /// تحديث رئيسي (تغييرات جذرية) - تحديث إجباري
  major,
}

/// Version comparison utility class
/// فئة أدوات مقارنة الإصدارات
class VersionComparator {
  /// Compare two versions and return the update type needed
  /// مقارنة إصدارين وإرجاع نوع التحديث المطلوب
  static UpdateType compareVersions(
    SemanticVersion current,
    SemanticVersion latest,
  ) {
    if (latest <= current) {
      return UpdateType.none;
    }

    if (latest.major > current.major) {
      return UpdateType.major;
    }

    if (latest.minor > current.minor) {
      return UpdateType.minor;
    }

    if (latest.patch > current.patch) {
      return UpdateType.patch;
    }

    return UpdateType.none;
  }

  /// Check if a forced update is required based on minimum version
  /// التحقق مما إذا كان التحديث الإجباري مطلوبًا بناءً على الحد الأدنى للإصدار
  static bool isForceUpdateRequired(
    SemanticVersion current,
    SemanticVersion minimumRequired,
  ) {
    return current < minimumRequired;
  }

  /// Check if the current version meets the minimum requirement
  /// التحقق مما إذا كان الإصدار الحالي يلبي الحد الأدنى المطلوب
  static bool meetsMinimumVersion(
    SemanticVersion current,
    SemanticVersion minimum,
  ) {
    return current >= minimum;
  }

  /// Calculate version difference description
  /// حساب وصف الفرق بين الإصدارات
  static String getVersionDifferenceDescription(
    SemanticVersion current,
    SemanticVersion latest, {
    bool arabic = false,
  }) {
    final updateType = compareVersions(current, latest);

    switch (updateType) {
      case UpdateType.none:
        return arabic ? 'التطبيق محدث' : 'App is up to date';
      case UpdateType.patch:
        return arabic
            ? 'تحديث تصحيحي متاح (إصلاحات أخطاء)'
            : 'Patch update available (bug fixes)';
      case UpdateType.minor:
        return arabic
            ? 'تحديث ثانوي متاح (ميزات جديدة)'
            : 'Minor update available (new features)';
      case UpdateType.major:
        return arabic
            ? 'تحديث رئيسي متاح (تحسينات كبيرة)'
            : 'Major update available (major improvements)';
    }
  }
}
