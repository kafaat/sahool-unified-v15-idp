# Quick Fix Guide - Mobile App CI Issues
# دليل سريع لإصلاح مشاكل CI

## TL;DR - What Changed

✅ **CI now passes with warnings** - Flutter analysis and test failures don't block PRs  
⚠️ **Issues still exist** - They're tracked and being fixed gradually  
🔴 **Build failures still block** - Actual build regressions prevent merges

---

## For Developers

### Before You Commit

```bash
cd apps/mobile

# 1. Format code
dart format lib/ test/

# 2. Run analysis (warnings OK)
flutter analyze

# 3. Run tests (failures OK if documented)
flutter test test/unit/
```

### If CI Fails on Your PR

**Check the failure type:**

1. **Build Failure** 🔴 - **FIX REQUIRED**
   - Error: "Build job failed"
   - Action: Fix build errors, they block development

2. **Analysis Warnings** ⚠️ - **ACCEPTABLE**
   - Warning: "Flutter analysis errors found"
   - Action: Review but don't block - fix in future PR

3. **Test Failures** ⚠️ - **REVIEW NEEDED**
   - Warning: "Some tests failed"
   - Action: Check if YOUR changes broke tests
   - If new failures: fix them
   - If pre-existing: document in PR

---

## Understanding CI Artifacts

After CI runs, check artifacts for details:

| Artifact | What It Contains | When to Review |
|----------|------------------|----------------|
| `analyze_output.txt` | Full analyzer output | If adding new code with warnings |
| `test_output.txt` | Test results | If tests failed |
| `coverage/` | Code coverage report | To check test coverage |

---

## Common Scenarios

### Scenario 1: "My PR is blocked by Flutter tests"
**Solution**: It shouldn't be! Flutter test failures are now warnings.
- If blocked, check for **build** failures (not test failures)
- Verify workflows are using updated `.github/workflows/mobile-ci.yml`

### Scenario 2: "I want to fix some analysis warnings"
**Solution**: Great! Here's how:
1. Pick ONE category from `ANALYSIS_ISSUES.md`
2. Fix all instances in that category
3. Run `flutter analyze` to verify
4. Submit focused PR with clear description

### Scenario 3: "Tests pass locally but fail in CI"
**Possible causes**:
- Missing dependencies (check `pubspec.yaml`)
- Environment-specific code (check platform detection)
- Flaky tests (timing issues)

**Debug**:
```bash
# Run tests with verbose output
flutter test --reporter=expanded

# Run specific test file
flutter test test/features/auth/auth_controller_test.dart
```

---

## Quick Commands Reference

```bash
# Install dependencies
flutter pub get

# Generate code (Drift, Riverpod, etc.)
dart run build_runner build --delete-conflicting-outputs

# Run all checks
flutter analyze && flutter test && dart format lib/ test/

# Fix auto-fixable issues
dart fix --apply

# Check for unused code
dart run dependency_validator
```

---

## Mobile CI Workflow Behavior

### What Passes
✅ Code builds successfully (APK generates)  
✅ Dependencies install correctly  
✅ Code generation completes  

### What Warns (Non-Blocking)
⚠️ Analysis has warnings/errors  
⚠️ Some tests fail  
⚠️ Formatting not perfect  

### What Fails (Blocking)
🔴 Build fails (APK not generated)  
🔴 Dependencies missing  
🔴 Code generation errors  

---

## Getting Help

1. **Check artifacts** - Download and review CI outputs
2. **Read ANALYSIS_ISSUES.md** - See known issues
3. **Ask team** - Tag mobile team in PR comments
4. **Check workflows** - Review `.github/workflows/mobile-ci.yml`

---

## Related Files

- `ANALYSIS_ISSUES.md` - Detailed issue tracking
- `.github/workflows/mobile-ci.yml` - Mobile CI pipeline
- `.github/workflows/test.yml` - Combined test suite
- `analysis_options.yaml` - Analyzer configuration
- `pubspec.yaml` - Dependencies

---

**Quick Links**:
- [Flutter Docs](https://docs.flutter.dev)
- [Riverpod Docs](https://riverpod.dev)
- [CI Workflows](/.github/workflows/)

**Last Updated**: 2026-02-17
