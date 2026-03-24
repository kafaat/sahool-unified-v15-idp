import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/di/providers.dart';
import 'package:sahool_field_app/core/iam/iam_providers.dart';
import 'package:sahool_field_app/core/widgets/connectivity_widget.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart';
import 'package:sahool_field_app/features/field_hub/ui/field_dashboard.dart';
import 'package:sahool_field_app/features/tasks/domain/entities/task.dart';
import 'package:sahool_field_app/features/tasks/providers/tasks_provider.dart';
import 'package:sahool_field_app/features/weather/presentation/providers/weather_provider.dart';
import '../../helpers/test_helpers.dart';

void main() {
  group('FieldDashboard Widget', () {
    /// Common overrides needed by FieldDashboard once data has loaded.
    /// The widget watches connectivity, weather, and tasks providers
    /// inside its data branch, so we must stub them to avoid hitting
    /// real platform channels (Connectivity+) and the unimplemented
    /// database provider.
    List<Override> get _baseOverrides => [
          currentTenantProvider.overrideWithValue(null),
          connectivityProvider.overrideWith(
            (ref) => _FakeConnectivityNotifier(),
          ),
          weatherProvider.overrideWith(
            (ref) => _FakeWeatherNotifier(),
          ),
          tasksProvider.overrideWith(
            (ref) => _FakeTasksNotifier(),
          ),
        ];

    /// Helper that wraps FieldDashboard with mocked providers so we don't
    /// need a real database or IAM state.
    Widget buildDashboard({List<Field> fields = const []}) {
      return createTestableWidget(
        overrides: [
          ..._baseOverrides,
          fieldsStreamProvider('default')
              .overrideWith((ref) => Stream.value(fields)),
        ],
        child: const FieldDashboard(),
      );
    }

    testWidgets('should display loading indicator initially', (tester) async {
      await tester.pumpWidget(
        createTestableWidget(
          overrides: [
            ..._baseOverrides,
            fieldsStreamProvider('default')
                .overrideWith((ref) => const Stream.empty()),
          ],
          child: const FieldDashboard(),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should display dashboard after data loads', (tester) async {
      await tester.pumpWidget(buildDashboard());
      await tester.pump();

      // App bar title should always show
      expect(find.text('لوحة القيادة'), findsOneWidget);
    });

    testWidgets('should show refresh button in app bar', (tester) async {
      await tester.pumpWidget(buildDashboard());
      await tester.pump();

      expect(find.byIcon(Icons.refresh), findsOneWidget);
    });

    testWidgets('should show notification icon in app bar', (tester) async {
      await tester.pumpWidget(buildDashboard());
      await tester.pump();

      expect(find.byIcon(Icons.notifications_outlined), findsOneWidget);
    });

    testWidgets('should display FAB for new task', (tester) async {
      await tester.pumpWidget(buildDashboard());
      await tester.pump();

      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.text('مهمة جديدة'), findsOneWidget);
    });
  });
}

// ---------------------------------------------------------------------------
// Fake notifiers used to isolate widget tests from real platform channels
// and unimplemented database providers.
// ---------------------------------------------------------------------------

class _FakeConnectivityNotifier extends StateNotifier<ConnectivityState>
    implements ConnectivityNotifier {
  _FakeConnectivityNotifier() : super(const ConnectivityState());

  @override
  Future<void> checkConnectivity() async {}

  @override
  void startSync() {}

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _FakeWeatherNotifier extends StateNotifier<WeatherState>
    implements WeatherNotifier {
  _FakeWeatherNotifier() : super(const WeatherState());

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _FakeTasksNotifier extends StateNotifier<AsyncValue<List<FieldTask>>>
    implements TasksNotifier {
  _FakeTasksNotifier() : super(const AsyncValue.data([]));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
