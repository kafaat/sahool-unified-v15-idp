# Flutter ProGuard Rules

# Keep Flutter classes
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Keep AndroidX Window Extensions (fixes R8 missing class error)
-dontwarn androidx.window.extensions.**
-dontwarn androidx.window.sidecar.**
-keep class androidx.window.** { *; }

# Keep Isar classes
-keep class dev.isar.** { *; }
-keep class io.isar.** { *; }

# Keep plugin classes
-keep class plugin.** { *; }

# Suppress warnings for missing classes
-ignorewarnings
