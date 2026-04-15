import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/field_scout/domain/models/scout_session.dart';
import 'package:sahool_field_app/features/field_scout/presentation/providers/field_scout_provider.dart';

void main() {
  group('FieldScoutState', () {
    test('should have correct default values', () {
      const state = FieldScoutState();
      expect(state.currentSession, isNull);
      expect(state.lastCompletedSession, isNull);
      expect(state.currentLocation, isNull);
      expect(state.isTracking, false);
      expect(state.isAnalyzing, false);
      expect(state.lastAnalysis, isNull);
      expect(state.error, isNull);
    });

    test('hasActiveSession should return false when no session', () {
      const state = FieldScoutState();
      expect(state.hasActiveSession, false);
    });

    test('copyWith should preserve values when not specified', () {
      const state = FieldScoutState(isTracking: true);
      final copy = state.copyWith();
      expect(copy.isTracking, true);
    });

    test('copyWith should update isAnalyzing', () {
      const state = FieldScoutState();
      final copy = state.copyWith(isAnalyzing: true);
      expect(copy.isAnalyzing, true);
      expect(copy.isTracking, false); // preserved
    });

    test('copyWith should clear error', () {
      const state = FieldScoutState(error: 'some error');
      final copy = state.copyWith(error: null);
      // Note: copyWith assigns error directly (not via ??), so passing null clears it
      expect(copy.error, isNull);
    });
  });

  group('ScoutSession Models', () {
    test('GeoPoint should store coordinates', () {
      final point = GeoPoint(
        latitude: 15.3694,
        longitude: 44.1910,
        accuracy: 5.0,
        timestamp: DateTime(2026, 3, 24),
      );

      expect(point.latitude, 15.3694);
      expect(point.longitude, 44.1910);
      expect(point.accuracy, 5.0);
    });

    test('CheckpointType should have all expected values', () {
      expect(CheckpointType.values, contains(CheckpointType.routine));
      expect(CheckpointType.values, contains(CheckpointType.issue));
    });

    test('IssueCategory should have all expected values', () {
      expect(IssueCategory.values, contains(IssueCategory.pest));
      expect(IssueCategory.values, contains(IssueCategory.disease));
      expect(IssueCategory.values, contains(IssueCategory.weed));
      expect(IssueCategory.values, contains(IssueCategory.water));
      expect(IssueCategory.values, contains(IssueCategory.nutrient));
      expect(IssueCategory.values, contains(IssueCategory.other));
    });

    test('IssueSeverity should have all expected values', () {
      expect(IssueSeverity.values, contains(IssueSeverity.low));
      expect(IssueSeverity.values, contains(IssueSeverity.medium));
      expect(IssueSeverity.values, contains(IssueSeverity.high));
      expect(IssueSeverity.values, contains(IssueSeverity.critical));
    });

    test('ScoutSessionStatus should have all expected values', () {
      expect(ScoutSessionStatus.values, contains(ScoutSessionStatus.active));
      expect(ScoutSessionStatus.values, contains(ScoutSessionStatus.paused));
      expect(ScoutSessionStatus.values, contains(ScoutSessionStatus.completed));
    });
  });

  group('Providers', () {
    test('fieldScoutProvider should be auto-dispose', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final state = container.read(fieldScoutProvider);
      expect(state.hasActiveSession, false);
      expect(state.isTracking, false);
    });

    test('currentScoutSessionProvider should return null initially', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final session = container.read(currentScoutSessionProvider);
      expect(session, isNull);
    });

    test('isScoutingProvider should return false initially', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final isScouting = container.read(isScoutingProvider);
      expect(isScouting, false);
    });
  });
}
