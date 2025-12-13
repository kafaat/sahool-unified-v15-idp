// ============================================
// SAHOOL Mobile - منصة سهول الزراعية
// Smart Agricultural Platform for Yemen
// Version 7.1.3
// ============================================

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:get_it/get_it.dart';

import 'core/di/injection.dart';
import 'core/theme/sahool_theme.dart';
import 'core/theme/john_deere_colors.dart';
import 'core/utils/bloc_observer.dart';
import 'features/auth/presentation/bloc/auth_bloc.dart';
import 'features/dashboard/presentation/screens/dashboard_screen.dart';
import 'features/auth/presentation/screens/login_screen.dart';

final getIt = GetIt.instance;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive for offline storage
  await Hive.initFlutter();
  
  // Setup dependency injection
  await configureDependencies();
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
    systemNavigationBarColor: JohnDeereColors.surface,
    systemNavigationBarIconBrightness: Brightness.dark,
  ));
  
  // Setup Bloc observer
  Bloc.observer = SahoolBlocObserver();
  
  runApp(const SahoolApp());
}

class SahoolApp extends StatelessWidget {
  const SahoolApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => getIt<AuthBloc>()..add(CheckAuthStatus())),
      ],
      child: MaterialApp(
        title: 'سهول - SAHOOL',
        debugShowCheckedModeBanner: false,
        
        // RTL Support
        locale: const Locale('ar'),
        supportedLocales: const [
          Locale('ar'), // Arabic
          Locale('en'), // English
        ],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        
        // Theme
        theme: SahoolTheme.light,
        darkTheme: SahoolTheme.dark,
        themeMode: ThemeMode.light,
        
        // Routes
        home: BlocBuilder<AuthBloc, AuthState>(
          builder: (context, state) {
            if (state is AuthAuthenticated) {
              return const DashboardScreen();
            }
            return const LoginScreen();
          },
        ),
        
        // Named Routes
        routes: {
          '/login': (context) => const LoginScreen(),
          '/dashboard': (context) => const DashboardScreen(),
          // Add more routes as needed
        },
      ),
    );
  }
}
