import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'core/config/theme.dart';
import 'features/tasks/presentation/tasks_list_screen.dart';

class SahoolFieldApp extends StatelessWidget {
  const SahoolFieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SAHOOL Field',
      debugShowCheckedModeBanner: false,

      // Arabic RTL Support
      locale: const Locale('ar'),
      supportedLocales: const [
        Locale('ar'),
        Locale('en'),
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
      home: const TasksListScreen(),
      routes: {
        '/tasks': (context) => const TasksListScreen(),
      },
    );
  }
}
