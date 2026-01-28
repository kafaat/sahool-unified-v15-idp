# Kimi Repair Agent - Integration Guide
# دليل التكامل - وكيل إصلاح Kimi

## 🎯 Overview | نظرة عامة

This document describes how the Kimi Repair Agent integrates with the existing SAHOOL platform infrastructure.

يصف هذا المستند كيفية تكامل وكيل إصلاح Kimi مع البنية التحتية الموجودة لمنصة سهول.

## 🏗️ Architecture | البنية المعمارية

### Integration Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kimi Repair Agent Layer                      │
│  (Optional AI Provider - Kimi, OpenAI, Ollama, Anthropic)      │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│              SAHOOL Auto-Fix Infrastructure                      │
│  shared/ai/auto_fix/ - Existing diagnostic & fix engine         │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                   Analysis Tools Layer                           │
│  Ruff, ESLint, Mypy, Bandit, Semgrep, Dart Analyze             │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                Service-Specific Agents                           │
│  agro-advisor, yield-prediction, crop-intelligence              │
└─────────────────────────────────────────────────────────────────┘
```

### Component Integration

#### 1. Configuration System

**Location**: `.kimi-agents/repair-agent-config.yaml`

```yaml
integration:
  # Use existing infrastructure
  use_existing_auto_fix: true
  auto_fix_path: "shared/ai/auto_fix"
  
  # Coordinate with existing agents
  use_existing_code_fix_agent: true
  code_fix_agent_endpoint: "http://code-fix-agent:8161"
  
  use_existing_code_review_agent: true
  code_review_agent_endpoint: "http://code-review-agent:8162"
  
  # How agents work together
  agent_coordination: "collaborative"
```

#### 2. Existing Auto-Fix Engine

**Location**: `shared/ai/auto_fix/`

The Kimi agent leverages the existing auto-fix infrastructure:

```python
from shared.ai.auto_fix import AutoFixEngine, quick_diagnose, quick_fix

# Kimi uses the existing engine
engine = AutoFixEngine(dry_run=False)
report = await engine.diagnose("apps/services/")
fixes = await engine.apply_fix_plan(plan, report)
```

**Key Classes**:
- `AutoFixEngine`: Main orchestration
- `CodeDiagnostics`: Multi-tool diagnostics
- `CodeFixer`: Automated fixing
- `AutoAudit`: Audit trail integration

#### 3. Code Fix Agent Service

**Location**: `apps/services/code-fix-agent/`

The Kimi agent coordinates with the existing code-fix-agent:

```yaml
# In governance/agents.yaml
code-fix-agent:
  endpoint: "https://api.sahool.app/agents/code-fix/invoke"
  capabilities:
    - analyze_code
    - fix_code
    - generate_tests
```

**Integration**:
- Kimi can delegate complex fixes to code-fix-agent
- code-fix-agent provides AI-powered analysis
- Results are merged and reported together

#### 4. Code Review Agent Service

**Location**: `apps/services/code-review-agent/`

```yaml
# In governance/agents.yaml
code-review-agent:
  endpoint: "https://api.sahool.app/agents/code-review/invoke"
  capabilities:
    - review_code
    - security_scan
    - performance_analysis
```

**Integration**:
- Kimi PR review uses code-review-agent insights
- Bilingual review comments
- Comprehensive analysis reports

## 🔄 Workflow Integration | تكامل سير العمل

### 1. CI/CD Integration

#### GitHub Actions Workflow Triggers

```yaml
# .github/workflows/kimi-repair.yml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: "0 2 * * *"  # Daily at 2 AM UTC
  workflow_dispatch:
```

#### Workflow Sequence

```
1. Config Check
   ↓
2. Kimi Scan (uses existing auto-fix)
   ↓
3. Generate Reports
   ↓
4. Upload Artifacts
   ↓
5. Create PR (if auto-apply)
   ↓
6. Notify (GitHub, Slack, Teams)
```

### 2. Pre-Commit Hook (Optional)

**Installation**:
```bash
cp .kimi-agents/templates/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Integration**:
- Runs before git commit
- Checks staged files only
- Blocks CRITICAL issues (EC misuse)
- Can be bypassed with `git commit --no-verify`

### 3. PR Review Automation

**Flow**:
```
PR Opened/Updated
   ↓
Analyze Changed Files
   ↓
Run Code Analysis (Ruff, Bandit, etc.)
   ↓
Check Agricultural Domain Issues
   ↓
Generate Bilingual Review
   ↓
Post Comment on PR
```

## 🔌 Service Integration | تكامل الخدمات

### Monitored Services

Configuration in `.kimi-agents/repair-agent-config.yaml`:

```yaml
monitored_projects:
  # High Priority - Specialized Agents
  - path: "apps/services/agro-advisor"
    priority: "high"
    specialized_agent: "agro_advisor_agent"
    
  - path: "apps/services/yield-prediction"
    priority: "high"
    specialized_agent: "yield_prediction_agent"
    
  - path: "apps/services/crop-intelligence-service"
    priority: "high"
    specialized_agent: "cv_specialist_agent"
  
  # Medium Priority - General Scanning
  - path: "apps/services/vegetation-analysis-service"
    priority: "medium"
  
  # Mobile & Frontend
  - path: "apps/mobile/sahool_field_app"
    priority: "high"
    language: "dart"
```

### Specialized Agent Activation

Specialized agents are invoked based on service path:

```bash
# When scanning agro-advisor
if [[ "$service_path" == *"agro-advisor"* ]]; then
  python apps/services/agro-advisor/.kimi/ec_repair_agent.py --scan
fi
```

## 📊 Data Flow | تدفق البيانات

### Scan Flow

```
Source Code
   ↓
[Kimi Scan Script]
   ↓
[Analysis Tools: Ruff, Bandit, Mypy, ESLint]
   ↓
[Existing Auto-Fix Engine]
   ↓
[Specialized Agents (if applicable)]
   ↓
[Kimi AI (optional)]
   ↓
Reports & Fixes
   ↓
[GitHub PR or Artifacts]
```

### Configuration Flow

```
.kimi-agents/repair-agent-config.yaml
   ↓
[Kimi Scan Script reads config]
   ↓
[Determines enabled tools & services]
   ↓
[Routes to appropriate agents/tools]
   ↓
[Collects and merges results]
```

## 🔒 Security Integration | التكامل الأمني

### Secrets Management

```yaml
# In GitHub repository secrets
KIMI_API_KEY: "sk-***"  # Optional, for Kimi AI
SLACK_WEBHOOK_URL: "https://..."  # Optional notifications
```

### Audit Trail

All operations logged to:
- `/var/log/kimi-agent/audit.log`
- `shared/ai/auto_fix` audit system
- GitHub Actions logs

### Safe Mode

```yaml
security:
  safe_mode: true
  prevent_secret_leaks: true
  api_key_env: "KIMI_API_KEY"
```

## 🎛️ Configuration Management | إدارة الإعدادات

### Centralized Configuration

**Main Config**: `.kimi-agents/repair-agent-config.yaml`

**Governance**: `governance/agents.yaml` - kimi-repair-agent entry

**Environment**:
```bash
# Optional environment variables
export KIMI_API_KEY="..."
export AUTO_APPLY_FIXES="false"
export KIMI_CONFIG=".kimi-agents/repair-agent-config.yaml"
```

### Agent Coordination Modes

```yaml
integration:
  agent_coordination: "collaborative"
```

**Modes**:
- `collaborative`: All agents work together simultaneously
- `sequential`: One after another (code-fix → kimi → code-review)
- `parallel`: Run independently, merge results

### Conflict Resolution

```yaml
integration:
  conflict_resolution: "prefer_kimi"
```

**Strategies**:
- `prefer_kimi`: Kimi suggestions take precedence
- `prefer_existing`: Existing auto-fix takes precedence
- `merge`: Combine suggestions from all agents

## 📈 Metrics Integration | تكامل المقاييس

### Data Collection

```python
# Metrics collected to SQLite database
db_path = "/tmp/kimi-metrics.db"

# Tables:
# - issues: Detected issues
# - scans: Scan operations
# - fixes: Applied fixes
```

### Visualization

```bash
# Generate metrics dashboard
python scripts/kimi-metrics-dashboard.py

# Output:
# - /tmp/kimi-metrics.png (chart)
# - /tmp/kimi-metrics-report.json (data)
```

### Prometheus Integration (Future)

```yaml
# Potential metrics endpoint
/metrics
  - kimi_scans_total
  - kimi_issues_found
  - kimi_fixes_applied
  - kimi_scan_duration_seconds
```

## 🧪 Testing Integration | تكامل الاختبارات

### Test the Integration

```bash
# 1. Verify configuration
cat .kimi-agents/repair-agent-config.yaml | grep "enabled:"

# 2. Run manual scan
./scripts/kimi-repair-scan.sh --dry-run

# 3. Check specialized agent
python apps/services/agro-advisor/.kimi/ec_repair_agent.py --scan

# 4. Verify workflow syntax
yamllint .github/workflows/kimi-*.yml

# 5. Test pre-commit hook
.kimi-agents/templates/pre-commit
```

## 🔧 Troubleshooting Integration | استكشاف أخطاء التكامل

### Common Integration Issues

#### 1. Kimi Not Running

**Check**:
```bash
# Verify enabled in config
grep "enabled:" .kimi-agents/repair-agent-config.yaml

# Check workflow files
ls -la .github/workflows/kimi-*.yml
```

#### 2. Conflicts with Existing Auto-Fix

**Solution**:
```yaml
# Set coordination mode
integration:
  agent_coordination: "collaborative"
  conflict_resolution: "merge"
```

#### 3. Missing Dependencies

**Fix**:
```bash
# Install Python tools
pip install ruff mypy bandit

# Install Node tools
npm install eslint
```

## 📚 Documentation References | مراجع التوثيق

### Existing Infrastructure

- **Auto-Fix**: `shared/ai/auto_fix/README.md`
- **Code Fix Agent**: `apps/services/code-fix-agent/README.md`
- **Code Review Agent**: `apps/services/code-review-agent/README.md`
- **Governance**: `governance/agents.yaml`

### Kimi Documentation

- **Main README**: `.kimi-agents/README.md`
- **Quick Start**: `.kimi-agents/QUICKSTART.md`
- **Configuration**: `.kimi-agents/repair-agent-config.yaml`
- **Specialized Agent**: `apps/services/agro-advisor/.kimi/README.md`

## 🎯 Best Practices | أفضل الممارسات

### 1. Enable Fallback

```yaml
agent:
  fallback_enabled: true  # Use existing auto-fix if Kimi unavailable
```

### 2. Coordinate Agents

```yaml
integration:
  agent_coordination: "collaborative"
```

### 3. Review Before Apply

```yaml
agent:
  auto_apply_fixes: false
  auto_merge_prs: false
```

### 4. Monitor Metrics

```bash
# Regular monitoring
python scripts/kimi-metrics-dashboard.py --days 30
```

### 5. Use Specialized Agents

Enable domain-specific agents for critical services:
```yaml
specialized_agents:
  agro_advisor_agent:
    enabled: true
```

---

**Version**: 16.0.0  
**Last Updated**: January 2026  
**Maintainer**: SAHOOL Platform Team
