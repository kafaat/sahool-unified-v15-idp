# SAHOOL Documentation Gaps Report | تقرير فجوات التوثيق

> Comprehensive analysis of undocumented features, modules, and libraries

[![Audit Date](https://img.shields.io/badge/Audit_Date-2026--01--24-blue.svg)]()
[![Platform Version](https://img.shields.io/badge/Version-16.0.0-green.svg)]()

---

## Executive Summary | الملخص التنفيذي

| Category | Total | Documented | Gap | Coverage |
|----------|-------|------------|-----|----------|
| **Microservices** | 61 | 45 | 16 | 74% |
| **GitHub Workflows** | 37 | 10 | 27 | 27% |
| **Makefile Commands** | 69 | 37 | 32 | 54% |
| **Shared Modules** | 54 | 20 | 34 | 37% |
| **Agricultural Libraries** | 14 | 0 | 14 | 0% |
| **AI/ML Modules** | 15+ | 8 | 7+ | 53% |
| **NPM Packages** | 16 | 16 | 0 | 100% |
| **Python Packages** | 4 | 4 | 0 | 100% |

---

## 1. Undocumented Services (16)

### Business Layer (10)

| Service | Port | Purpose |
|---------|------|---------|
| `agent-registry` | 8160 | Service registry and agent management |
| `audit-service` | - | Audit logging and compliance |
| `chat-service` | 8114 | Real-time chat service |
| `code-review-service` | - | Automated code review |
| `crm-service` | - | Customer relationship management |
| `globalgap-compliance` | 8120 | GlobalGAP IFA v6 certification |
| `logistics-service` | 8162 | Logistics and supply chain |
| `lowcode-engine` | - | Low-code development platform |
| `provider-config` | - | Provider configuration management |
| `wechat-service` | - | WeChat integration |

### Intelligence Layer (5)

| Service | Port | Purpose |
|---------|------|---------|
| `ai-agents-core` | 8121 | AI agents core framework |
| `ai-agents-service` | - | AI agents service |
| `code-fix-agent` | 8090 | Automated code fixing |
| `code-review-agent` | - | Code review agent |
| `knowledge-graph` | - | Knowledge graph management |

### Acquisition Layer (1)

| Service | Port | Purpose |
|---------|------|---------|
| `ussd-gateway` | 8130 | USSD protocol gateway |

---

## 2. Undocumented Makefile Commands (32)

### Mobile Development (11 commands)

```bash
mobile-test          # Run Flutter tests
mobile-build         # Build debug APK
mobile-build-release # Build release APK
mobile-build-aab     # Build App Bundle for Play Store
mobile-analyze       # Analyze Flutter code
mobile-format        # Format Dart code
mobile-clean         # Clean Flutter artifacts
mobile-deps          # Install Flutter dependencies
mobile-codegen       # Generate code (Drift, Freezed)
mobile-doctor        # Check Flutter environment
mobile-ci            # Run mobile CI checks
```

### Infrastructure (6 commands)

```bash
kong-reload      # Reload Kong configuration
vault-up         # Start HashiCorp Vault (BROKEN - wrong path)
vault-down       # Stop Vault (BROKEN - wrong path)
network-create   # Create SAHOOL network
network-inspect  # Inspect SAHOOL network
docs             # Show documentation
```

### Development Tools (6 commands)

```bash
help             # Show available commands
dev-install      # Install development dependencies
generate-tokens  # Generate design tokens
env-check        # Validate environment variables
stats            # Show project statistics
watch            # Watch logs continuously
```

### CI/CD (2 commands)

```bash
ci-full          # Full CI checks with coverage + security
security-scan    # Run security scans
```

### Package Aliases (3 commands)

```bash
starter-up       # Alias for dev-starter
professional-up  # Alias for dev-professional
enterprise-up    # Alias for dev-enterprise
```

### Quick Aliases (4 commands)

```bash
start     # Alias for 'up'
stop      # Alias for 'down'
rebuild   # Full rebuild (clean + build + up)
test-node # Run Node.js tests
```

---

## 3. Undocumented GitHub Workflows (27)

### Deployment (4)

- `blue-green-deploy.yml` - Blue-green deployment strategy
- `canary-deploy.yml` - Canary deployment strategy
- `release-candidate.yml` - Release candidate preparation
- `mobile-release.yml` - Mobile release & Play Store

### Security (3)

- `security.yml` - Comprehensive security scanning
- `security-audit.yml` - Security audit workflow
- `scorecard.yml` - OSSF Scorecard scoring

### Testing (5)

- `e2e-tests.yml` - End-to-end tests
- `playwright-e2e.yml` - Playwright cross-browser testing
- `quality-gates.yml` - Pre-merge quality gates
- `skills-tests.yml` - AI skills testing
- `load-test-validation.yml` - Load test validation

### Build (3)

- `docker-image.yml` - Docker image building
- `docker-buildx.yml` - Multi-architecture builds
- `flutter-apk.yml` - Flutter APK build

### Documentation (4)

- `docs.yml` - Documentation generation
- `lighthouse-ci.yml` - Performance auditing
- `deploy-preview.yml` - Preview environment
- `vercel-preview.yml` - Vercel preview deployment

### Governance (3)

- `governance-structure.yml` - Governance structure validation
- `generator-guard.yml` - Code generator validation
- `event-contracts-guard.yml` - Event schema validation

### Other (5)

- `test.yml` - Test suite with change detection
- `frontend-ci.yml` - Frontend CI
- `mobile-ci.yml` - Flutter mobile CI
- `release.yml` - Release workflow
- `infra-sync.yml` - Infrastructure synchronization

---

## 4. Undocumented Shared Modules (34)

### Agricultural Domain (23 modules)

| Module | Purpose |
|--------|---------|
| `agri_calendar/` | Agricultural calendar with Islamic integration |
| `audit_trail/` | Audit trail implementation |
| `batch_operations/` | Batch processing |
| `crop_insurance/` | Crop insurance management |
| `crop_rotation/` | Crop rotation planning |
| `drone_integration/` | Drone data integration |
| `equipment_maintenance/` | Equipment tracking |
| `farm_documents/` | Farm documentation |
| `fertilizer_management/` | Fertilizer management |
| `field_boundaries/` | PostGIS field boundaries |
| `geofencing/` | Geofencing |
| `harvest_quality/` | Harvest quality monitoring |
| `irrigation/` | HMC irrigation management |
| `labor_management/` | Labor management |
| `market_prices/` | Market price tracking |
| `ml_irrigation/` | ML-based irrigation |
| `notification_preferences/` | Notification preferences |
| `pest_scouting/` | Pest scouting reports |
| `pesticide_compliance/` | PHI/REI compliance |
| `soil_sensors/` | Soil sensor integration |
| `soil_testing/` | Soil testing data |
| `water_management/` | MEWA/NWC compliance |
| `weather_alerts/` | Weather alert management |

### Business/Community (5 modules)

| Module | Purpose |
|--------|---------|
| `cooperatives/` | Cooperative management |
| `crm/` | CRM functionality |
| `learning_marketplace/` | Learning marketplace |
| `smart_agriculture/` | Smart agriculture controls |
| `traceability/` | Supply chain traceability |

### Technology/Platform (6 modules)

| Module | Purpose |
|--------|---------|
| `design-system/` | Design system (TypeScript) |
| `edge_cloud/` | Edge computing |
| `integrations/` | Third-party integrations |
| `lowcode/` | Low-code platform |
| `mobile_sync/` | Mobile synchronization |
| `templates/` | Templates/configurations |

---

## 5. Agricultural Libraries Summary (14 modules)

| Module | Lines | Key Features |
|--------|-------|--------------|
| **agri_calendar** | 1,052 | 13 Saudi + 9 Yemen regions, 57+ crops, Hijri calendar |
| **crop_insurance** | 1,231 | Traditional + parametric, claims processing |
| **crop_rotation** | 1,233 | 60+ crops, soil health, 5-year plans |
| **fertilizer_management** | 620 | 50+ fertilizers, NPK, MRL compliance |
| **field_boundaries** | 2,000+ | PostGIS, geodesic calculations, sharing |
| **harvest_quality** | - | Grades A-F, buyer matching, pricing |
| **irrigation** | - | 4-dimension HMC framework |
| **ml_irrigation** | - | ET0, anomaly detection, patterns |
| **pest_scouting** | - | 100+ pests, economic thresholds, IPM |
| **pesticide_compliance** | - | 500+ pesticides, PHI/REI tracking |
| **soil_sensors** | - | MQTT/LoRaWAN/HTTP, calibration |
| **soil_testing** | - | NPK + micronutrients, amendments |
| **water_management** | - | MEWA/NWC compliance, efficiency |
| **weather_alerts** | - | Frost/heat thresholds, spray windows |

**Total: 10,000+ lines of code**

---

## 6. Undocumented AI/ML Modules (7+)

| Module | Purpose |
|--------|---------|
| `experience_learning.py` | Acontext-inspired self-learning with SOP generation |
| `vector_store.py` | Persistent vector DB (SQLite, Filesystem, Memory) |
| `huggingface_provider.py` | Arabic and multilingual embeddings |
| `validation.py` | Input/output safety validation |
| `metrics.py` | Prometheus-compatible metrics |
| `agents/` | Autonomous agent framework |
| `models_registry/` | 50+ agricultural AI models registry |

### CLAUDE.md Documentation Gaps in Auto-Fix

**Documented Tools (5):**
- Ruff, ESLint, Mypy, Bandit, Dart Analyze

**Actual Tools (8) - 3 missing:**
- Semgrep, Pylint, TypeScript (undocumented)

**Documented Strategies (3):**
- SAFE, AGGRESSIVE, MANUAL

**Actual Strategies (4) - different naming:**
- MINIMAL, SAFE, COMPREHENSIVE, REFACTOR

---

## 7. Governance Issues

### Port Configuration Conflicts (12)

| Service | Governance | Dockerfile | Status |
|---------|-----------|-----------|--------|
| agent-registry | 8160 | 8121 | ❌ |
| code-fix-agent | 8162 | 8090 | ❌ |
| crop-health-ai | 9095 | 8128 | ❌ |
| fertilizer-advisor | 9093 | 8127 | ❌ |
| field-core | 3005 | 3001 | ❌ |
| field-ops | 8155 | 8080 | ❌ |
| field-service | 8156 | 8115 | ❌ |
| logistics-service | 8162 | 8131 | ❌ |
| satellite-service | 9190 | 8125 | ❌ |
| skills-service | 8121 | 8110 | ❌ |
| ussd-gateway | 8163 | 8130 | ❌ |
| weather-advanced | 9092 | 8126 | ❌ |

### Agent Dependency Errors (8)

| Agent | Invalid Reference |
|-------|-------------------|
| disease-expert-agent | crop-health-service (should be crop-health) |
| yield-predictor-agent | yield-prediction-service (should be yield-prediction) |
| audit-agent | auto-fix-engine (not registered) |
| code-fix-agent | git-service (external) |
| code-review-agent | ci-cd-pipeline (external) |
| field-analyst-agent | satellite-service (deprecated) |
| fertilizer-advisor-agent | fertilizer-advisor (deprecated) |
| weather-advisor-agent | weather-advanced (deprecated) |

---

## 8. Integration Modules Summary (9)

| Module | Exports | Key Features |
|--------|---------|--------------|
| **integrations/wechat** | 44 | 5 AI agents, MCP protocol |
| **drone_integration** | 37 | DJI + ArduPilot, VRA maps |
| **edge_cloud** | 45 | 3-layer IoT, 200+ devices |
| **mobile_sync** | 51 | Conflict resolution, delta sync |
| **traceability** | 45 | QR codes, blockchain |
| **cooperatives** | 34 | Resource pooling, revenue sharing |
| **crm** | 12 | Farmer lifecycle, deals |
| **learning_marketplace** | 52 | Courses, progress, XP |
| **smart_agriculture** | 42 | PID control, IFTTT rules |

---

## 9. Broken/Incorrect Items

### Makefile Broken Commands

| Command | Issue | Fix |
|---------|-------|-----|
| `vault-up` | Path `infra/vault/` doesn't exist | Use `infrastructure/core/vault/` |
| `vault-down` | Path `infra/vault/` doesn't exist | Use `infrastructure/core/vault/` |

### Missing __init__.py Files

| Path | Impact |
|------|--------|
| `/shared/contracts/` | Cannot import as Python package |
| `/shared/contracts/schemas/` | No exports |
| `/shared/contracts/ai/` | No exports |

### CLAUDE.md Inaccuracies

| Item | Documented | Actual |
|------|------------|--------|
| Workflow count | 38 | 37 |
| Service count | 57+ | 61 |
| Auto-fix tools | 5 | 8 |
| Auto-fix strategies | 3 | 4 |

---

## 10. Recommendations

### Priority 1 - Critical (This Week)

1. **Fix Port Mismatches** - Update governance/services.yaml
2. **Fix Broken Makefile** - Correct vault paths
3. **Add Missing __init__.py** - Create for contracts module
4. **Update Agent Dependencies** - Remove deprecated references

### Priority 2 - High (This Sprint)

1. **Update CLAUDE.md Services** - Add 16 missing services
2. **Document Makefile Commands** - Add 32 commands
3. **Document Workflows** - Create workflow README
4. **Fix Auto-fix Documentation** - Correct tools and strategies

### Priority 3 - Medium (This Month)

1. **Document Shared Modules** - Add descriptions for 34 modules
2. **Document Agricultural Libraries** - Create comprehensive docs
3. **Document AI Modules** - Add 7+ missing modules
4. **Document Integration Modules** - Add 9 module guides

### Priority 4 - Low (Next Quarter)

1. **Auto-generate Documentation** - From governance files
2. **Implement Gap Detection** - CI workflow for coverage
3. **Create Video Tutorials** - For complex modules

---

## Appendix: File Counts

### Key Directories

| Directory | Python Files | TypeScript Files | Total |
|-----------|-------------|------------------|-------|
| `/shared/` | 200+ | 50+ | 250+ |
| `/apps/services/` | 500+ | 200+ | 700+ |
| `/packages/` | 50+ | 300+ | 350+ |
| `/.github/workflows/` | - | - | 37 |

### Documentation Files

| Directory | MD Files |
|-----------|----------|
| `/docs/` | 109+ |
| Service READMEs | 50+ |
| Package READMEs | 20+ |

---

**Generated:** 2026-01-24
**Audit Method:** Parallel agent exploration
**License:** Proprietary - KAFAAT © 2026
