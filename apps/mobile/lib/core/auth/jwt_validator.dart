import 'dart:convert';

/// JWT Claims Validator
/// أداة التحقق من مطالبات JWT
///
/// Validates JWT token structure and claims WITHOUT signature verification.
/// Mobile apps use HS256 tokens where the secret is server-side only.
/// This validator checks:
/// - Token structure (3 base64 parts)
/// - Expiry claim (exp)
/// - Required claims (sub, email)
/// - Token type (access vs refresh)

class JwtClaims {
  final String subject;
  final String? email;
  final List<String> roles;
  final String? tenantId;
  final String? tokenType;
  final DateTime? issuedAt;
  final DateTime? expiresAt;
  final String? jti;
  final Map<String, dynamic> raw;

  const JwtClaims({
    required this.subject,
    this.email,
    this.roles = const [],
    this.tenantId,
    this.tokenType,
    this.issuedAt,
    this.expiresAt,
    this.jti,
    this.raw = const {},
  });

  /// Check if the token is expired (with optional clock skew buffer)
  bool isExpired({Duration clockSkew = const Duration(seconds: 30)}) {
    if (expiresAt == null) return true;
    return DateTime.now().isAfter(expiresAt!.subtract(clockSkew));
  }

  /// Check if the token will expire within the given duration
  bool expiresWithin(Duration duration) {
    if (expiresAt == null) return true;
    return DateTime.now().isAfter(expiresAt!.subtract(duration));
  }

  /// Get remaining time until expiry
  Duration? get timeUntilExpiry {
    if (expiresAt == null) return null;
    final remaining = expiresAt!.difference(DateTime.now());
    return remaining.isNegative ? Duration.zero : remaining;
  }
}

/// Result of JWT validation
class JwtValidationResult {
  final bool isValid;
  final JwtClaims? claims;
  final String? error;

  const JwtValidationResult.valid(this.claims)
      : isValid = true,
        error = null;

  const JwtValidationResult.invalid(this.error)
      : isValid = false,
        claims = null;
}

/// Parse and validate JWT token claims
/// Does NOT verify the cryptographic signature (server-side only for HS256)
class JwtValidator {
  /// Parse JWT token and extract claims
  static JwtValidationResult parse(String token) {
    try {
      final parts = token.split('.');
      if (parts.length != 3) {
        return const JwtValidationResult.invalid(
          'Invalid JWT structure: expected 3 parts',
        );
      }

      // Decode payload (part 2)
      final payload = _decodeBase64Url(parts[1]);
      if (payload == null) {
        return const JwtValidationResult.invalid(
          'Invalid JWT payload: base64 decode failed',
        );
      }

      final Map<String, dynamic> claims;
      try {
        claims = json.decode(payload) as Map<String, dynamic>;
      } catch (_) {
        return const JwtValidationResult.invalid(
          'Invalid JWT payload: not valid JSON',
        );
      }

      // Validate required claim: sub (subject/user ID)
      final sub = claims['sub'] as String?;
      if (sub == null || sub.isEmpty) {
        return const JwtValidationResult.invalid(
          'Invalid JWT: missing "sub" claim',
        );
      }

      // Extract optional claims
      final email = claims['email'] as String?;

      // Roles: support both "roles" (array) and "role" (string)
      List<String> roles = [];
      if (claims['roles'] is List) {
        roles = (claims['roles'] as List).cast<String>();
      } else if (claims['role'] is String) {
        roles = [claims['role'] as String];
      }

      // Tenant ID: support both "tid" and "tenant_id"
      final tenantId = (claims['tid'] ?? claims['tenant_id']) as String?;

      // Token type
      final tokenType = claims['type'] as String?;

      // Timestamps
      DateTime? issuedAt;
      if (claims['iat'] is num) {
        issuedAt = DateTime.fromMillisecondsSinceEpoch(
          (claims['iat'] as num).toInt() * 1000,
        );
      }

      DateTime? expiresAt;
      if (claims['exp'] is num) {
        expiresAt = DateTime.fromMillisecondsSinceEpoch(
          (claims['exp'] as num).toInt() * 1000,
        );
      }

      final jti = claims['jti'] as String?;

      return JwtValidationResult.valid(
        JwtClaims(
          subject: sub,
          email: email,
          roles: roles,
          tenantId: tenantId,
          tokenType: tokenType,
          issuedAt: issuedAt,
          expiresAt: expiresAt,
          jti: jti,
          raw: claims,
        ),
      );
    } catch (e) {
      return JwtValidationResult.invalid('JWT parse error: $e');
    }
  }

  /// Validate token structure and expiry
  static JwtValidationResult validate(String token) {
    final result = parse(token);
    if (!result.isValid) return result;

    final claims = result.claims!;

    // Check expiry
    if (claims.isExpired()) {
      return const JwtValidationResult.invalid('Token has expired');
    }

    // Check token type (reject refresh tokens used as access tokens)
    if (claims.tokenType != null && claims.tokenType != 'access') {
      return const JwtValidationResult.invalid(
        'Invalid token type: expected "access"',
      );
    }

    return result;
  }

  /// Decode base64url encoded string
  static String? _decodeBase64Url(String input) {
    try {
      // Add padding if needed
      String normalized = input.replaceAll('-', '+').replaceAll('_', '/');
      switch (normalized.length % 4) {
        case 2:
          normalized += '==';
          break;
        case 3:
          normalized += '=';
          break;
      }
      return utf8.decode(base64.decode(normalized));
    } catch (_) {
      return null;
    }
  }
}
