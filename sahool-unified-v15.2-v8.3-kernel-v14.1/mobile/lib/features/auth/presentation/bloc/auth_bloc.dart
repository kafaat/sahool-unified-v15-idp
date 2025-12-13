// ============================================
// SAHOOL - Auth BLoC
// إدارة حالة المصادقة
// ============================================

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../core/api/auth_interceptor.dart';

// ============================================
// EVENTS
// ============================================

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class CheckAuthStatus extends AuthEvent {}

class LoginRequested extends AuthEvent {
  final String email;
  final String password;

  const LoginRequested({required this.email, required this.password});

  @override
  List<Object?> get props => [email, password];
}

class RegisterRequested extends AuthEvent {
  final String email;
  final String password;
  final String fullName;
  final String? phone;

  const RegisterRequested({
    required this.email,
    required this.password,
    required this.fullName,
    this.phone,
  });

  @override
  List<Object?> get props => [email, password, fullName, phone];
}

class LogoutRequested extends AuthEvent {}

class TokenRefreshRequested extends AuthEvent {}

// ============================================
// STATES
// ============================================

abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthAuthenticated extends AuthState {
  final String userId;
  final String email;
  final String fullName;
  final String role;

  const AuthAuthenticated({
    required this.userId,
    required this.email,
    required this.fullName,
    required this.role,
  });

  @override
  List<Object?> get props => [userId, email, fullName, role];
}

class AuthUnauthenticated extends AuthState {}

class AuthError extends AuthState {
  final String message;

  const AuthError(this.message);

  @override
  List<Object?> get props => [message];
}

// ============================================
// BLOC
// ============================================

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc() : super(AuthInitial()) {
    on<CheckAuthStatus>(_onCheckAuthStatus);
    on<LoginRequested>(_onLoginRequested);
    on<RegisterRequested>(_onRegisterRequested);
    on<LogoutRequested>(_onLogoutRequested);
    on<TokenRefreshRequested>(_onTokenRefreshRequested);
  }

  Future<void> _onCheckAuthStatus(
    CheckAuthStatus event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    try {
      final hasToken = await AuthInterceptor.hasValidToken();
      
      if (hasToken) {
        // TODO: Validate token and get user info
        emit(const AuthAuthenticated(
          userId: 'demo',
          email: 'demo@sahool.app',
          fullName: 'مستخدم تجريبي',
          role: 'owner',
        ));
      } else {
        emit(AuthUnauthenticated());
      }
    } catch (e) {
      emit(AuthUnauthenticated());
    }
  }

  Future<void> _onLoginRequested(
    LoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    try {
      // TODO: Call API
      await Future.delayed(const Duration(seconds: 2)); // Simulate API call
      
      // Save tokens
      await AuthInterceptor.saveTokens('demo_access_token', 'demo_refresh_token');

      emit(const AuthAuthenticated(
        userId: 'demo',
        email: 'demo@sahool.app',
        fullName: 'مستخدم تجريبي',
        role: 'owner',
      ));
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }

  Future<void> _onRegisterRequested(
    RegisterRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    try {
      // TODO: Call API
      await Future.delayed(const Duration(seconds: 2));
      
      emit(AuthUnauthenticated()); // Go to login after registration
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }

  Future<void> _onLogoutRequested(
    LogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    try {
      await AuthInterceptor.clearTokens();
      emit(AuthUnauthenticated());
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }

  Future<void> _onTokenRefreshRequested(
    TokenRefreshRequested event,
    Emitter<AuthState> emit,
  ) async {
    // Token refresh is handled by the interceptor
  }
}
