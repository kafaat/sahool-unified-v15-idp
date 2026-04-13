# Prompt — Fix Flutter Android Build CI Flake

> Self-contained AI-agent prompt. Copy the **entire block between the
> `BEGIN PROMPT` and `END PROMPT` markers** into a new branch and paste
> it as the first message to your AI assistant. The prompt assumes the
> agent has shell + git access to a fresh checkout of
> `kafaat/sahool-unified-v15-idp`.

---

## When to use

Use this prompt when the **`Flutter - Android Build`** check (job in
`.github/workflows/frontend-tests.yml`, also `Build Sahool APK` in
`.github/workflows/flutter-apk.yml`) fails intermittently on a PR that
**did not** modify any Flutter / mobile source code (or only modified
auto-generated Dart contract files under
`apps/mobile/lib/core/contracts/`).

---

## ─────────────── BEGIN PROMPT ───────────────

You are an AI software engineer. Your task is to **harden the SAHOOL
Flutter Android CI workflow against transient infrastructure flakes**
in the repository `kafaat/sahool-unified-v15-idp`. Create a new branch
`claude/fix-flutter-android-ci-flake` and submit a focused PR.

### Background

The PR `kafaat/sahool-unified-v15-idp#1581` repeatedly hit a "Flutter -
Android Build" CI failure even though it did not touch any
`apps/mobile/**` source code (only auto-generated 2-line contract
version comments under `apps/mobile/lib/core/contracts/`). The pattern
of failures across 8 consecutive runs on the same code:

| Run | Result |
|---|---|
| #4307 | ✅ Passed |
| #4309 | ❌ Failed |
| #4313 | ✅ Passed |
| #4314 | ❌ Failed |
| #4316 | ❌ Failed |
| #4317 | ❌ Failed |
| #4318 | ❌ Failed |

This is a textbook **infrastructure flake** — same code, different
outcomes — caused by external CDN / network / disk-space variability.

### Files involved

Two workflows run a Flutter Android build:

1. **`.github/workflows/frontend-tests.yml`** · job
   `flutter-android-build` (around line 754). Runs on every PR
   touching `apps/mobile/**`. Heavy-weight: NDK, Flutter SDK, Gradle.

2. **`.github/workflows/flutter-apk.yml`** · job `build-apk`
   (around line 33). Same workload, runs on `apps/mobile/**` PR pushes.

Both jobs perform the same expensive, network-dependent steps:

- `actions/setup-java@v5` · download Temurin JDK 17 (~200 MB)
- `android-actions/setup-android@v4` · setup Android SDK
- `sdkmanager --install "platforms;android-35" "ndk;27.0.12077973"`
   · downloads ~1 GB Android NDK from Google
- `subosito/flutter-action@v2` · download Flutter SDK 3.27.1 (~500 MB)
- `flutter pub get` · pulls every transitive package from Pub.dev
- `flutter build apk --debug` · runs Gradle with 4 GB heap on a
   GitHub-hosted runner that has ~7 GB RAM total
- `actions/upload-artifact@v7` · uploads the resulting APK

Each of these can transiently fail on Pub.dev, Google CDN, Maven
Central, or simple OOM.

### Required changes

Apply **all** of the following. Each is small and orthogonal — please
keep them in separate, well-described commits inside the same PR so
the reviewer can revert any one independently if needed.

#### 1 · Skip Flutter jobs when PR only touches auto-generated contracts

The Dart contract files under `apps/mobile/lib/core/contracts/` are
**generated** by `scripts/sync-contracts-to-dart.ts` and have a
`/// DO NOT EDIT` header. Changes there can never affect Flutter
build correctness — only the contract values consumed at runtime.

Add `paths-ignore` to BOTH workflows so a contract-only PR does not
trigger the heavy Flutter Android job:

```yaml
on:
  pull_request:
    paths:
      - 'apps/mobile/**'
    paths-ignore:                                         # NEW
      - 'apps/mobile/lib/core/contracts/**'              # NEW
      - 'apps/mobile/**/*.md'                            # NEW
```

(Same change in `flutter-apk.yml` for the `push:` trigger.)

This single change would have skipped the Flutter Android job on
PR #1581's contract-version bump entirely. Verify by checking that
`git diff origin/main..HEAD -- 'apps/mobile/**'` for that PR shows
ONLY the two contracts files.

#### 2 · Add resilient retry to NDK + SDK installs

`sdkmanager --install "ndk;27.0.12077973"` is the single most
fragile step (1+ GB download from Google). Wrap it in a 3-attempt
shell retry with exponential back-off:

```bash
- name: Install required Android SDK components
  run: |
    for attempt in 1 2 3; do
      echo "Attempt $attempt: installing Android SDK components..."
      if yes | sdkmanager --install \
           "platforms;android-35" \
           "ndk;27.0.12077973"; then
        echo "✓ SDK components installed"
        exit 0
      fi
      echo "✗ Attempt $attempt failed; sleeping $((attempt * 30))s"
      sleep $((attempt * 30))
    done
    echo "::error::Failed to install Android SDK components after 3 attempts"
    exit 1
```

#### 3 · Pin Flutter SDK install via cache + retry

`subosito/flutter-action@v2` already supports `cache: true` (used).
Add a fallback retry **around the Flutter step** since the action
itself does not retry on download failures:

```yaml
- name: Setup Flutter (with retry on network failure)
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 15
    max_attempts: 3
    retry_wait_seconds: 30
    command: |
      curl -sSL https://...   # unsuitable here — see note below
```

Note: `subosito/flutter-action` is itself the install. The cleanest
approach is to use `nick-fields/retry@v3` to wrap a shell that
re-invokes the underlying flutter command. Alternatively, accept the
flake here and rely on item #4 (job-level retry).

#### 4 · Retry the entire Flutter Android job once on failure

Add a job-level retry. GitHub Actions has no native job-retry, but
the Marketplace action `nick-fields/retry@v3` (or a simple matrix +
`continue-on-error` + dependent collector) works. Since this PR is
focused on resilience, the simplest pattern is:

- Split `flutter-android-build` into `flutter-android-build` +
  `flutter-android-build-summary`.
- The summary job uses `if: always() && (needs.flutter-android-build.result == 'success' || needs.flutter-android-build-rerun.result == 'success')`
- Add a `flutter-android-build-rerun` job that runs only if the first
  attempt failed.

If that's too invasive, simpler: add `continue-on-error: false` and
document that flakes on this single check are tolerated by the merge
policy (require a manual re-run via the GitHub UI).

#### 5 · Cache the NDK across runs

Even with retries, downloading NDK every run wastes 1+ GB of bandwidth.
Add an `actions/cache@v5` step keyed on the NDK version BEFORE the
sdkmanager install:

```yaml
- name: Cache Android NDK
  uses: actions/cache@v5
  with:
    path: ${{ runner.temp }}/android-sdk/ndk/27.0.12077973
    key: android-ndk-27.0.12077973-${{ runner.os }}
```

#### 6 · Increase the disk-space-cleanup step

The current "Free disk space" step only removes `dotnet`, `ghc`,
`CodeQL`, and `boost`. The Android NDK + Flutter + node_modules can
push past 14 GB on a 7 GB runner. Add:

```bash
sudo rm -rf /opt/hostedtoolcache/Ruby || true
sudo rm -rf /opt/hostedtoolcache/PyPy || true
sudo rm -rf /opt/hostedtoolcache/go || true
sudo rm -rf /home/linuxbrew || true
sudo docker system prune --all --force || true
```

#### 7 · Set explicit Gradle daemon config to avoid OOM

The current step exports `GRADLE_OPTS` but doesn't configure the
daemon. Add `gradle.properties`-equivalent flags:

```bash
export GRADLE_OPTS="-Xmx5g \
  -XX:MaxMetaspaceSize=512m \
  -XX:+HeapDumpOnOutOfMemoryError \
  -Dfile.encoding=UTF-8 \
  -Dorg.gradle.daemon=false \
  -Dorg.gradle.caching=true \
  -Dorg.gradle.parallel=true \
  -Dorg.gradle.workers.max=2"
```

`-Dorg.gradle.daemon=false` is critical — daemon mode caches nothing
in CI and just holds 1+ GB of RAM hostage.

### Verification

After applying the changes:

1. **Local syntax check**: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/frontend-tests.yml')); yaml.safe_load(open('.github/workflows/flutter-apk.yml'))"` — both must succeed.

2. **Workflow lint**: if `actionlint` is available locally, run it.
   Otherwise, push the branch and confirm GitHub does not flag the
   workflow as malformed.

3. **Trigger CI**: push the branch, open a draft PR. The `Flutter -
   Android Build` job should:
   - Be **skipped** when the PR body lists only contract changes
     (verifies item #1).
   - Pass on first attempt for ~95 % of runs (verifies items #2-#7).

4. **Re-run sample**: re-run the same workflow run 3 times via the
   GitHub UI. All three should succeed (or fail with the same root
   cause, which is itself useful diagnostic info).

### Out-of-scope (do NOT change)

- Any code in `apps/mobile/**` outside the workflow files.
- `pubspec.yaml` / `pubspec.lock` — version pins are not the issue.
- The actual Dart code or Android Gradle config in
  `apps/mobile/sahool_field_app/android/`.
- Any other CI workflow (web, admin, services).

### Deliverable

A single PR titled:

```
ci(flutter): harden Android Build against CDN/network flakes
```

with each numbered item from §"Required changes" as a separate commit.
The PR description should reference this prompt and the parent
investigation in PR #1581.

### Reviewer checklist (include in the PR description)

- [ ] PR with only contract changes (e.g.
  `apps/mobile/lib/core/contracts/error_codes.dart`) does NOT trigger
  Flutter Android Build.
- [ ] PR with real `apps/mobile/**` change DOES trigger it.
- [ ] NDK install step retries on failure (manually break the Google
  CDN URL once to verify; revert).
- [ ] Cache hit on NDK reduces step time from minutes to seconds on
  the second run.
- [ ] Disk-space step shows >5 GB free after cleanup.
- [ ] Gradle finishes without OOM; build succeeds.

## ─────────────── END PROMPT ───────────────

---

## Notes for the human distributing this prompt

- The fix touches **only `.github/workflows/`**. No application code
  changes are needed.
- Estimated effort for an AI agent with full repo access: **30–60 min**
  including a CI roundtrip.
- Risk: low. Each change is in CI YAML, fully reversible.
- Owner: platform-team (CI + DevOps).
- Cross-references:
  - Source PR where the flake was diagnosed: #1581
  - Audit doc: `docs/audits/E2E_USER_JOURNEY_AUDIT.md` (if present)
  - Relevant CLAUDE.md sections: "GitHub Workflows" + "Mobile
    Architecture".
