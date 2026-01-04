##############################################################################
# SAHOOL Field App - Debug ProGuard Configuration
# Less aggressive obfuscation for debug builds to maintain debuggability
# Generated: 2026-01-03
##############################################################################

##############################################################################
# GENERAL DEBUG SETTINGS
##############################################################################

# Keep source file names and line numbers for debugging
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Keep all debug information
-keepattributes *Annotation*
-keepattributes Signature
-keepattributes Exceptions
-keepattributes InnerClasses
-keepattributes EnclosingMethod

# Less aggressive optimization for faster builds
-optimizationpasses 1
-dontusemixedcaseclassnames
-verbose

# DO NOT remove logging in debug builds
# -assumenosideeffects class android.util.Log - COMMENTED OUT FOR DEBUG

##############################################################################
# FLUTTER FRAMEWORK - Essential Rules
##############################################################################

-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }
-keep class io.flutter.embedding.** { *; }

# Flutter JNI
-keepclassmembers class * {
    native <methods>;
}

# Flutter plugin registry
-keep class io.flutter.plugin.common.** { *; }
-keep class io.flutter.plugin.platform.** { *; }

##############################################################################
# ANDROID CORE LIBRARIES
##############################################################################

# AndroidX
-keep class androidx.** { *; }
-keep interface androidx.** { *; }
-dontwarn androidx.**

# Android Work Manager
-keep class androidx.work.** { *; }
-dontwarn androidx.work.**

##############################################################################
# KOTLIN & COROUTINES
##############################################################################

# Kotlin
-keep class kotlin.** { *; }
-keep class kotlin.Metadata { *; }
-dontwarn kotlin.**
-keepclassmembers class **$WhenMappings {
    <fields>;
}

# Kotlin Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-keep,allowobfuscation,allowshrinking class kotlin.coroutines.Continuation

##############################################################################
# DIO HTTP CLIENT
##############################################################################

# OkHttp (used by Dio)
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }

-dontwarn org.conscrypt.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**

##############################################################################
# JSON SERIALIZATION
##############################################################################

# Gson
-keep class com.google.gson.** { *; }
-keep class sun.misc.Unsafe { *; }

# Keep model classes
-keep class io.sahool.sahool_field_app.data.models.** { *; }
-keep class io.sahool.sahool_field_app.domain.entities.** { *; }

# Keep JSON annotations
-keepclasseswithmembers class * {
    @com.google.gson.annotations.* <fields>;
}

##############################################################################
# DRIFT DATABASE
##############################################################################

-keep class drift.** { *; }
-keep class org.sqlite.** { *; }
-keep class net.sqlcipher.** { *; }
-dontwarn drift.**
-dontwarn org.sqlite.**
-dontwarn net.sqlcipher.**

-keep class io.sahool.sahool_field_app.data.database.** { *; }

##############################################################################
# FLUTTER SECURE STORAGE
##############################################################################

-keep class com.it_nomads.fluttersecurestorage.** { *; }
-dontwarn com.it_nomads.fluttersecurestorage.**

# Android KeyStore
-keep class android.security.keystore.** { *; }
-keep class javax.crypto.** { *; }

##############################################################################
# SOCKET.IO CLIENT
##############################################################################

-keep class io.socket.** { *; }
-keep interface io.socket.** { *; }
-dontwarn io.socket.**

-keep class io.socket.engineio.** { *; }
-dontwarn io.socket.engineio.**

-keep class org.json.** { *; }

##############################################################################
# RIVERPOD STATE MANAGEMENT
##############################################################################

# Keep all provider classes for debugging
-keep class **Provider { *; }
-keep class **NotifierProvider { *; }
-keep class **StateNotifierProvider { *; }

##############################################################################
# FLUTTER PLUGINS
##############################################################################

# Notifications
-keep class com.dexterous.** { *; }
-dontwarn com.dexterous.**

# Image Picker & Camera
-keep class io.flutter.plugins.imagepicker.** { *; }
-keep class io.flutter.plugins.camera.** { *; }
-keep class androidx.camera.** { *; }
-dontwarn androidx.camera.**

# Mobile Scanner
-keep class dev.steenbakker.mobile_scanner.** { *; }
-keep class com.google.mlkit.** { *; }
-keep class com.google.android.gms.vision.** { *; }
-dontwarn com.google.mlkit.**

# Maps
-keep class net.touchcapture.** { *; }
-keep class com.mapbox.** { *; }
-keep class org.maplibre.** { *; }
-dontwarn com.mapbox.**
-dontwarn org.maplibre.**

# Security - Jailbreak Detection
-keep class com.pichillilorenzo.** { *; }
-keep class dev.fluttercommunity.plus.device_info.** { *; }
-keep class dev.fluttercommunity.plus.package_info.** { *; }

# Storage & Preferences
-keep class io.flutter.plugins.sharedpreferences.** { *; }
-keep class io.flutter.plugins.pathprovider.** { *; }

# Connectivity
-keep class dev.fluttercommunity.plus.connectivity.** { *; }
-dontwarn dev.fluttercommunity.plus.connectivity.**

# UI Libraries
-keep class com.caverock.androidsvg.** { *; }
-dontwarn com.caverock.androidsvg.**

##############################################################################
# CUSTOM APP CLASSES
##############################################################################

# Keep your app's main activity with full debugging info
-keep class io.sahool.sahool_field_app.MainActivity { *; }
-keep class io.sahool.sahool_field_app.** extends android.app.Application { *; }

# Keep all native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

##############################################################################
# STANDARD ANDROID RULES
##############################################################################

# Enums
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Parcelable
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# Serializable
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}

##############################################################################
# JAVA 8+ DESUGARING
##############################################################################

-dontwarn java.lang.invoke.**
-keep class java.lang.invoke.** { *; }

##############################################################################
# R8 COMPATIBILITY
##############################################################################

-keepattributes RuntimeVisibleAnnotations
-keepattributes RuntimeInvisibleAnnotations
-keepattributes RuntimeVisibleParameterAnnotations
-keepattributes RuntimeInvisibleParameterAnnotations
-keepattributes AnnotationDefault

##############################################################################
# END OF DEBUG PROGUARD RULES
##############################################################################
