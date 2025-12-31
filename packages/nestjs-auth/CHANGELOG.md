# Changelog

All notable changes to `@sahool/nestjs-auth` will be documented in this file.

## [1.0.0] - 2024-12-31

### Added

- Initial release of shared authentication module
- JWT authentication with RS256/HS256 support
- Role-based access control (RBAC)
- Permission-based access control
- Token revocation with Redis backend
- User validation with Redis caching
- Multiple guard types:
  - JwtAuthGuard
  - RolesGuard
  - PermissionsGuard
  - FarmAccessGuard
  - OptionalAuthGuard
  - ActiveAccountGuard
  - TokenRevocationGuard
- Custom decorators:
  - @Public()
  - @Roles()
  - @RequirePermissions()
  - @CurrentUser()
  - @UserId()
  - @UserRoles()
  - @TenantId()
  - @UserPermissions()
  - @AuthToken()
  - @RequestLanguage()
  - @SkipRevocationCheck()
- Configuration management with environment variables
- Bilingual error messages (English/Arabic)
- Full TypeScript support with type definitions
- Comprehensive documentation:
  - README.md
  - USAGE_EXAMPLES.md
  - MIGRATION_GUIDE.md
  - INTEGRATION_EXAMPLE.md
- User repository interface for database integration
- Token revocation service
- User validation service with caching

### Features

- Global authentication guard support
- Async module configuration
- Passport JWT strategy integration
- Redis-based caching for performance
- Automatic token expiration
- Request tracking and logging
- Multi-tenant support
- Farm access control (domain-specific)
- Active account validation
- Token revocation on logout, password change, etc.

### Documentation

- Complete API documentation
- Usage examples for common patterns
- Migration guide from custom implementations
- Integration example for marketplace-service
- Step-by-step setup instructions
- Troubleshooting guide
- Best practices

### Testing

- Unit test examples
- E2E test examples
- Mock configuration for testing

## Migration from Existing Auth

Services using custom auth implementations can migrate to this shared module. See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for details.

### Breaking Changes

None - this is the initial release.

### Deprecated

None - this is the initial release.

### Security

- JWT secret validation in production
- Minimum secret length requirements
- Support for RS256 asymmetric encryption
- Token revocation for compromised tokens
- User status validation (active, verified, not deleted/suspended)
- Rate limiting support (via configuration)

## Future Plans

- [ ] Add support for refresh tokens
- [ ] Add rate limiting middleware
- [ ] Add API key authentication
- [ ] Add OAuth2 support
- [ ] Add SAML support
- [ ] Add biometric authentication
- [ ] Add two-factor authentication (2FA)
- [ ] Add session management
- [ ] Add audit logging
- [ ] Add RBAC management UI
- [ ] Add permission management UI
- [ ] Add authentication analytics
- [ ] Add GraphQL support
- [ ] Add WebSocket authentication
- [ ] Add microservice-to-microservice auth
