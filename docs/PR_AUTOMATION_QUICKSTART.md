# PR Automation Quick Start Guide

Get started with automated PR merging in 5 minutes.

## Prerequisites

- GitHub CLI installed (`gh`)
- Git configured
- Repository access

## Quick Start

### 1. Verify Setup

```bash
# Check GitHub CLI auth
gh auth status

# Check repository
cd /path/to/sahool-unified-v15-idp
git status
```

### 2. Test with Dry Run

```bash
# Test merging a single PR (safe, no actual merge)
./scripts/auto-merge-prs.sh --pr 123 --dry-run

# Output shows what would happen:
# ✓ PR #123 passed status checks
# ✓ No conflicts detected
# ✓ Tests passed
# ⚠️ Dry run: would merge PR #123
```

### 3. Merge Your First PR

```bash
# After verifying dry-run looks good
./scripts/auto-merge-prs.sh --pr 123

# Or via GitHub Actions:
# Go to Actions → Auto-Merge PRs → Run workflow
# Enter PR number: 123
# Select options
# Click "Run workflow"
```

## Common Use Cases

### Use Case 1: Merge Ready PRs

**Scenario**: You have PRs that passed CI and have approvals

```bash
# List open PRs
gh pr list --state open

# Check specific PR
gh pr view 123

# Merge it
./scripts/auto-merge-prs.sh --pr 123
```

### Use Case 2: Resolve Conflicts

**Scenario**: PR has merge conflicts

```bash
# Auto-resolve conflicts (keep PR version)
./scripts/auto-merge-prs.sh --pr 456 --conflict ours

# Or use intelligent auto-resolution
./scripts/auto-merge-prs.sh --pr 456 --conflict auto
```

### Use Case 3: Batch Process PRs

**Scenario**: Multiple PRs ready to merge

```bash
# Test first
./scripts/auto-merge-prs.sh --all --dry-run

# Review output, then merge
./scripts/auto-merge-prs.sh --all
```

### Use Case 4: Monitor PR Health

**Scenario**: Check status of all open PRs

```bash
# Via GitHub Actions:
# Go to Actions → PR Status Monitor → Run workflow

# Check generated report in workflow artifacts
```

## Merge Strategies Cheat Sheet

| Strategy | Use When | Result |
|----------|----------|--------|
| `auto` | Not sure | Best strategy chosen automatically |
| `merge` | Feature branch | Merge commit with full history |
| `squash` | Many commits | Single commit, clean history |
| `rebase` | Linear history | Replay commits on base |

Example:

```bash
# Squash merge for clean history
./scripts/auto-merge-prs.sh --pr 789 --strategy squash
```

## Conflict Resolution Cheat Sheet

| Strategy | Use When | Result |
|----------|----------|--------|
| `auto` | Common files | Smart resolution based on file type |
| `ours` | Feature branch | Keep PR changes |
| `theirs` | Hotfix to main | Keep base branch |
| `manual` | Complex | Skip auto-resolution |

Example:

```bash
# Keep PR version for feature branch
./scripts/auto-merge-prs.sh --pr 101 --conflict ours
```

## Labels for Auto-Merge

Add labels to PRs for automatic processing:

```bash
# Via GitHub CLI
gh pr edit 123 --add-label "auto-merge"

# Or via GitHub UI:
# 1. Go to PR
# 2. Add label "auto-merge" or "ready-to-merge"
# 3. Workflow triggers automatically
```

## Safety Tips

✅ **DO:**
- Use `--dry-run` first
- Check CI status
- Get code reviews
- Test locally for critical changes

❌ **DON'T:**
- Skip approvals for production
- Merge failing CI
- Force-merge without reviewing
- Use `theirs` for feature branches

## Troubleshooting

### Problem: "gh: command not found"

**Solution**: Install GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
winget install GitHub.cli
```

### Problem: "Not authenticated"

**Solution**: Login to GitHub CLI

```bash
gh auth login
# Follow prompts
```

### Problem: "Permission denied"

**Solution**: Check repository permissions

```bash
gh repo view
# Verify you have write access
```

### Problem: "Merge failed"

**Solution**: Check logs

```bash
# View detailed logs
cat auto-merge-*.log

# Check merge reports
ls -l merge-reports/
```

## Advanced Features

### Custom Approval Requirements

```bash
# Merge without approvals (use cautiously)
./scripts/auto-merge-prs.sh --pr 123 --no-approvals
```

### Scheduled Merges

Enable scheduled runs in `.github/workflows/auto-merge-prs.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

### Notifications

Enable notifications in PR Status Monitor:

```bash
gh workflow run pr-status-monitor.yml -f send_notifications=true
```

## Next Steps

1. Read full documentation: [docs/PR_AUTOMATION.md](./PR_AUTOMATION.md)
2. Review merge reports regularly
3. Set up scheduled monitoring
4. Customize merge strategies per project

## Support

- 📚 Full docs: [docs/PR_AUTOMATION.md](./PR_AUTOMATION.md)
- 🐛 Report issues: Add `auto-merge` label
- 💬 Questions: Create discussion in repo

---

**Happy Merging! 🎉**
