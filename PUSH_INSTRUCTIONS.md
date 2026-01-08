# Instructions to Resolve PR #388 Merge Conflicts

## Current Status
The merge conflicts in PR #388 have been **resolved locally** in the `claude/create-auto-audit-tools-qTNzb` branch.

## Local State
- Branch: `claude/create-auto-audit-tools-qTNzb`
- Current commit: `079b6309` - "Add merge conflict resolution documentation"
- Parent commit: `4a7a3b7f` - "Resolve merge conflicts with main branch"
- All 5 conflicts resolved

## To Complete the Fix

The resolved commits need to be pushed to the remote PR branch. Since the tool cannot push directly to the PR branch, one of these options should be used:

### Option 1: Force Push (if you have write access to the PR branch)
```bash
git push -f origin claude/create-auto-audit-tools-qTNzb
```

### Option 2: Create a new commit on the PR branch on GitHub
The owner of the PR branch should:
1. Pull the latest `main` branch
2. Merge `main` into `claude/create-auto-audit-tools-qTNzb` 
3. Resolve conflicts using the `--ours` strategy (keep HEAD versions)
4. Push the merge commit

### Option 3: Close and Recreate the PR
Create a new PR from the resolved branch.

## Files with Resolved Conflicts
1. ✅ apps/mobile/lib/core/http/api_client.dart
2. ✅ apps/mobile/lib/features/astronomical/providers/astronomical_providers.dart
3. ✅ apps/services/astronomical-calendar/src/main.py
4. ✅ infra/kong/kong.yml
5. ✅ infrastructure/gateway/kong/kong.yml

## Resolution Details
All conflicts were resolved by keeping the HEAD (PR branch) version, which uses the modern `EnvConfig` approach. See `MERGE_CONFLICT_RESOLUTION.md` for detailed information.

## Verification
After pushing, verify the PR status at:
https://github.com/kafaat/sahool-unified-v15-idp/pull/388

The PR should show as mergeable with no conflicts.
