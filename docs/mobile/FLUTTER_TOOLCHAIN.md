# Flutter toolchain compatibility

Use **Flutter 3.44.9, stable archive, with Dart 3.12.2** for the existing mobile
applications and shared core. All four actual pubspecs declare Dart
`>=3.10.0 <3.13.0` and Flutter `>=3.44.9`; CI, release, and preview workflows pin
the exact validated Flutter version. The primary `apps/mobile/pubspec.yaml`
Flutter minimum is the source checked by the workflow drift tests.

## Why this version

The old Flutter 3.27.1 / Dart 3.6.0 workflow cannot resolve the primary app:
its SDK localization package pins `intl 0.19.0`, while the app requires
`intl ^0.20.2`. The original primary lock also already requires Dart 3.10.
Downgrading only intl would leave these toolchain requirements inconsistent.

Flutter 3.44.9 supplies `intl 0.20.2` and matches the original primary lock's
SDK-pinned test dependencies. Resolving that app changes only the lock's SDK
constraints; it does not upgrade its package versions. The secondary field app
and shared core now use the same `intl ^0.20.2` constraint. The field-app lock
updates the SDK-selected packages and the compatible calendar version.

This is an **archived compatibility baseline**, not a claim that 3.44.9 is the
latest Flutter release or receives the newest hotfixes. Flutter 3.47.9 /
Dart 3.13.7 was also tested. Pub resolution succeeded, but actual code generation
failed in analyzer 7.6.0 on `DotShorthandPropertyAccessImpl` while reading the
Dart 3.13 SDK, then stalled with pending actions. That process was stopped after
309 seconds. A targeted analyzer/Riverpod patch resolution did not remove the
existing generator constraints. The explicit Dart upper bound rejects that
known incompatible combination early.

Freezed 2.x, Riverpod 2.x, Drift, SQLite 2.x and SQLCipher remain in their
existing dependency families. A newer SDK migration must validate those
generators and the encrypted database integration together; this repair does
not change storage behavior or Python requirements.

## Android and source compatibility

Both Android applications use AGP 8.12.2, Kotlin 2.2.20, Gradle 8.14,
Java 17 and compile SDK 36. These satisfy the already-declared
`sensors_plus 7.0.0` minimums (AGP 8.12.1, Kotlin 2.2.0 and Gradle 8.13).
The NDK and signing/deployment configuration are unchanged. The Android build
must still pass in the existing GitHub runner; local validation does not claim
an APK was built.

Source migrations use `CardThemeData`, `DialogThemeData` and `TabBarThemeData`
with the same property values, generate field-app localizations into
`lib/generated/l10n`, and import that source instead of the removed synthetic
`package:flutter_gen`. Existing API tests name callbacks whose invocation is
used, because `_` is now a non-binding Dart wildcard. Small invalid export and
logger-call defects found by real compilation are corrected without changing
their runtime policy.

## Reproduce the checks

From the repository root, install Flutter 3.44.9 and use its bundled Dart.
CI installs `libsqlite3-dev` before native SQLite tests.

```sh
python -m pytest -q tests/unit/test_flutter_toolchain_consistency.py
cd apps/mobile
flutter pub get --enforce-lockfile
dart run build_runner build --delete-conflicting-outputs
flutter test test/unit/ test/widget/ test/integration/
flutter analyze --no-fatal-infos
```

Resolve the committed application locks in `apps/mobile/sahool_field_app` and
`apps/mobile/sahool_app` with `flutter pub get --enforce-lockfile` too. Resolve
the shared library in `packages/sahool-mobile-core` with `flutter pub get`.
The Test Suite workflow checks all four resolutions. Run code generation in
the field app and core before their analysis or tests. Generated fixture and
localization output is reproduced by these tools; unrelated generated-file
formatting changes are not part of this repair.

The Python guard checks all four SDK/intl declarations, all three application
locks, every Flutter setup action in the root and standalone app workflows,
reusable-workflow defaults and overrides, and the Dart 3.13 exclusion. Negative
cases prove that stale, floating, shadowed and inconsistent pins are rejected.
The native Dart compatibility test imports the real application route graph
and core exports and checks that migrated theme styles are preserved.

## Validation limits

The primary unit/widget/integration selection passed **664 tests** on Flutter
3.44.9. A separate focused run including the new native compile/theme checks
and existing logger/config tests passed **69 tests** (overlapping the previous
selection). The four migrated API-test files passed **45 tests**. Root, field
and shared-core code generation succeeded. All three application lockfiles
passed enforced resolution without changing their bytes. The SDK drift guard
passed **17 cases**.

Final root/field analysis has **zero errors**, with 1,651 warnings and 1,600
informational findings; the unmasked command still exits 1 because of warnings.
The unified app has zero errors, four warnings and 13 informational findings.
Standalone shared-core analysis still has 219 errors (178 in library sources),
including conflicting exports, missing helpers and copied integration-test
imports. Those broader library defects are outside this toolchain repair.

The full field-app run, before renaming the four API-test callbacks, recorded
4,683 passes and 20 failures. Four failures were compilation of those test files
and are covered by the passing 45-test rerun. The other 16 concern the tenant
default assertion, asynchronous notifier disposal and a network-dependent HTTP
expectation. They are retained as explicit follow-up findings, not skipped or
reported as passing. Root workflow validation passes; the two standalone nested
workflows retain existing deprecated-action findings.

An actual `flutter build web --release --no-pub` failed because the existing
application route graph imports `drift/native.dart`, `sqlite3` and SQLCipher,
which require `dart:ffi`. That native-storage chain is unavailable on web.
`deploy-preview.yml` and `lighthouse-ci.yml` contain web consumers; aligning
their SDK pin does not repair this separate platform limitation. No storage
fallback, encryption change, deployment, or masked successful build is added.

## First GitHub CI results and R8 configuration correction

The first PR run tested head
`c40ebd50c809652b5e04541fb6b04aa9057b9958` through merge
`be8071b360971666c18a0b9ba8a7e7779dda336f`. The
[Test Suite mobile job](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41238802657/job/124648282519)
passed **564 unit, 41 widget and 61 integration tests (666 total)** after code
generation and successful lock resolution. These CI counts are separate from
the earlier local runs above.

The [primary Android build](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41238802797/job/124648999694)
failed before APK compilation while applying `com.android.application`:
AGP rejected `android.enableR8`, which was removed in AGP 7.0, and
`assembleDebug` exited **1**. The obsolete `android.enableR8=true` option is
removed from both applications' `gradle.properties`. R8 has been the
[default shrinker since AGP 3.4](https://developer.android.com/build/releases/agp-3-4-0-release-notes?hl=en),
so no replacement opt-in is needed. Both `android.enableR8.fullMode=true`
settings and the existing shrinking/ProGuard configuration are preserved.
An APK build after this correction remains unverified until GitHub CI completes.

The [field-app Android build](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41238802809/job/124650681151)
also failed with **exit 1** on the same removed `android.enableR8` option.
Its failure is covered by removing that property from the field application's
configuration alongside the primary application.

The [iOS build](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41238802797/job/124648999729)
also exited **1**. While adding Swift Package Manager integration, Xcode rejected
the `flutter_native_splash` public headers (`include`) directory as invalid or
outside the target. The existing `continue-on-error: true` setting on the build
step makes the job appear successful; it does not demonstrate a successful iOS
build.

Flutter 3.44 enables SwiftPM by default. Both existing iOS applications lock
`flutter_native_splash 2.4.4`, whose Swift package lacks the public-header layout
required by that build path. To preserve their customized Podfiles, both apps
now explicitly set `flutter.config.enable-swift-package-manager: false`, the
[documented per-project CocoaPods option](https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers#turn-off-swiftpm-for-a-single-project).
This is a compatibility setting for Flutter 3.44.9 until the splash plugin and
the full native dependency graph are validated with SwiftPM. The package
[changelog records SwiftPM fixes in 2.4.5](https://pub.dev/packages/flutter_native_splash/changelog).
Podfiles, Xcode projects and package versions are unchanged. The drift guard
rejects a missing, enabled or string-valued SwiftPM override in either app.
The earlier iOS failure remains the actual CI result until a new build proves
this correction; local manifest acceptance is not an iOS build.
The extended guard passed **23 cases**. Flutter 3.44.9 accepted both project
manifests with `flutter pub get --offline --enforce-lockfile`; all three app
lockfile hashes remained unchanged. This used the project setting without
changing the user's global Flutter configuration.

The [wider primary test job](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41238802797/job/124648999718)
recorded **2,703 passes and 6 failures**. The
[full field-app test job](https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/41238802809/job/124649223327)
recorded **4,729 passes and 15 failures**, although its existing `tee` pipeline
reported job success. These failures remain recorded; the R8 correction does
not alter tests or their execution policy.

## Primary references

- [Flutter SDK archive](https://docs.flutter.dev/install/archive) and
  [official Linux release metadata](https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json)
- [Flutter 3.44.9 localization dependencies](https://github.com/flutter/flutter/blob/3.44.9/packages/flutter_localizations/pubspec.yaml)
- [Flutter 3.44.9 test dependencies](https://github.com/flutter/flutter/blob/3.44.9/packages/flutter_test/pubspec.yaml)
- [Flutter component theme migration](https://docs.flutter.dev/release/breaking-changes/component-theme-normalization)
- [Flutter localization source migration](https://docs.flutter.dev/release/breaking-changes/flutter-generate-i10n-source)
- [sensors_plus 7.0.0 requirements](https://pub.dev/packages/sensors_plus/versions/7.0.0)
- [Android Gradle Plugin 8.12 compatibility](https://developer.android.com/build/releases/agp-8-12-0-release-notes)
