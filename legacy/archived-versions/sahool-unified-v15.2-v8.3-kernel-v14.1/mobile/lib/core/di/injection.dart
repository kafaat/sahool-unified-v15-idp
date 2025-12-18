// ============================================
// SAHOOL - Dependency Injection Configuration
// إعداد حقن التبعيات
// ============================================

import 'package:get_it/get_it.dart';
import 'package:dio/dio.dart';
import '../api/api_client.dart';
import '../api/auth_interceptor.dart';
import '../database/local_database.dart';
import '../../features/auth/presentation/bloc/auth_bloc.dart';

final getIt = GetIt.instance;

Future<void> configureDependencies() async {
  // ============================================
  // Core Services
  // ============================================
  
  // Dio HTTP Client
  getIt.registerLazySingleton<Dio>(() {
    final dio = Dio(BaseOptions(
      baseUrl: 'http://localhost:3000/api/v1',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));
    
    // Add interceptors
    dio.interceptors.add(AuthInterceptor());
    dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
    ));
    
    return dio;
  });

  // API Client
  getIt.registerLazySingleton<ApiClient>(
    () => ApiClient(getIt<Dio>()),
  );

  // Local Database
  getIt.registerLazySingleton<LocalDatabase>(
    () => LocalDatabase(),
  );

  // ============================================
  // Repositories
  // ============================================
  
  // Auth Repository
  // getIt.registerLazySingleton<AuthRepository>(
  //   () => AuthRepositoryImpl(getIt<ApiClient>(), getIt<LocalDatabase>()),
  // );

  // Field Repository
  // getIt.registerLazySingleton<FieldRepository>(
  //   () => FieldRepositoryImpl(getIt<ApiClient>(), getIt<LocalDatabase>()),
  // );

  // ============================================
  // BLoCs
  // ============================================
  
  // Auth BLoC
  getIt.registerFactory<AuthBloc>(
    () => AuthBloc(),
  );

  // Dashboard BLoC
  // getIt.registerFactory<DashboardBloc>(
  //   () => DashboardBloc(getIt<FieldRepository>()),
  // );
}
