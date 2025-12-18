// ============================================
// SAHOOL - BLoC Observer
// مراقب أحداث BLoC للتصحيح
// ============================================

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logger/logger.dart';

class SahoolBlocObserver extends BlocObserver {
  final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 0,
      errorMethodCount: 5,
      lineLength: 50,
      colors: true,
      printEmojis: true,
      printTime: true,
    ),
  );

  @override
  void onCreate(BlocBase bloc) {
    super.onCreate(bloc);
    _logger.d('onCreate -- ${bloc.runtimeType}');
  }

  @override
  void onChange(BlocBase bloc, Change change) {
    super.onChange(bloc, change);
    _logger.i(
      'onChange -- ${bloc.runtimeType}\n'
      'Current State: ${change.currentState}\n'
      'Next State: ${change.nextState}',
    );
  }

  @override
  void onError(BlocBase bloc, Object error, StackTrace stackTrace) {
    _logger.e(
      'onError -- ${bloc.runtimeType}',
      error: error,
      stackTrace: stackTrace,
    );
    super.onError(bloc, error, stackTrace);
  }

  @override
  void onClose(BlocBase bloc) {
    super.onClose(bloc);
    _logger.d('onClose -- ${bloc.runtimeType}');
  }

  @override
  void onEvent(Bloc bloc, Object? event) {
    super.onEvent(bloc, event);
    _logger.d('onEvent -- ${bloc.runtimeType}: $event');
  }

  @override
  void onTransition(Bloc bloc, Transition transition) {
    super.onTransition(bloc, transition);
    _logger.i(
      'onTransition -- ${bloc.runtimeType}\n'
      'Event: ${transition.event}\n'
      'Current State: ${transition.currentState}\n'
      'Next State: ${transition.nextState}',
    );
  }
}
