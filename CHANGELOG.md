# Changelog

All notable changes to the SAHOOL Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Docker Sequential Build Scripts** (PR #315)
  - `docker-one-by-one.ps1`: PowerShell script for sequential container builds
  - `docker-one-by-one.sh`: Bash equivalent for Linux/macOS users
  - Prevents resource conflicts on M1/M2 Macs and constrained environments
  - Two-phase build approach with comprehensive error handling

- **Comprehensive Test Infrastructure** (PR #315)
  - 24 integration test files covering all major workflows
  - Load testing framework with k6 (smoke, load, stress, spike, soak scenarios)
  - Multi-client simulation for realistic testing
  - Unit tests for AI, kernel, NDVI, and shared modules
  - Smoke tests for quick sanity checks
  - Performance testing with Grafana dashboards and InfluxDB metrics

- **Developer Tools** (PR #315)
  - Architecture validation: `tools/arch/check_imports.py`
  - Compliance checklist generator: `tools/compliance/generate_checklist.py`
  - Environment validation: `tools/env/validate_env.py`
  - Event catalog generator: `tools/events/generate_catalog.py`
  - Security certificate generators: `tools/security/certs/`
  - IoT sensor simulator: `tools/sensor-simulator/simulator.py`

- **Documentation**
  - POST_MERGE_VERIFICATION.md: Comprehensive post-merge checklist
  - Enhanced test documentation in tests/README.md
  - Load testing guides: tests/load/README.md and QUICKSTART.md

## [16.0.1] - 2024-12-24

### Security
- **API Gateway Security Hardening**
  - Removed wildcard CORS (`allow_origins=["*"]`) from 4 core services
  - Implemented centralized CORS configuration with environment-based whitelisting
  - Added production, development, and staging origin whitelists
  - Enhanced WebSocket gateway with mandatory authentication (removed `WS_REQUIRE_AUTH` bypass)
  - Comprehensive JWT validation with error logging
  - IoT Gateway hardening with device authorization and sensor validation
  - Added tenant isolation checks across all IoT operations

- **Kong Configuration Enhancements**
  - Fixed service port mappings (ws-gateway: 8089→8081, crop-growth-model: 3000→3023)
  - Added 7 missing services from docker-compose to Kong configuration
  - Standardized health checks to `/healthz` endpoint across all 31 services
  - Implemented consistent service naming (kebab-case)
  - Total: 31 upstreams configured with active/passive health monitoring

### Added
- **Mobile App - Golden Release Improvements**
  - Comprehensive testing infrastructure with fixtures, mocks, and test helpers
  - 17 new loading state components (Shimmer, Skeleton patterns)
  - 20+ predefined empty states with Arabic/RTL support
  - Performance monitoring with FPS tracking
  - Optimized list components with pagination support
  - 23 new database indexes for query optimization
  - Token refresh mechanism in auth service
  - AES-256 encryption for sensitive data
  - Local notification service with 6 channels
  - Firebase Cloud Messaging integration
  - Deep linking support for notifications

- **Web & Admin Dashboard Improvements**
  - Real-time alert panel with WebSocket integration
  - KPI cards and responsive grid layouts
  - Quick action buttons for common operations
  - Enhanced settings page with comprehensive configuration options
  - Improved error boundaries with detailed error states
  - WebSocket hooks for real-time data updates
  - Enhanced epidemic, irrigation, and sensor monitoring pages

### Changed
- Database schema updated to v5 with performance optimizations
- Biometric service enhanced with Arabic prompts
- Auth interceptor with automatic 401 handling
- Improved field, task, and weather data fetching hooks

### Fixed
- Docker build compatibility issues across multiple services
- Android dexing problems in mobile app
- Package-lock.json synchronization issues
- Merge conflicts in multiple service configurations

## [16.0.0] - 2024-12-17

### Added
- Sprint 1 Governance Pack
  - Ruff linter/formatter with strict configuration
  - Pre-commit hooks for code quality
  - detect-secrets integration for security
  - ENV drift detection and validation
  - Migration rules documentation
  - Contract structure for events/APIs

### Added
- **Sprint 10**: AI Explainability & Feedback System
  - Explanation models with confidence breakdown
  - Evidence tracking for AI decisions
  - Context aggregator for unified field data
  - Feedback collection with sentiment analysis
  - Prometheus-compatible metrics

- **Sprint 11**: Web Dashboard Upgrade
  - KPI cards and grid layout
  - Real-time alert panel with filtering
  - Quick action buttons
  - Cockpit main dashboard
  - WebSocket integration hooks

- **Sprint 12**: Mobile Enhancement
  - Super Home Screen with daily brief
  - Offline sync engine with conflict resolution
  - Push notification service
  - Riverpod state management

- **RC Workflow**: GitHub Actions Release Candidate
  - Automated RC builds on tag push
  - Multi-environment deployment
  - Slack notifications

### Changed
- Updated all dependencies to December 2025 versions
- Python target version upgraded to 3.11
- Flutter minimum SDK version to 3.24.0

## [15.3.2] - 2025-12-15

### Fixed
- Flutter build compatibility issues
- Python import refactoring for clean structure
- Android dexing issue resolution

### Changed
- Research core module integration
- Agro rules engine updates

## [15.2.0] - 2025-12-01

### Added
- Marketplace API endpoints
- Field operations service
- NATS messaging integration
- Kong API Gateway configuration

### Security
- OTP-based authentication system
- JWT token validation
- Rate limiting on API endpoints

---

[Unreleased]: https://github.com/kafaat/sahool-unified-v15-idp/compare/v16.0.1...HEAD
[16.0.1]: https://github.com/kafaat/sahool-unified-v15-idp/compare/v16.0.0...v16.0.1
[16.0.0]: https://github.com/kafaat/sahool-unified-v15-idp/compare/v15.3.2...v16.0.0
[15.3.2]: https://github.com/kafaat/sahool-unified-v15-idp/compare/v15.2.0...v15.3.2
[15.2.0]: https://github.com/kafaat/sahool-unified-v15-idp/releases/tag/v15.2.0
