# ADR-009: Claude Code Workflow Integration

| Item | Details |
|------|---------|
| **Status** | Accepted |
| **Date** | 2026-03-11 |
| **Authors** | SAHOOL Platform Team |
| **Reviewers** | Platform Architecture Team, DevEx Team |

## Context

SAHOOL is a national agricultural intelligence platform with a large and complex codebase:

1. **72 microservices** across Python (FastAPI) and Node.js (NestJS)
2. **80 shared Python modules** covering agricultural domains, AI, and infrastructure
3. **27 npm workspace packages** for shared types, UI components, and utilities
4. **Flutter mobile app** with 57 feature modules and offline-first architecture
5. **537+ documentation files** across multiple directories

Developers need AI assistance for navigating cross-service dependencies, maintaining quality standards across languages, and onboarding to domain-specific agricultural logic. Manual code review and documentation cannot scale with the platform's growth rate.

## Decision

### 1. CLAUDE.md as Single Source of Context

We adopt a centralized `CLAUDE.md` file (112 KB) at the repository root as the single source of project context for Claude Code. This file contains:

- Complete repository structure and technology stack
- Service registry with ports, types, and descriptions
- Development commands and Docker build conventions
- API conventions, event architecture, and security patterns
- Testing guidelines and environment configuration

**Rationale**: A single file eliminates context fragmentation and ensures Claude Code has consistent, up-to-date platform knowledge without requiring multiple file reads.

### 2. AI Skills Architecture

We organize Claude Code skills into 4 categories under `.claude/skills/`:

- **Context Engineering**: Memory management, token compression, LLM-as-Judge evaluation
- **SAHOOL Domain**: Crop advisory generation, farm documentation
- **Obsidian Documentation**: Markdown formatting, canvas-based knowledge graphs
- **Development**: Code review patterns, service scaffolding, test generation

Each skill is a standalone markdown module that can be invoked independently or composed into workflows.

### 3. MCP Server Integration

Claude Code connects to SAHOOL's MCP server (`apps/services/mcp-server/`, port 8201) for live platform data access including:

- Service health status and dependency graphs
- Database schema introspection
- NATS event catalog and subscription state
- Real-time metrics from Prometheus

### 4. Development Workflow Integration

Claude Code is integrated into four primary development workflows:

- **Code Review**: Cross-service impact analysis, convention compliance checks
- **Service Scaffolding**: Generate new services from IDP templates with correct ports, events, and health endpoints
- **Test Generation**: Create unit, integration, and smoke tests following existing patterns
- **Documentation**: Generate and update service docs, API specs, and migration guides

### 5. Bilingual Support Requirement

All Claude Code-generated content must support Arabic and English:

- Documentation includes both `title` and `title_ar` fields
- Error messages follow the bilingual pattern in `shared/errors_py.py`
- Advisory output uses the established `summary` / `summary_ar` convention
- Code comments remain in English; user-facing strings must be bilingual

### 6. Security Boundaries

Claude Code operates within defined security guardrails:

- **No secrets access**: Cannot read `.env` files, Vault tokens, or credential stores
- **RBAC awareness**: Respects role-based patterns when generating auth code
- **Audit logging**: All AI-assisted code changes are traceable via conventional commits with `claude/` branch prefix
- **No production access**: Claude Code cannot execute commands against production infrastructure

## Consequences

### Positive
- Faster developer onboarding (platform context available in single file)
- Consistent code quality across 72 services and 3 languages
- Bilingual documentation generated automatically
- Reduced manual effort for cross-service dependency analysis
- Standardized service scaffolding following IDP templates

### Negative
- CLAUDE.md maintenance overhead as platform evolves (must stay synchronized)
- Skill module complexity increases with domain-specific agricultural logic
- Dependency on Claude Code availability for optimized workflows

### Risks
- Context window limits may truncate CLAUDE.md for very large queries
- LLM hallucination risk in domain-specific agricultural advice (mitigated by LLM-as-Judge evaluation)
- Generated code may not account for undocumented service behaviors

## References

- CLAUDE.md - Project context file (repository root)
- `.claude/skills/` - AI skills architecture
- ADR-008 - AI Architecture & Model Selection
- Backstage IDP Templates - `idp/templates/`
- MCP Server - `apps/services/mcp-server/`
- Conventional Commits - Git workflow standard
