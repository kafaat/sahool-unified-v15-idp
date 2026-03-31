import 'onboarding_step.dart';

/// SAHOOL Onboarding Progress Model
/// نموذج تقدم الإعداد الأولي
///
/// Tracks user progress through the onboarding flow
/// يتتبع تقدم المستخدم خلال تدفق الإعداد الأولي

/// User profile data collected during onboarding
/// بيانات الملف الشخصي المجمعة أثناء الإعداد
class OnboardingProfile {
  /// User's name
  final String? userName;

  /// Farm name
  final String? farmName;

  /// User's phone number (already collected during login)
  final String? phoneNumber;

  /// Profile image path (optional)
  final String? profileImagePath;

  const OnboardingProfile({
    this.userName,
    this.farmName,
    this.phoneNumber,
    this.profileImagePath,
  });

  /// Check if profile is complete
  bool get isComplete => userName != null && userName!.isNotEmpty;

  /// Create a copy with updated values
  OnboardingProfile copyWith({
    String? userName,
    String? farmName,
    String? phoneNumber,
    String? profileImagePath,
  }) {
    return OnboardingProfile(
      userName: userName ?? this.userName,
      farmName: farmName ?? this.farmName,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      profileImagePath: profileImagePath ?? this.profileImagePath,
    );
  }

  /// Convert to JSON for storage
  Map<String, dynamic> toJson() {
    return {
      'userName': userName,
      'farmName': farmName,
      'phoneNumber': phoneNumber,
      'profileImagePath': profileImagePath,
    };
  }

  /// Create from JSON
  factory OnboardingProfile.fromJson(Map<String, dynamic> json) {
    return OnboardingProfile(
      userName: json['userName'] as String?,
      farmName: json['farmName'] as String?,
      phoneNumber: json['phoneNumber'] as String?,
      profileImagePath: json['profileImagePath'] as String?,
    );
  }
}

/// First field data collected during onboarding
/// بيانات الحقل الأول المجمعة أثناء الإعداد
class OnboardingFirstField {
  /// Field name
  final String? fieldName;

  /// Crop type
  final String? cropType;

  /// Area in hectares (optional)
  final double? areaHectares;

  /// Field created successfully
  final bool isCreated;

  /// Whether user skipped this step
  final bool isSkipped;

  const OnboardingFirstField({
    this.fieldName,
    this.cropType,
    this.areaHectares,
    this.isCreated = false,
    this.isSkipped = false,
  });

  /// Create a copy with updated values
  OnboardingFirstField copyWith({
    String? fieldName,
    String? cropType,
    double? areaHectares,
    bool? isCreated,
    bool? isSkipped,
  }) {
    return OnboardingFirstField(
      fieldName: fieldName ?? this.fieldName,
      cropType: cropType ?? this.cropType,
      areaHectares: areaHectares ?? this.areaHectares,
      isCreated: isCreated ?? this.isCreated,
      isSkipped: isSkipped ?? this.isSkipped,
    );
  }

  /// Convert to JSON for storage
  Map<String, dynamic> toJson() {
    return {
      'fieldName': fieldName,
      'cropType': cropType,
      'areaHectares': areaHectares,
      'isCreated': isCreated,
      'isSkipped': isSkipped,
    };
  }

  /// Create from JSON
  factory OnboardingFirstField.fromJson(Map<String, dynamic> json) {
    return OnboardingFirstField(
      fieldName: json['fieldName'] as String?,
      cropType: json['cropType'] as String?,
      areaHectares: json['areaHectares'] as double?,
      isCreated: json['isCreated'] as bool? ?? false,
      isSkipped: json['isSkipped'] as bool? ?? false,
    );
  }
}

/// Complete onboarding progress state
/// حالة تقدم الإعداد الكاملة
class OnboardingProgress {
  /// Current step in the onboarding flow
  final OnboardingStepType currentStep;

  /// Current page index in the features tour
  final int featuresTourPage;

  /// Total pages in features tour
  static const int totalFeaturesTourPages = 5;

  /// Profile data
  final OnboardingProfile profile;

  /// First field data
  final OnboardingFirstField firstField;

  /// Permission states
  final Map<String, bool> permissionStates;

  /// Whether onboarding has been completed
  final bool isCompleted;

  /// Whether onboarding was skipped
  final bool wasSkipped;

  /// Timestamp when onboarding was completed
  final DateTime? completedAt;

  const OnboardingProgress({
    this.currentStep = OnboardingStepType.welcome,
    this.featuresTourPage = 0,
    this.profile = const OnboardingProfile(),
    this.firstField = const OnboardingFirstField(),
    this.permissionStates = const {},
    this.isCompleted = false,
    this.wasSkipped = false,
    this.completedAt,
  });

  /// Calculate overall progress percentage
  double get progressPercentage {
    const totalSteps = 6; // Total number of onboarding steps
    int currentStepIndex;

    switch (currentStep) {
      case OnboardingStepType.welcome:
        currentStepIndex = 0;
        break;
      case OnboardingStepType.featuresTour:
        // Calculate partial progress through features tour
        currentStepIndex = 1;
        final tourProgress = featuresTourPage / totalFeaturesTourPages;
        return ((currentStepIndex + tourProgress) / totalSteps) * 100;
      case OnboardingStepType.permissions:
        currentStepIndex = 2;
        break;
      case OnboardingStepType.profileSetup:
        currentStepIndex = 3;
        break;
      case OnboardingStepType.firstField:
        currentStepIndex = 4;
        break;
      case OnboardingStepType.completion:
        currentStepIndex = 5;
        break;
    }

    return (currentStepIndex / totalSteps) * 100;
  }

  /// Get step number for display
  int get currentStepNumber {
    switch (currentStep) {
      case OnboardingStepType.welcome:
        return 1;
      case OnboardingStepType.featuresTour:
        return 2;
      case OnboardingStepType.permissions:
        return 3;
      case OnboardingStepType.profileSetup:
        return 4;
      case OnboardingStepType.firstField:
        return 5;
      case OnboardingStepType.completion:
        return 6;
    }
  }

  /// Check if all required permissions are granted
  bool get allRequiredPermissionsGranted {
    for (final permission in OnboardingPermissions.permissions) {
      if (permission.isRequired) {
        if (permissionStates[permission.id] != true) {
          return false;
        }
      }
    }
    return true;
  }

  /// Create a copy with updated values
  OnboardingProgress copyWith({
    OnboardingStepType? currentStep,
    int? featuresTourPage,
    OnboardingProfile? profile,
    OnboardingFirstField? firstField,
    Map<String, bool>? permissionStates,
    bool? isCompleted,
    bool? wasSkipped,
    DateTime? completedAt,
  }) {
    return OnboardingProgress(
      currentStep: currentStep ?? this.currentStep,
      featuresTourPage: featuresTourPage ?? this.featuresTourPage,
      profile: profile ?? this.profile,
      firstField: firstField ?? this.firstField,
      permissionStates: permissionStates ?? this.permissionStates,
      isCompleted: isCompleted ?? this.isCompleted,
      wasSkipped: wasSkipped ?? this.wasSkipped,
      completedAt: completedAt ?? this.completedAt,
    );
  }

  /// Convert to JSON for storage
  Map<String, dynamic> toJson() {
    return {
      'currentStep': currentStep.name,
      'featuresTourPage': featuresTourPage,
      'profile': profile.toJson(),
      'firstField': firstField.toJson(),
      'permissionStates': permissionStates,
      'isCompleted': isCompleted,
      'wasSkipped': wasSkipped,
      'completedAt': completedAt?.toIso8601String(),
    };
  }

  /// Create from JSON
  factory OnboardingProgress.fromJson(Map<String, dynamic> json) {
    return OnboardingProgress(
      currentStep: OnboardingStepType.values.firstWhere(
        (e) => e.name == json['currentStep'],
        orElse: () => OnboardingStepType.welcome,
      ),
      featuresTourPage: json['featuresTourPage'] as int? ?? 0,
      profile: json['profile'] != null
          ? OnboardingProfile.fromJson(json['profile'] as Map<String, dynamic>)
          : const OnboardingProfile(),
      firstField: json['firstField'] != null
          ? OnboardingFirstField.fromJson(
              json['firstField'] as Map<String, dynamic>)
          : const OnboardingFirstField(),
      permissionStates:
          Map<String, bool>.from(json['permissionStates'] as Map? ?? {}),
      isCompleted: json['isCompleted'] as bool? ?? false,
      wasSkipped: json['wasSkipped'] as bool? ?? false,
      completedAt: json['completedAt'] != null
          ? DateTime.tryParse(json['completedAt'] as String) ?? DateTime.now()
          : null,
    );
  }
}
