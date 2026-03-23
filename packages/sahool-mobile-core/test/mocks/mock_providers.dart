import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_field_app/core/http/api_client.dart';

/// Mock Providers for SAHOOL Field App Tests
/// موفرات وهمية للاختبارات
///
/// Note: mockito removed due to analyzer 7.x incompatibility
/// Using manual mocks instead

/// Mock API Client Provider
class MockApiClientNotifier extends StateNotifier<ApiClient?> {
  MockApiClientNotifier() : super(null);

  void setMockClient(ApiClient client) {
    state = client;
  }
}

/// Fake Sync Status for testing
enum FakeSyncStatus { idle, syncing, error }

/// Mock Sync Engine for testing
class MockSyncEngineNotifier extends StateNotifier<FakeSyncStatus> {
  MockSyncEngineNotifier() : super(FakeSyncStatus.idle);

  void setSyncing() => state = FakeSyncStatus.syncing;
  void setIdle() => state = FakeSyncStatus.idle;
  void setError() => state = FakeSyncStatus.error;
}

/// Creates a ProviderContainer with common test overrides
ProviderContainer createTestContainer({
  List<Override> additionalOverrides = const [],
}) {
  return ProviderContainer(
    overrides: [
      // Add common overrides here
      ...additionalOverrides,
    ],
  );
}

/// Test provider overrides factory
class TestOverrides {
  /// Override for network offline state
  static List<Override> networkOffline() {
    return [
      // Add network offline override
    ];
  }

  /// Override for empty data state
  static List<Override> emptyData() {
    return [
      // Add empty data override
    ];
  }

  /// Override for error state
  static List<Override> errorState(String message) {
    return [
      // Add error state override
    ];
  }
}
