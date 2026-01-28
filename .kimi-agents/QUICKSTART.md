# Kimi Repair Agent - Quick Start Guide
# دليل البدء السريع - وكيل إصلاح Kimi

## 🚀 Quick Start | البدء السريع

### 1. Configuration | الإعدادات

The Kimi Repair Agent is already configured and ready to use. Configuration is located at:

```
.kimi-agents/repair-agent-config.yaml
```

### 2. Environment Setup (Optional) | إعداد البيئة (اختياري)

If using Kimi AI API (optional):

```bash
# Set your Kimi API key
export KIMI_API_KEY="your-kimi-api-key-here"
```

**Note**: Kimi AI integration is optional. The system works with existing auto-fix infrastructure even without Kimi API.

### 3. Run Manual Scan | تشغيل الفحص اليدوي

```bash
# Full project scan
./scripts/kimi-repair-scan.sh

# Scan with auto-apply (requires review)
./scripts/kimi-repair-scan.sh --auto-apply

# Dry run (no changes)
./scripts/kimi-repair-scan.sh --dry-run
```

### 4. View Reports | عرض التقارير

Reports are generated in `/tmp/`:

```bash
# Markdown report
cat /tmp/kimi-report.md

# HTML report (if pandoc is installed)
open /tmp/kimi-report.html

# JSON report
cat /tmp/kimi-report.json
```

### 5. Generate Metrics | إنشاء المقاييس

```bash
# Generate metrics dashboard
python scripts/kimi-metrics-dashboard.py

# With sample data for testing
python scripts/kimi-metrics-dashboard.py --add-sample-data

# View chart
open /tmp/kimi-metrics.png
```

## 🔧 Configuration Options | خيارات الإعدادات

### Enable/Disable Kimi Agent

Edit `.kimi-agents/repair-agent-config.yaml`:

```yaml
agent:
  enabled: true  # Set to false to disable
  fallback_enabled: true  # Use existing auto-fix if Kimi unavailable
```

### Configure Detected Issues

```yaml
detected_issues:
  - id: "ec_as_nutrient"
    enabled: true  # Enable/disable specific issue detection
    severity: "critical"
```

### Configure Monitored Services

```yaml
monitored_projects:
  - path: "apps/services/agro-advisor"
    priority: "high"
    specialized_agent: "agro_advisor_agent"
```

## 🤖 Specialized Agents | الوكلاء المتخصصون

### Agro Advisor EC Repair Agent

Detects EC misuse in agricultural services:

```bash
# Run specialized agent
python apps/services/agro-advisor/.kimi/ec_repair_agent.py --scan

# Export results
python apps/services/agro-advisor/.kimi/ec_repair_agent.py \
  --scan \
  --export-json /tmp/ec-issues.json
```

## 📊 CI/CD Integration | تكامل CI/CD

### Automatic Scanning

The Kimi Repair Agent runs automatically on:

- **Push to main/develop**
- **Pull requests**
- **Daily at 2 AM UTC** (5 AM Riyadh time)

### Manual Trigger

Go to GitHub Actions → "Kimi Repair Agent" → "Run workflow"

Options:
- `auto_apply`: Create PR with fixes
- `scan_scope`: all, services, shared, mobile

### PR Review Bot

Automatically reviews PRs with:
- Code quality checks
- Security analysis
- Agricultural domain checks
- Bilingual comments

## 🔍 What Gets Scanned | ما يتم فحصه

### Python Services

- **Ruff**: Linting and formatting
- **Bandit**: Security vulnerabilities
- **Mypy**: Type checking
- **Pytest**: Test discovery

### TypeScript/JavaScript

- **ESLint**: Code quality
- **TypeScript**: Type checking

### Agricultural Domain

- **EC Misuse**: Incorrect use of EC for nutrients
- **ML Optimization**: GridSearch vs SBO
- **CV Pipelines**: Computer vision improvements

## ✅ Best Practices | أفضل الممارسات

### 1. Review Before Applying

Always review auto-generated fixes before applying:

```yaml
agent:
  auto_apply_fixes: false  # Require human review
```

### 2. Enable Safe Mode

```yaml
security:
  safe_mode: true  # Extra validation
```

### 3. Regular Scans

Run scans regularly (daily scheduled):

```yaml
ci_integration:
  scheduled_scans:
    enabled: true
    cron: "0 2 * * *"
```

### 4. Monitor Metrics

Check metrics regularly:

```bash
python scripts/kimi-metrics-dashboard.py
```

## 🐛 Troubleshooting | استكشاف الأخطاء

### Kimi Agent Not Running

1. Check configuration:
   ```bash
   cat .kimi-agents/repair-agent-config.yaml | grep "enabled:"
   ```

2. Verify workflow:
   ```bash
   ls -la .github/workflows/kimi-*.yml
   ```

### No Reports Generated

1. Check output directory:
   ```bash
   ls -la /tmp/kimi-*
   ```

2. Run with verbose logging:
   ```bash
   DEBUG=1 ./scripts/kimi-repair-scan.sh
   ```

### Fixes Not Applied

1. Check auto-apply setting:
   ```yaml
   agent:
     auto_apply_fixes: false  # Default: require review
   ```

2. Check PR was created:
   ```bash
   git branch | grep kimi-auto
   ```

## 📚 Documentation | الوثائق

- **Main README**: `.kimi-agents/README.md`
- **Configuration**: `.kimi-agents/repair-agent-config.yaml`
- **Governance**: `governance/agents.yaml` (kimi-repair-agent)
- **Workflows**: `.github/workflows/kimi-*.yml`
- **Specialized Agents**: `apps/services/*/.kimi/README.md`

## 🔗 Integration Points | نقاط التكامل

### Existing Infrastructure

The Kimi agent integrates with:

1. **Auto-Fix Engine**: `shared/ai/auto_fix/`
2. **Code Fix Agent**: `apps/services/code-fix-agent/`
3. **Code Review Agent**: `apps/services/code-review-agent/`
4. **GitHub Actions**: 37 existing workflows

### Coordination

```yaml
integration:
  agent_coordination: "collaborative"  # All agents work together
  conflict_resolution: "prefer_kimi"   # How to resolve conflicts
```

## 💡 Tips | نصائح

1. **Start with Dry Run**: Test with `--dry-run` first
2. **Review All Changes**: Never blindly accept auto-fixes
3. **Use Specialized Agents**: Enable domain-specific agents
4. **Monitor Metrics**: Track improvements over time
5. **Configure Notifications**: Set up Slack/Teams webhooks

## 🎯 Next Steps | الخطوات التالية

1. ✅ Review configuration in `.kimi-agents/repair-agent-config.yaml`
2. ✅ Run first scan: `./scripts/kimi-repair-scan.sh`
3. ✅ Review reports in `/tmp/`
4. ✅ Enable specialized agents for your services
5. ✅ Configure CI/CD integration
6. ✅ Set up notifications (optional)

---

**Need Help?** | **تحتاج مساعدة؟**

- Check documentation in `docs/`
- Review governance in `governance/`
- Consult `CLAUDE.md` for AI integration guidelines

**Version**: 16.0.0  
**Last Updated**: January 2026  
**Maintainer**: SAHOOL Platform Team
