# Pull Request Automation System

Comprehensive automation for resolving conflicts, verifying correctness, and merging pull requests in the SAHOOL platform.

## Overview

The PR Automation System provides:

- **Automated Conflict Resolution**: Intelligently resolves merge conflicts using configurable strategies
- **Comprehensive Testing**: Runs tests before merging to ensure code quality
- **Smart Merge Strategies**: Supports merge, squash, and rebase strategies
- **Safety Checks**: Requires CI/CD checks to pass and minimum approvals
- **Status Monitoring**: Continuously monitors PR health and sends notifications
- **Detailed Reporting**: Generates audit trails for all merge operations

## Components

### 1. Auto-Merge Workflow (`.github/workflows/auto-merge-prs.yml`)

**Purpose**: Automates the entire PR merge process from conflict resolution to final merge.

**Triggers**:
- Manual dispatch (workflow_dispatch) with PR selection
- PR labeled with `auto-merge` or `ready-to-merge`
- Optional scheduled runs (disabled by default)

**Features**:
- Process individual PRs or all open PRs
- Multiple merge strategies (auto, merge, squash, rebase)
- Automatic conflict resolution (auto, ours, theirs)
- Requires all CI checks to pass
- Optional approval requirements
- Dry-run mode for testing
- Detailed merge reports

**Usage**:

```bash
# Via GitHub UI:
# 1. Go to Actions → Auto-Merge PRs → Run workflow
# 2. Enter PR numbers (e.g., "123,456" or "all")
# 3. Select merge and conflict strategies
# 4. Choose dry-run for testing
# 5. Click "Run workflow"

# Via GitHub CLI:
gh workflow run auto-merge-prs.yml \
  -f pr_numbers="123,456" \
  -f merge_strategy="auto" \
  -f conflict_strategy="auto" \
  -f require_approvals=true \
  -f dry_run=false
```

### 2. Auto-Merge Script (`scripts/auto-merge-prs.sh`)

**Purpose**: Command-line tool for automated PR merging with full control.

**Features**:
- Fetch and process open PRs
- Automatic conflict detection and resolution
- Pre-merge testing
- Multiple merge strategies
- Detailed logging and reporting
- Safety checks

**Usage**:

```bash
# Merge specific PR
./scripts/auto-merge-prs.sh --pr 123

# Merge all open PRs (dry-run first!)
./scripts/auto-merge-prs.sh --all --dry-run

# Merge with squash strategy
./scripts/auto-merge-prs.sh --pr 456 --strategy squash

# Auto-resolve conflicts keeping PR version
./scripts/auto-merge-prs.sh --pr 789 --conflict ours

# Merge without requiring approvals
./scripts/auto-merge-prs.sh --pr 101 --no-approvals
```

**Options**:

| Option | Description | Default |
|--------|-------------|---------|
| `--pr <number>` | Merge specific PR number | - |
| `--all` | Merge all open PRs | - |
| `--strategy <type>` | Merge strategy: auto\|merge\|squash\|rebase | auto |
| `--conflict <type>` | Conflict resolution: auto\|ours\|theirs | auto |
| `--require-approvals` | Require approvals before merge | true |
| `--no-approvals` | Don't require approvals | - |
| `--dry-run` | Test without actually merging | false |
| `--help` | Show help message | - |

### 3. PR Status Monitor (`.github/workflows/pr-status-monitor.yml`)

**Purpose**: Continuously monitors PR health and takes corrective actions.

**Triggers**:
- Scheduled (daily at 9 AM UTC)
- Manual dispatch
- On push to main/develop branches

**Features**:
- Monitor all open PRs for conflicts
- Auto-update PR branches from base branch
- Check CI status and approvals
- Track stale PRs (not updated in 7+ days)
- Generate daily PR health reports
- Create issues for PRs needing attention

**Usage**:

```bash
# Via GitHub UI:
# 1. Go to Actions → PR Status Monitor → Run workflow
# 2. Choose to auto-update branches
# 3. Choose to send notifications
# 4. Click "Run workflow"

# Via GitHub CLI:
gh workflow run pr-status-monitor.yml \
  -f auto_update=true \
  -f send_notifications=true
```

## Merge Strategies

### Auto (Recommended)

Automatically selects the best merge strategy based on PR characteristics:
- Single commit → Rebase
- Feature branch → Merge commit
- Hotfix → Squash

### Merge

Creates a merge commit preserving full branch history:
- ✅ Preserves all commits
- ✅ Shows branch topology
- ❌ More verbose history

### Squash

Combines all commits into a single commit:
- ✅ Clean, linear history
- ✅ Easy to revert
- ❌ Loses individual commit history

### Rebase

Replays commits on top of base branch:
- ✅ Linear history
- ✅ Preserves individual commits
- ❌ Rewrites history (requires force-push)

## Conflict Resolution Strategies

### Auto (Recommended)

Intelligently resolves conflicts based on file types:

| File Type | Strategy | Reason |
|-----------|----------|--------|
| `*.lock`, `*.json`, `*.yaml` | Keep PR version | Configuration updates |
| `requirements.txt`, `package.json` | Keep PR version | Dependency updates |
| Other files | Keep PR version | Feature changes |

### Ours

Always keep the PR branch version:
- ✅ Preserves PR changes
- ✅ Simple and predictable
- ⚠️ May discard important base branch updates

### Theirs

Always keep the base branch version:
- ✅ Preserves base branch stability
- ⚠️ May discard PR changes
- ⚠️ Use with caution

### Manual

Skip auto-resolution and require manual intervention:
- ✅ Full control
- ❌ Requires manual work
- 👍 Best for complex conflicts

## Safety Measures

### CI/CD Checks

All CI/CD checks must pass before merge:
- ✅ Code quality (linting, formatting)
- ✅ Tests (unit, integration, e2e)
- ✅ Security scans (CodeQL, Semgrep)
- ✅ Build verification

### Approval Requirements

Configurable minimum approvals:
- Default: 1 approval required
- Can be disabled with `--no-approvals`
- Respects branch protection rules

### Protected Branches

Extra safety for main/develop branches:
- Requires all checks to pass
- Requires approvals
- No force-push allowed

### Rollback Mechanism

If merge causes issues:

```bash
# Find the merge commit
git log --oneline --merges -n 5

# Revert the merge
git revert -m 1 <merge-commit-sha>

# Push the revert
git push origin main
```

## Reports and Logging

### Merge Reports

Each PR merge generates a detailed report:

```markdown
# PR #123 Merge Report

**Date**: 2026-02-11 13:00:00 UTC
**PR**: #123 - Add new feature
**Status**: ✅ Merged

## Details

- **Head Branch**: feature/new-feature
- **Base Branch**: main
- **Merge Strategy**: auto
- **Conflict Strategy**: auto
- **Had Conflicts**: true
- **Conflicts Resolved**: true
- **Tests Passed**: true

## Outcome

✅ PR merged successfully
```

Reports are saved as artifacts and retained for 30 days.

### PR Health Reports

Daily reports show overall PR health:

```markdown
# Pull Request Health Report

**Generated**: 2026-02-11 09:00:00 UTC
**Total Open PRs**: 15

## Summary

- 🔴 **Conflicted PRs**: 3
- 🟠 **Failing CI**: 2
- 🟡 **Stale PRs**: 5
- 🟢 **Ready to Merge**: 5
```

### Logs

All operations are logged:

```bash
# View merge logs
cat auto-merge-*.log

# View reports
ls -l merge-reports/
```

## Configuration

### Environment Variables

```bash
# Minimum approvals required
MIN_APPROVALS=1

# Protected branches (comma-separated)
PROTECTED_BRANCHES="main,develop"

# GitHub token for authentication
GITHUB_TOKEN=<your-token>
```

### Workflow Inputs

All workflows accept inputs for customization:

```yaml
# Auto-Merge Workflow
pr_numbers: "all"           # PR numbers to merge
merge_strategy: "auto"      # Merge strategy
conflict_strategy: "auto"   # Conflict resolution
require_approvals: true     # Require approvals
dry_run: true              # Test mode

# PR Status Monitor
auto_update: false         # Auto-update branches
send_notifications: true   # Send notifications
```

## Best Practices

### Before Merging

1. **Review PR Changes**: Always review the diff before merging
2. **Check CI Status**: Ensure all checks pass
3. **Get Approvals**: Require at least 1 approval
4. **Test Locally**: For critical changes, test locally first
5. **Use Dry Run**: Test automation with `--dry-run` first

### When Conflicts Occur

1. **Understand Changes**: Review both sides of the conflict
2. **Choose Strategy Wisely**: 
   - Use `auto` for common cases
   - Use `ours` for feature branches
   - Use `theirs` for hotfixes to main
3. **Test After Resolution**: Always run tests after resolving conflicts
4. **Manual Review**: For complex conflicts, resolve manually

### For Production

1. **Require Approvals**: Always enable approval requirements
2. **Protect Branches**: Use branch protection for main/develop
3. **Monitor Status**: Enable PR status monitoring
4. **Review Reports**: Check merge reports regularly
5. **Use Auto-Update**: Keep PR branches up-to-date

## Troubleshooting

### "No PRs to process"

**Cause**: No open PRs or all PRs filtered out
**Solution**: Check PR list with `gh pr list --state open`

### "Insufficient approvals"

**Cause**: PR doesn't have required approvals
**Solution**: Get approvals or use `--no-approvals` flag (not recommended for production)

### "CI checks failed"

**Cause**: One or more CI checks are failing
**Solution**: Fix issues and re-run checks, or skip with `--dry-run` for testing

### "Failed to resolve conflicts"

**Cause**: Automatic conflict resolution failed
**Solution**: 
1. Try different conflict strategy (`ours` or `theirs`)
2. Resolve manually and commit
3. Re-run automation

### "Merge failed"

**Cause**: Various reasons (permissions, branch protection, etc.)
**Solution**: 
1. Check error message in logs
2. Verify GitHub token permissions
3. Check branch protection rules
4. Ensure PR is in mergeable state

## Examples

### Scenario 1: Merge Single PR

```bash
# 1. Check PR status
gh pr view 123

# 2. Test merge (dry-run)
./scripts/auto-merge-prs.sh --pr 123 --dry-run

# 3. Actual merge
./scripts/auto-merge-prs.sh --pr 123
```

### Scenario 2: Batch Merge Multiple PRs

```bash
# 1. List open PRs
gh pr list --state open

# 2. Test all PRs (dry-run)
./scripts/auto-merge-prs.sh --all --dry-run

# 3. Merge all ready PRs
./scripts/auto-merge-prs.sh --all
```

### Scenario 3: Merge with Conflicts

```bash
# 1. Check for conflicts
gh pr view 456

# 2. Merge with auto-resolution
./scripts/auto-merge-prs.sh --pr 456 --conflict auto

# 3. Or keep PR version
./scripts/auto-merge-prs.sh --pr 456 --conflict ours
```

### Scenario 4: Squash Merge Feature Branch

```bash
# Merge feature branch with squash
./scripts/auto-merge-prs.sh --pr 789 --strategy squash
```

### Scenario 5: Monitor PR Health

```bash
# Via GitHub Actions (manual trigger)
gh workflow run pr-status-monitor.yml -f auto_update=true
```

## Integration with CI/CD

The automation system integrates with existing CI/CD:

```yaml
# Example: Trigger auto-merge after successful CI
name: CI Pipeline
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # ... run tests ...
  
  auto-merge:
    needs: test
    if: |
      github.event.pull_request.draft == false &&
      contains(github.event.pull_request.labels.*.name, 'auto-merge')
    runs-on: ubuntu-latest
    steps:
      - name: Auto-merge PR
        uses: ./.github/workflows/auto-merge-prs.yml
        with:
          pr_numbers: ${{ github.event.pull_request.number }}
```

## Security Considerations

1. **GitHub Token**: Use fine-grained tokens with minimal permissions
2. **Branch Protection**: Enable branch protection for main/develop
3. **Code Review**: Always require code review before merge
4. **Security Scans**: Ensure CodeQL and other scans pass
5. **Audit Trail**: All merges are logged and reported

## Maintenance

### Regular Tasks

- **Weekly**: Review PR health reports
- **Monthly**: Clean up old merge reports
- **Quarterly**: Review and update merge strategies

### Updates

Update workflows and scripts as needed:

```bash
# Update auto-merge script
git pull origin main
chmod +x scripts/auto-merge-prs.sh
```

## Support

For issues or questions:

1. Check this documentation
2. Review workflow logs in GitHub Actions
3. Check merge reports in artifacts
4. Create an issue with the `auto-merge` label

## License

Proprietary - KAFAAT © 2026
