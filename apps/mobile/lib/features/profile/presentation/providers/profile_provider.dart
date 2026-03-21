/// Profile Provider - User Profile State Management
/// موفر الملف الشخصي - إدارة حالة ملف المستخدم
library;
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
  ProfileNotifier() : super(const ProfileState()) {
    loadProfile();
  }

  /// Load user profile from backend/local storage
  /// تحميل ملف المستخدم من الخادم / التخزين المحلي
  Future<void> loadProfile() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await Future.delayed(const Duration(milliseconds: 500));
      state = state.copyWith(
        isLoading: false,
        userId: 'user_001',
        userName: 'Ahmed Al-Rashidi',
        userNameAr: 'أحمد الراشدي',
        email: 'ahmed@sahool.app',
        phone: '+966 50 123 4567',
        farmName: 'Al-Rashidi Farm',
        farmNameAr: 'مزرعة الراشدي',
        farmAreaHectares: 450,
        location: 'القصيم، المملكة العربية السعودية',
        language: 'ar',
        fieldsCount: 12,
        tasksCompleted: 156,
        achievementsCount: 23,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  /// Update profile fields
  /// تحديث حقول الملف الشخصي
  Future<void> updateProfile({
    String? userName,
    String? phone,
    String? farmName,
  }) async {
    state = state.copyWith(isLoading: true);
    try {
      await Future.delayed(const Duration(milliseconds: 300));
      state = state.copyWith(
        isLoading: false,
        userName: userName ?? state.userName,
        phone: phone ?? state.phone,
        farmName: farmName ?? state.farmName,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  /// Upload avatar image
  /// رفع صورة الملف الشخصي
  Future<void> uploadAvatar(String filePath) async {
    state = state.copyWith(isLoading: true);
    try {
      await Future.delayed(const Duration(seconds: 1));
      state = state.copyWith(isLoading: false, avatarUrl: filePath);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
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
  return ProfileNotifier();
});
