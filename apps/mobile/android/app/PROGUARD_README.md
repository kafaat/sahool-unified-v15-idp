# ProGuard Obfuscation Configuration

This document explains the ProGuard configuration for the SAHOOL Field App and how it protects against reverse engineering.

## Overview

The app now uses aggressive ProGuard/R8 obfuscation to protect against reverse engineering and unauthorized access. We have two separate ProGuard configurations:

- **`proguard-rules.pro`**: Production rules with aggressive obfuscation
- **`proguard-rules-debug.pro`**: Debug rules that maintain debuggability

## What's Been Configured

### 1. R8 Full Mode
R8 full mode is enabled in `gradle.properties`:
```properties
android.enableR8.fullMode=true
android.enableR8=true
```

This provides:
- More aggressive code shrinking
- Better optimization
- Smaller APK size
- Enhanced obfuscation

### 2. Production Build Configuration (`proguard-rules.pro`)

#### Security Features:
- **Source file obfuscation**: Original file names are replaced with "SourceFile"
- **Line number removal**: Stack traces don't reveal original line numbers
- **Log removal**: All Android Log calls (d, v, i, w, e) are stripped from release builds
- **5 optimization passes**: Aggressive code optimization
- **Aggressive shrinking**: Removes unused code and resources

#### Protected Libraries:
✅ Dio HTTP Client & OkHttp
✅ Flutter Secure Storage
✅ Drift Database (SQLite/SQLCipher)
✅ Socket.IO Client
✅ Riverpod State Management
✅ JSON Serialization (Freezed, json_serializable)
✅ Flutter Local Notifications
✅ Image Processing (Camera, Image Picker)
✅ Mobile Scanner (QR/Barcode)
✅ Maps (Flutter Map, MapLibre GL)
✅ Security Libraries (Jailbreak Detection)
✅ All Flutter plugins

### 3. Debug Build Configuration (`proguard-rules-debug.pro`)

#### Debug-Friendly Features:
- **Keeps source files and line numbers**: Full stack traces for debugging
- **Keeps log statements**: All logging remains for development
- **Single optimization pass**: Faster build times
- **Maintains debuggability**: Easier to debug with Android Studio
- **Less aggressive shrinking**: Prevents issues during development

## Build Types Configuration

### Debug Builds
```bash
flutter build apk --debug
# OR
cd android && ./gradlew assembleDebug
```
- Uses `proguard-rules-debug.pro`
- Minification enabled but less aggressive
- Resource shrinking disabled for faster builds
- Keeps all debug symbols
- Logging statements preserved

### Release Builds
```bash
flutter build apk --release
# OR
cd android && ./gradlew assembleRelease
```
- Uses `proguard-rules.pro`
- Aggressive obfuscation enabled
- Resource shrinking enabled
- All log statements removed
- Source files and line numbers obfuscated
- Requires proper keystore configuration

## Security Improvements

### Before:
❌ Basic Flutter-only rules
❌ Source files and line numbers visible
❌ Log statements in production
❌ Easy to reverse engineer
❌ No library-specific rules

### After:
✅ Comprehensive rules for all dependencies
✅ Source files renamed to generic "SourceFile"
✅ All logging removed in production
✅ Aggressive code obfuscation
✅ Library-specific keep rules
✅ R8 full mode optimization
✅ 5-pass optimization
✅ Smaller APK size

## What Gets Obfuscated

### Obfuscated (Production):
- App package classes (except models and database)
- Method names
- Field names
- Variable names
- Source file names
- Line numbers

### Not Obfuscated (Kept):
- Flutter framework classes
- Plugin classes
- Model classes (JSON serialization)
- Database entities
- Classes with reflection
- Native methods
- Parcelable/Serializable classes
- Enum classes
- AndroidX libraries

## Testing ProGuard Configuration

### 1. Build Debug with Minification:
```bash
flutter build apk --debug
```
Test all app features to ensure nothing breaks.

### 2. Build Release:
```bash
flutter build apk --release
```
Thoroughly test all features in release mode.

### 3. Analyze APK:
```bash
cd android
./gradlew assembleRelease
# Then use Android Studio's APK Analyzer
```

### 4. Check for ProGuard Warnings:
Look for warnings in build output:
```bash
./gradlew assembleRelease --info | grep -i proguard
```

## Troubleshooting

### Issue: App crashes in release mode
**Solution**: Check if a class needs to be kept. Add a rule to `proguard-rules.pro`:
```proguard
-keep class your.package.YourClass { *; }
```

### Issue: JSON serialization fails
**Solution**: Ensure model classes are kept:
```proguard
-keep class your.package.models.** { *; }
```

### Issue: Reflection errors
**Solution**: Keep classes that use reflection:
```proguard
-keep class your.package.ReflectionClass { *; }
-keepclassmembers class your.package.ReflectionClass {
    <methods>;
    <fields>;
}
```

### Issue: Native method errors
**Solution**: Native methods are already kept, but if you add new ones:
```proguard
-keepclasseswithmembernames class * {
    native <methods>;
}
```

## Verifying Obfuscation

### 1. Check APK Size
Release APK should be significantly smaller than debug APK.

### 2. Decompile APK
Use tools like JADX to decompile the release APK:
```bash
# Install JADX
# Open release APK with JADX
# Verify class names are obfuscated (a, b, c, etc.)
```

### 3. Check Stack Traces
Stack traces in production should show:
- Generic source file names ("SourceFile")
- Obfuscated class names
- No revealing package structures

## Adding New Dependencies

When adding new Flutter packages or Android libraries:

1. Check if the library requires ProGuard rules
2. Add rules to both `proguard-rules.pro` and `proguard-rules-debug.pro`
3. Test in release mode
4. Check library documentation for recommended ProGuard rules

### Example:
```proguard
##############################################################################
# NEW LIBRARY NAME
##############################################################################

-keep class com.library.package.** { *; }
-dontwarn com.library.package.**
```

## Important Notes

### DO NOT:
- ❌ Remove keep rules for Flutter framework
- ❌ Remove keep rules for model classes
- ❌ Disable minification in release builds
- ❌ Keep debug symbols in production
- ❌ Use debug ProGuard rules in production

### DO:
- ✅ Test thoroughly after adding new rules
- ✅ Keep model classes for JSON serialization
- ✅ Keep classes that use reflection
- ✅ Test release builds before deployment
- ✅ Monitor crash reports for obfuscation issues
- ✅ Keep ProGuard mappings for crash analysis

## ProGuard Mapping Files

Release builds generate mapping files at:
```
android/app/build/outputs/mapping/release/mapping.txt
```

**IMPORTANT**: Save these files for each release! They're needed to deobfuscate crash reports.

### Recommended:
1. Upload mapping files to your crash reporting service (Firebase Crashlytics, Sentry, etc.)
2. Archive mapping files with version tags
3. Never delete mapping files for released versions

## Performance Impact

### Build Time:
- Debug builds: +10-20% (due to minification)
- Release builds: +20-30% (due to aggressive optimization)

### APK Size Reduction:
- Expected reduction: 20-40% smaller
- Depends on code complexity and dependencies

### Runtime Performance:
- Slightly improved due to optimization
- No negative impact on app performance

## References

- [Android ProGuard Documentation](https://developer.android.com/studio/build/shrink-code)
- [R8 Full Mode](https://developer.android.com/studio/build/shrink-code#full-mode)
- [Flutter ProGuard](https://docs.flutter.dev/deployment/android#shrinking-your-code-with-r8)

## Maintenance

Review and update ProGuard rules when:
- Adding new dependencies
- Upgrading major library versions
- Changing app architecture
- Adding new features with reflection
- Receiving crash reports related to missing classes

---

**Last Updated**: 2026-01-03
**Configuration Version**: 1.0
**Tested with**: Flutter 3.27.x, Dart 3.6.0
