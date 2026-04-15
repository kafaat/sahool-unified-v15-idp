/// Profile Provider - User Profile State Management
/// موفر الملف الشخصي - إدارة حالة ملف المستخدم
library;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/profile_repository.dart';

/// User profile state
/// حالة الملف الشخصي
class ProfileState {
  final String userId;
  final String userName;
  final String userNameAr;
  final String email;
  final String phone;
  final String? avatarUrl;
  final String farmName;
  final String farmNameAr;
  final double farmAreaHectares;
  final String location;
  final String language; // 'ar' | 'en'
  final int fieldsCount;
  final int tasksCompleted;
  final int achievementsCount;
  final bool isLoading;
  final String? error;

  const ProfileState({
    this.userId = '',
    this.userName = '',
    this.userNameAr = '',
    this.email = '',
    this.phone = '',
    this.avatarUrl,
    this.farmName = '',
    this.farmNameAr = '',
    this.farmAreaHectares = 0,
    this.location = '',
    this.language = 'ar',
    this.fieldsCount = 0,
    this.tasksCompleted = 0,
    this.achievementsCount = 0,
    this.isLoading = false,
    this.error,
  });

  ProfileState copyWith({
    String? userId,
    String? userName,
    String? userNameAr,
    String? email,
    String? phone,
    String? avatarUrl,
    String? farmName,
    String? farmNameAr,
    double? farmAreaHectares,
    String? location,
    String? language,
    int? fieldsCount,
    int? tasksCompleted,
    int? achievementsCount,
    bool? isLoading,
    String? error,
  }) {
    return ProfileState(
      userId: userId ?? this.userId,
      userName: userName ?? this.userName,
      userNameAr: userNameAr ?? this.userNameAr,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      farmName: farmName ?? this.farmName,
      farmNameAr: farmNameAr ?? this.farmNameAr,
      farmAreaHectares: farmAreaHectares ?? this.farmAreaHectares,
      location: location ?? this.location,
      language: language ?? this.language,
      fieldsCount: fieldsCount ?? this.fieldsCount,
      tasksCompleted: tasksCompleted ?? this.tasksCompleted,
      achievementsCount: achievementsCount ?? this.achievementsCount,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Profile state notifier
/// مُعلم حالة الملف الشخصي
class ProfileNotifier extends StateNotifier<ProfileState> {
  final ProfileRepository _repo;

  ProfileNotifier(this._repo) : super(const ProfileState()) {
    loadProfile();
  }

  /// Load user profile from user-service (GET /api/v1/users/me)
  /// تحميل ملف المستخدم من الخادم
  Future<void> loadProfile() async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _repo.getMe();
    result.when(
      success: (profile) {
        state = profile.copyWith(isLoading: false);
      },
      failure: (message, statusCode) {
        state = state.copyWith(isLoading: false, error: message);
      },
    );
  }

  /// Update profile fields via user-service (PATCH /api/v1/users/me)
  /// تحديث حقول الملف الشخصي
  Future<void> updateProfile({
    String? userName,
    String? phone,
    String? farmName,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _repo.updateMe(
      userName: userName,
      phone: phone,
      farmName: farmName,
    );
    result.when(
      success: (profile) {
        state = profile.copyWith(isLoading: false);
      },
      failure: (message, statusCode) {
        state = state.copyWith(isLoading: false, error: message);
      },
    );
  }

  /// Upload avatar image via user-service (POST /api/v1/users/me/avatar)
  /// رفع صورة الملف الشخصي
  Future<void> uploadAvatar(String filePath) async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _repo.uploadAvatar(filePath);
    result.when(
      success: (avatarUrl) {
        state = state.copyWith(isLoading: false, avatarUrl: avatarUrl);
      },
      failure: (message, statusCode) {
        state = state.copyWith(isLoading: false, error: message);
      },
    );
  }

  /// Change app language
  /// تغيير لغة التطبيق
  void changeLanguage(String lang) {
    state = state.copyWith(language: lang);
  }
}

/// Provider for profile state
/// موفر حالة الملف الشخصي
final profileProvider =
    StateNotifierProvider.autoDispose<ProfileNotifier, ProfileState>((ref) {
  return ProfileNotifier(ref.read(profileRepoProvider));
});
