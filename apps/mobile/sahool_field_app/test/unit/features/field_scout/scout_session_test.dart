import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/field_scout/domain/models/scout_session.dart';

void main() {
  group('GeoPoint', () {
    test('toJson and fromJson round-trip', () {
      final point = GeoPoint(
        latitude: 15.369,
        longitude: 44.191,
        altitude: 2200.0,
        accuracy: 5.0,
        timestamp: DateTime(2026, 1, 10, 8, 30),
      );

      final json = point.toJson();
      final restored = GeoPoint.fromJson(json);

      expect(restored.latitude, point.latitude);
      expect(restored.longitude, point.longitude);
      expect(restored.altitude, point.altitude);
      expect(restored.accuracy, point.accuracy);
      expect(restored.timestamp, point.timestamp);
    });

    test('distanceTo returns 0 for same point', () {
      final p = GeoPoint(latitude: 15.0, longitude: 44.0);
      expect(p.distanceTo(p), closeTo(0, 1));
    });

    test('distanceTo returns reasonable distance for known points', () {
      // Sana'a to Aden is ~320 km
      final sanaa = GeoPoint(latitude: 15.369, longitude: 44.191);
      final aden = GeoPoint(latitude: 12.788, longitude: 45.018);
      final distance = sanaa.distanceTo(aden);
      // Should be around 290-320 km
      expect(distance, greaterThan(250000));
      expect(distance, lessThan(400000));
    });
  });

  group('IssueDetails', () {
    test('toJson and fromJson round-trip', () {
      const issue = IssueDetails(
        category: IssueCategory.pest,
        severity: IssueSeverity.high,
        description: 'Red Palm Weevil detected',
        affectedAreaPercent: 15.5,
        recommendations: ['Apply treatment', 'Report to ministry'],
      );

      final json = issue.toJson();
      final restored = IssueDetails.fromJson(json);

      expect(restored.category, IssueCategory.pest);
      expect(restored.severity, IssueSeverity.high);
      expect(restored.description, 'Red Palm Weevil detected');
      expect(restored.affectedAreaPercent, 15.5);
      expect(restored.recommendations, hasLength(2));
    });
  });

  group('AIAnalysis', () {
    test('toJson and fromJson round-trip', () {
      final analysis = AIAnalysis(
        modelVersion: 'yolo26-m-v2.1',
        confidence: 0.92,
        detectedIssue: 'Leaf Rust',
        category: IssueCategory.disease,
        severity: IssueSeverity.medium,
        suggestions: ['Apply fungicide', 'Monitor weekly'],
        analyzedAt: DateTime(2026, 1, 15, 10, 0),
      );

      final json = analysis.toJson();
      final restored = AIAnalysis.fromJson(json);

      expect(restored.modelVersion, 'yolo26-m-v2.1');
      expect(restored.confidence, 0.92);
      expect(restored.detectedIssue, 'Leaf Rust');
      expect(restored.category, IssueCategory.disease);
      expect(restored.severity, IssueSeverity.medium);
      expect(restored.suggestions, hasLength(2));
    });

    test('handles null optional fields', () {
      final analysis = AIAnalysis(
        modelVersion: 'v1.0',
        confidence: 0.5,
        analyzedAt: DateTime(2026, 1, 1),
      );

      final json = analysis.toJson();
      final restored = AIAnalysis.fromJson(json);

      expect(restored.detectedIssue, isNull);
      expect(restored.category, isNull);
      expect(restored.severity, isNull);
      expect(restored.suggestions, isEmpty);
    });
  });

  group('ScoutCheckpoint', () {
    test('hasIssue returns true when issue is present', () {
      final checkpoint = ScoutCheckpoint(
        id: 'cp1',
        location: GeoPoint(latitude: 15.0, longitude: 44.0),
        timestamp: DateTime(2026, 1, 1),
        type: CheckpointType.issue,
        issue: const IssueDetails(
          category: IssueCategory.pest,
          severity: IssueSeverity.low,
          description: 'Minor aphid presence',
        ),
      );
      expect(checkpoint.hasIssue, true);
      expect(checkpoint.hasPhotos, false);
      expect(checkpoint.hasAIAnalysis, false);
    });

    test('hasIssue returns false when no issue', () {
      final checkpoint = ScoutCheckpoint(
        id: 'cp2',
        location: GeoPoint(latitude: 15.0, longitude: 44.0),
        timestamp: DateTime(2026, 1, 1),
        type: CheckpointType.routine,
      );
      expect(checkpoint.hasIssue, false);
    });

    test('hasPhotos returns true when photos are present', () {
      final checkpoint = ScoutCheckpoint(
        id: 'cp3',
        location: GeoPoint(latitude: 15.0, longitude: 44.0),
        timestamp: DateTime(2026, 1, 1),
        type: CheckpointType.photo,
        photoUrls: ['photo1.jpg', 'photo2.jpg'],
      );
      expect(checkpoint.hasPhotos, true);
    });

    test('toJson and fromJson round-trip', () {
      final checkpoint = ScoutCheckpoint(
        id: 'cp4',
        location: GeoPoint(latitude: 15.5, longitude: 44.2),
        timestamp: DateTime(2026, 2, 1, 9, 0),
        type: CheckpointType.measurement,
        note: 'Soil moisture reading',
        measurements: {'moisture': 35.0, 'temperature': 22.5},
      );

      final json = checkpoint.toJson();
      final restored = ScoutCheckpoint.fromJson(json);

      expect(restored.id, 'cp4');
      expect(restored.type, CheckpointType.measurement);
      expect(restored.note, 'Soil moisture reading');
      expect(restored.measurements!['moisture'], 35.0);
    });
  });

  group('ScoutSession', () {
    late ScoutSession session;

    setUp(() {
      session = ScoutSession(
        id: 'session-001',
        fieldId: 'field-001',
        fieldName: 'حقل القمح',
        scouterId: 'user-001',
        scouterName: 'أحمد',
        startedAt: DateTime(2026, 1, 15, 8, 0),
        endedAt: DateTime(2026, 1, 15, 9, 30),
        status: ScoutSessionStatus.completed,
        checkpoints: [
          ScoutCheckpoint(
            id: 'cp1',
            location: GeoPoint(latitude: 15.0, longitude: 44.0),
            timestamp: DateTime(2026, 1, 15, 8, 10),
            type: CheckpointType.routine,
          ),
          ScoutCheckpoint(
            id: 'cp2',
            location: GeoPoint(latitude: 15.0, longitude: 44.0),
            timestamp: DateTime(2026, 1, 15, 8, 30),
            type: CheckpointType.issue,
            issue: const IssueDetails(
              category: IssueCategory.disease,
              severity: IssueSeverity.medium,
              description: 'Leaf spot observed',
            ),
          ),
        ],
        trackPoints: [
          GeoPoint(latitude: 15.0, longitude: 44.0),
          GeoPoint(latitude: 15.001, longitude: 44.001),
        ],
      );
    });

    test('duration calculates correctly', () {
      expect(session.duration, const Duration(hours: 1, minutes: 30));
    });

    test('issuesCount counts checkpoints with issues', () {
      expect(session.issuesCount, 1);
    });

    test('distanceMeters calculates distance from track points', () {
      expect(session.distanceMeters, greaterThan(0));
    });

    test('distanceMeters returns 0 for less than 2 track points', () {
      final noTrack = session.copyWith(trackPoints: []);
      expect(noTrack.distanceMeters, 0);

      final onePoint = session.copyWith(
        trackPoints: [GeoPoint(latitude: 15.0, longitude: 44.0)],
      );
      expect(onePoint.distanceMeters, 0);
    });

    test('toJson and fromJson round-trip', () {
      final json = session.toJson();
      final restored = ScoutSession.fromJson(json);

      expect(restored.id, session.id);
      expect(restored.fieldId, session.fieldId);
      expect(restored.fieldName, session.fieldName);
      expect(restored.scouterId, session.scouterId);
      expect(restored.scouterName, session.scouterName);
      expect(restored.status, ScoutSessionStatus.completed);
      expect(restored.checkpoints.length, 2);
      expect(restored.trackPoints.length, 2);
    });

    test('copyWith creates modified copy', () {
      final paused = session.copyWith(status: ScoutSessionStatus.paused);
      expect(paused.status, ScoutSessionStatus.paused);
      expect(paused.id, session.id);
    });
  });

  group('ScoutSessionSummary', () {
    test('toJson and fromJson round-trip', () {
      const summary = ScoutSessionSummary(
        totalCheckpoints: 10,
        issuesFound: 3,
        photosCount: 8,
        distanceMeters: 1500.5,
        duration: Duration(hours: 2),
        fieldCoveragePercent: 85.0,
        issuesByCategory: {IssueCategory.pest: 2, IssueCategory.disease: 1},
        issuesBySeverity: {IssueSeverity.low: 1, IssueSeverity.medium: 2},
        overallHealthStatus: 'good',
        recommendations: ['Continue monitoring', 'Apply treatment'],
      );

      final json = summary.toJson();
      final restored = ScoutSessionSummary.fromJson(json);

      expect(restored.totalCheckpoints, 10);
      expect(restored.issuesFound, 3);
      expect(restored.photosCount, 8);
      expect(restored.distanceMeters, 1500.5);
      expect(restored.duration, const Duration(hours: 2));
      expect(restored.fieldCoveragePercent, 85.0);
      expect(restored.issuesByCategory[IssueCategory.pest], 2);
      expect(restored.issuesBySeverity[IssueSeverity.medium], 2);
      expect(restored.overallHealthStatus, 'good');
      expect(restored.recommendations, hasLength(2));
    });
  });

  group('Enums', () {
    test('ScoutSessionStatus has all values', () {
      expect(ScoutSessionStatus.values, hasLength(4));
    });

    test('CheckpointType has all values', () {
      expect(CheckpointType.values, hasLength(6));
    });

    test('IssueCategory has all values', () {
      expect(IssueCategory.values, hasLength(9));
    });

    test('IssueSeverity has all values', () {
      expect(IssueSeverity.values, hasLength(4));
    });
  });
}
