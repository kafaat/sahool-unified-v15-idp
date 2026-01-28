# SAHOOL Kimi Repair Agent
# وكيل إصلاح Kimi لمنصة سهول

## Overview | نظرة عامة

The Kimi Repair Agent is an AI-powered code analysis and repair system integrated into the SAHOOL platform. It works alongside existing auto-fix infrastructure to provide intelligent code review, bug detection, and automated fixes.

وكيل إصلاح Kimi هو نظام ذكي لتحليل وإصلاح الكود متكامل مع منصة سهول. يعمل جنباً إلى جنب مع البنية التحتية الموجودة للإصلاح التلقائي لتوفير مراجعة ذكية للكود واكتشاف الأخطاء والإصلاحات التلقائية.

## Features | الميزات

### 🔍 Intelligent Code Analysis
- **Domain-Specific Detection**: Agricultural domain issue detection (EC misuse, ML optimization)
- **Multi-Tool Integration**: Ruff, ESLint, Mypy, Bandit, and more
- **Bilingual Support**: Arabic and English reports and suggestions

### 🔧 Automated Repair
- **Safe Fixes**: Human-reviewed before application
- **Multiple Strategies**: Minimal, Safe, Comprehensive, Refactor
- **Specialized Agents**: Domain-specific repair agents for agro-advisor and yield-prediction

### 🤖 AI Integration
- **Kimi AI**: Optional Kimi AI provider integration
- **Fallback Support**: Falls back to existing auto-fix infrastructure
- **Multiple Providers**: Support for Kimi, OpenAI, Ollama, Anthropic

## Configuration | الإعدادات

### Main Configuration File
Location: `.kimi-agents/repair-agent-config.yaml`

Key sections:
- **Agent Settings**: Model, mode, language preferences
- **Detected Issues**: Configurable issue detection (EC misuse, ML optimization, security, etc.)
- **Scan Tools**: Python, TypeScript, Dart tool configuration
- **Monitored Projects**: Services and paths to monitor
- **CI/CD Integration**: GitHub Actions, PR settings, notifications
- **Specialized Agents**: Domain-specific agent configuration

### Environment Variables

```bash
# Required for Kimi AI (optional)
export KIMI_API_KEY="your-kimi-api-key"

# Optional notification webhooks
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
```

## Usage | الاستخدام

### 1. Enable/Disable Kimi Agent

Edit `.kimi-agents/repair-agent-config.yaml`:
```yaml
agent:
  enabled: true  # Set to false to disable
  fallback_enabled: true  # Use existing auto-fix if Kimi unavailable
```

### 2. Run Manual Scan

```bash
# Using the scan script (when implemented)
./scripts/kimi-repair-scan.sh

# Or use existing auto-fix infrastructure
python -m shared.ai.auto_fix.diagnostic_cli --all --fix
```

### 3. CI/CD Integration

The Kimi agent automatically runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch
- Scheduled daily at 2 AM UTC

Configure in: `.github/workflows/kimi-repair.yml`

### 4. Specialized Agents

Enable domain-specific agents for targeted services:

**Agro Advisor Agent**: Detects EC misuse in agricultural calculations
```yaml
specialized_agents:
  agro_advisor_agent:
    enabled: true  # Monitors apps/services/agro-advisor
```

**Yield Prediction Agent**: Optimizes ML models
```yaml
specialized_agents:
  yield_prediction_agent:
    enabled: true  # Monitors yield-prediction services
```

**Computer Vision Agent**: Improves CV pipelines
```yaml
specialized_agents:
  cv_specialist_agent:
    enabled: true  # Monitors crop-intelligence services
```

## Integration with Existing Infrastructure | التكامل مع البنية الموجودة

### Existing Auto-Fix Engine
The Kimi agent is designed to work with `shared/ai/auto_fix`:

```yaml
integration:
  use_existing_auto_fix: true
  auto_fix_path: "shared/ai/auto_fix"
```

### Existing Code Fix Agent
Coordinates with `apps/services/code-fix-agent`:

```yaml
integration:
  use_existing_code_fix_agent: true
  code_fix_agent_endpoint: "http://code-fix-agent:8161"
```

### Existing Code Review Agent
Works with `apps/services/code-review-agent`:

```yaml
integration:
  use_existing_code_review_agent: true
  code_review_agent_endpoint: "http://code-review-agent:8162"
```

### Coordination Modes
- `collaborative`: All agents work together
- `sequential`: One after another
- `parallel`: Run simultaneously

## Detected Issues | المشكلات المكتشفة

### Agricultural Domain Issues
1. **EC as Nutrient Indicator** (Critical)
   - Pattern: Using EC value for NPK calculation
   - Fix: Use actual lab results instead

2. **Unoptimized ML Models** (High)
   - Pattern: GridSearchCV usage
   - Fix: Replace with SBO optimizer + Boruta

3. **Missing CV Pipeline** (High)
   - Pattern: Basic object detection
   - Fix: Implement MWG-YOLO architecture

### Code Quality Issues
1. **Security Vulnerabilities** (Critical)
2. **Performance Bottlenecks** (Medium)
3. **Code Style Violations** (Low)
4. **Missing Tests** (Medium, disabled by default)

## Output & Reports | التقارير والمخرجات

### Report Formats
- **HTML**: `/tmp/kimi-report.html` - Human-readable
- **JSON**: `/tmp/kimi-report.json` - Machine-readable
- **Markdown**: `/tmp/kimi-report.md` - Documentation
- **SARIF**: `/tmp/kimi-security.sarif` - GitHub Security Alerts
- **Patch**: `/tmp/kimi-fixes.patch` - Git patch file

### Metrics Database
Location: `/tmp/kimi-metrics.db`
Retention: 90 days

## Security | الأمان

### API Key Management
- Store in environment variable `KIMI_API_KEY`
- Never commit keys to repository
- Use GitHub Secrets for CI/CD

### Safe Mode
```yaml
security:
  safe_mode: true  # Extra validation before fixes
  prevent_secret_leaks: true
```

### Audit Trail
All operations logged to: `/var/log/kimi-agent/audit.log`

## Customization | التخصيص

### Add New Issue Detection

Edit `.kimi-agents/repair-agent-config.yaml`:
```yaml
detected_issues:
  - id: "my_custom_issue"
    severity: "high"
    description: "My custom issue description"
    description_ar: "وصف المشكلة المخصصة"
    enabled: true
```

### Add New Specialized Agent

```yaml
specialized_agents:
  my_custom_agent:
    name: "My Custom Agent"
    name_ar: "الوكيل المخصص"
    enabled: true
    focus_areas:
      - "custom_domain"
    patterns:
      - regex: "pattern_to_detect"
        suggestion: "Suggestion for fix"
        severity: "medium"
```

## Troubleshooting | استكشاف الأخطاء

### Kimi Agent Not Running
1. Check `agent.enabled: true` in config
2. Verify `KIMI_API_KEY` is set (if using Kimi AI)
3. Check workflow files in `.github/workflows/`

### Fixes Not Applied
1. Verify `auto_apply_fixes: false` - requires manual review
2. Check PR was created in GitHub
3. Review logs in `/var/log/kimi-agent/audit.log`

### Fallback to Existing Auto-Fix
If Kimi is unavailable, the system automatically falls back to existing auto-fix infrastructure when `fallback_enabled: true`.

## Directory Structure | هيكل المجلد

```
.kimi-agents/
├── README.md                    # This file
├── repair-agent-config.yaml    # Main configuration
└── templates/                   # Agent templates (future)
```

## Related Documentation | الوثائق ذات الصلة

- **Auto-Fix Engine**: `shared/ai/auto_fix/`
- **Code Fix Agent**: `apps/services/code-fix-agent/`
- **Code Review Agent**: `apps/services/code-review-agent/`
- **Governance**: `governance/agents.yaml`
- **CI/CD Workflows**: `.github/workflows/`

## Support | الدعم

For issues and questions:
1. Check existing documentation in `docs/`
2. Review governance files in `governance/`
3. Consult `CLAUDE.md` for AI integration guidelines

---

**Version**: 16.0.0  
**Last Updated**: January 2026  
**Maintainer**: SAHOOL Platform Team
