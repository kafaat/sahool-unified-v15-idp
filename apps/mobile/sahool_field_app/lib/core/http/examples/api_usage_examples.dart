/// Example usage of the improved API client with error handling and retry logic
///
/// This file demonstrates how to use:
/// - ApiResult for type-safe error handling
/// - ApiError for standardized errors
/// - Circuit breaker pattern
/// - Retry logic with exponential backoff

import '../api_client.dart';
import '../api_error_handler.dart';
import '../api_result.dart';

/// Example model
class User {
  final String id;
  final String name;
  final String email;

  User({
    required this.id,
    required this.name,
    required this.email,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as String,
        name: json['name'] as String,
        email: json['email'] as String,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'email': email,
      };
}

/// Example service using the new API client
class UserService {
  final ApiClient _apiClient;

  UserService(this._apiClient);

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 1: Basic usage with ApiResult
  // ═══════════════════════════════════════════════════════════════════════════

  /// Fetch user with type-safe error handling
  Future<ApiResult<User>> getUser(String userId) async {
    final result = await _apiClient.getSafe<Map<String, dynamic>>(
      '/users/$userId',
    );

    // Transform the result to User model
    return result.map((data) => User.fromJson(data));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 2: Using when() for handling both success and failure
  // ═══════════════════════════════════════════════════════════════════════════

  Future<void> displayUser(String userId) async {
    final result = await getUser(userId);

    result.when(
      success: (user) {
        print('User found: ${user.name} (${user.email})');
      },
      failure: (error) {
        print('Error loading user: ${error.message}');

        // Handle specific error types
        if (error.isNetworkError) {
          print('Please check your internet connection');
        } else if (error.isAuthError) {
          print('Please log in again');
        }
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 3: Using map and flatMap for transformations
  // ═══════════════════════════════════════════════════════════════════════════

  Future<ApiResult<String>> getUserEmail(String userId) async {
    final result = await getUser(userId);

    // Extract just the email
    return result.map((user) => user.email);
  }

  Future<ApiResult<List<User>>> getUserFriends(String userId) async {
    final userResult = await getUser(userId);

    // Chain API calls with flatMap
    return userResult.flatMap((user) async {
      final friendsResult = await _apiClient.getSafe<List<dynamic>>(
        '/users/${user.id}/friends',
      );

      return friendsResult.map(
        (friends) => friends.map((f) => User.fromJson(f)).toList(),
      );
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 4: Using getOrElse for default values
  // ═══════════════════════════════════════════════════════════════════════════

  Future<User> getUserOrDefault(String userId) async {
    final result = await getUser(userId);

    return result.getOrElse(
      User(
        id: 'unknown',
        name: 'Unknown User',
        email: 'unknown@example.com',
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 5: Handling validation errors
  // ═══════════════════════════════════════════════════════════════════════════

  Future<ApiResult<User>> createUser({
    required String name,
    required String email,
  }) async {
    final result = await _apiClient.postSafe<Map<String, dynamic>>(
      '/users',
      {
        'name': name,
        'email': email,
      },
    );

    return result.map((data) => User.fromJson(data));
  }

  Future<String> createUserWithErrorHandling({
    required String name,
    required String email,
  }) async {
    final result = await createUser(name: name, email: email);

    return result.when(
      success: (user) => 'User created: ${user.name}',
      failure: (error) {
        // Handle different error types
        if (error.isValidationError) {
          // Extract validation errors from response
          if (error.data is Map) {
            final errors = error.data['errors'] as Map<String, dynamic>?;
            if (errors != null) {
              return 'Validation errors: ${errors.values.join(', ')}';
            }
          }
          return 'Invalid input: ${error.message}';
        }

        if (error.isNetworkError) {
          return 'Network error: Please check your connection';
        }

        return 'Error: ${error.message}';
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 6: Using onSuccess and onFailure for side effects
  // ═══════════════════════════════════════════════════════════════════════════

  Future<ApiResult<User>> updateUser(User user) async {
    final result = await _apiClient.putSafe<Map<String, dynamic>>(
      '/users/${user.id}',
      user.toJson(),
    );

    return result
        .map((data) => User.fromJson(data))
        .onSuccess((user) {
          // Log success
          print('User updated successfully: ${user.name}');
        })
        .onFailure((error) {
          // Log error
          print('Failed to update user: ${error.message}');
        });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 7: Async transformations
  // ═══════════════════════════════════════════════════════════════════════════

  Future<ApiResult<String>> getUserProfilePicture(String userId) async {
    return getUser(userId).flatMapAsync((user) async {
      // Fetch profile picture URL
      final pictureResult = await _apiClient.getSafe<Map<String, dynamic>>(
        '/users/${user.id}/picture',
      );

      return pictureResult.map((data) => data['url'] as String);
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 8: Circuit breaker status monitoring
  // ═══════════════════════════════════════════════════════════════════════════

  Map<String, dynamic> getApiHealth() {
    return _apiClient.getCircuitBreakerStatus();
  }

  void resetApiCircuitBreaker() {
    _apiClient.resetCircuitBreaker();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 9: Legacy exception-based usage (for backward compatibility)
  // ═══════════════════════════════════════════════════════════════════════════

  Future<User?> getUserLegacy(String userId) async {
    try {
      final data = await _apiClient.get('/users/$userId');
      return User.fromJson(data as Map<String, dynamic>);
    } on ApiException catch (e) {
      print('Error: ${e.message}');

      if (e.isNetworkError) {
        print('Network error occurred');
      }

      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Example 10: Error type checking
  // ═══════════════════════════════════════════════════════════════════════════

  Future<void> demonstrateErrorHandling() async {
    final result = await getUser('invalid-id');

    result.whenOrNull(
      failure: (error) {
        // Check error type
        switch (error.type) {
          case ApiErrorType.network:
            print('Network issue - try again later');
            break;
          case ApiErrorType.auth:
            print('Authentication required - redirecting to login');
            break;
          case ApiErrorType.notFound:
            print('User not found');
            break;
          case ApiErrorType.validation:
            print('Invalid user ID format');
            break;
          case ApiErrorType.server:
            print('Server error - please contact support');
            break;
          case ApiErrorType.rateLimited:
            print('Too many requests - please wait');
            break;
          default:
            print('Unexpected error: ${error.message}');
        }

        // Log technical details for debugging
        print('Technical: ${error.technicalMessage}');
        print('Code: ${error.code}');
        print('Status: ${error.statusCode}');
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 11: UI Integration (with Flutter)
// ═══════════════════════════════════════════════════════════════════════════

/// Example UI state management
class UserState {
  final User? user;
  final bool isLoading;
  final ApiError? error;

  UserState({
    this.user,
    this.isLoading = false,
    this.error,
  });

  UserState copyWith({
    User? user,
    bool? isLoading,
    ApiError? error,
  }) {
    return UserState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// Example controller/notifier
class UserController {
  final UserService _userService;
  UserState _state = UserState();

  UserController(this._userService);

  UserState get state => _state;

  Future<void> loadUser(String userId) async {
    // Set loading state
    _state = _state.copyWith(isLoading: true, error: null);

    // Fetch user
    final result = await _userService.getUser(userId);

    // Update state based on result
    _state = result.when(
      success: (user) => _state.copyWith(
        user: user,
        isLoading: false,
        error: null,
      ),
      failure: (error) => _state.copyWith(
        user: null,
        isLoading: false,
        error: error,
      ),
    );
  }

  String getUserFriendlyError() {
    final error = _state.error;
    if (error == null) return '';

    return ApiErrorHandler.getUserMessage(
      error.code,
      defaultMessage: error.message,
    );
  }

  bool canRetry() {
    return _state.error?.isRetryable ?? false;
  }
}
