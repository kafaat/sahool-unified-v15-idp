# ==============================================================================
# SAHOOL Field App - Production ProGuard Rules
# Generated: 2026-02-02
#
# هذا الملف يحتوي على قواعد ProGuard للإنتاج
# يوفر حماية قوية للكود مع الحفاظ على الأداء
# ==============================================================================

# Optimization passes - More passes = better optimization
-optimizationpasses 5
-dontusemixedcaseclassnames
-verbose

# ==============================================================================
# DEBUG INFO & LOGGING (Production Security)
# ==============================================================================

# Keep attributes for debugging in development
# For production, consider removing SourceFile,LineNumberTable
-keepattributes SourceFile,LineNumberTable,Signature,Exceptions,InnerClasses,Deprecated,EnclosingMethod

# Remove all logging calls in release builds for security
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
    public static *** w(...);
    public static *** e(...);
}

-assumenosideeffects class io.flutter.Log {
    public static *** d(...);
    public static *** v(...);
}

# ==============================================================================
# FLUTTER FRAMEWORK (Required)
# ==============================================================================

-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }
-keep class io.flutter.embedding.** { *; }

# Flutter JNI
-keep class io.flutter.embedding.engine.FlutterJNI { *; }
-keep class io.flutter.embedding.engine.deferredcomponents.** { *; }

# ==============================================================================
# ANDROID FRAMEWORK
# ==============================================================================

# AndroidX
-keep class androidx.** { *; }
-keep interface androidx.** { *; }
-dontwarn androidx.**

# Android Architecture Components
-keep class * extends androidx.lifecycle.ViewModel { <init>(); }
-keep class * extends androidx.lifecycle.AndroidViewModel { <init>(android.app.Application); }

# Work Manager
-keep class androidx.work.** { *; }
-dontwarn androidx.work.**

# ==============================================================================
# KOTLIN & COROUTINES
# ==============================================================================

-keep class kotlin.** { *; }
-keep class kotlin.Metadata { *; }
-dontwarn kotlin.**

# Kotlin Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-keep class kotlinx.coroutines.** { *; }
-dontwarn kotlinx.coroutines.**

# Keep generic signature of Call, Response (R8 full mode strips signatures)
-keep,allowobfuscation,allowshrinking class kotlin.coroutines.Continuation

# ==============================================================================
# NETWORK LIBRARIES
# ==============================================================================

# OkHttp
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }
-dontwarn okhttp3.**
-dontwarn okio.**

# Retrofit (if used indirectly)
-keep,allowobfuscation,allowshrinking interface retrofit2.Call
-keep,allowobfuscation,allowshrinking class retrofit2.Response

# ==============================================================================
# SERIALIZATION
# ==============================================================================

# Gson
-keep class com.google.gson.** { *; }
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn sun.misc.**
-keep class * extends com.google.gson.TypeAdapter
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# JSON Serialization for Flutter
-keep class * implements java.io.Serializable { *; }
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    !static !transient <fields>;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}

# ==============================================================================
# DATABASE - DRIFT & SQLCIPHER
# ==============================================================================

# Drift database
-keep class drift.** { *; }
-keep class moor.** { *; }
-dontwarn drift.**
-dontwarn moor.**

# SQLCipher
-keep class net.sqlcipher.** { *; }
-keep class net.sqlcipher.database.** { *; }
-dontwarn net.sqlcipher.**

# SQLite
-keep class org.sqlite.** { *; }
-dontwarn org.sqlite.**

# ==============================================================================
# SECURITY & CRYPTO
# ==============================================================================

# Android KeyStore
-keep class android.security.** { *; }
-keep class javax.crypto.** { *; }
-keep class javax.crypto.spec.** { *; }

# Flutter Secure Storage
-keep class com.it_nomads.fluttersecurestorage.** { *; }
-dontwarn com.it_nomads.fluttersecurestorage.**

# Crypto
-keep class org.bouncycastle.** { *; }
-dontwarn org.bouncycastle.**

# ==============================================================================
# CAMERA & IMAGE PROCESSING
# ==============================================================================

# Camera
-keep class io.flutter.plugins.camera.** { *; }
-dontwarn io.flutter.plugins.camera.**

# Image Picker
-keep class io.flutter.plugins.imagepicker.** { *; }
-dontwarn io.flutter.plugins.imagepicker.**

# ==============================================================================
# MAPS & LOCATION
# ==============================================================================

# Flutter Map
-keep class flutter_map.** { *; }
-dontwarn flutter_map.**

# Geolocator
-keep class com.baseflow.geolocator.** { *; }
-dontwarn com.baseflow.geolocator.**

# ==============================================================================
# CONNECTIVITY & NETWORK
# ==============================================================================

# Connectivity Plus
-keep class dev.fluttercommunity.plus.connectivity.** { *; }
-dontwarn dev.fluttercommunity.plus.connectivity.**

# Dio HTTP Client
-keep class io.flutter.plugins.dio.** { *; }
-dontwarn io.flutter.plugins.dio.**

# ==============================================================================
# STATE MANAGEMENT - RIVERPOD
# ==============================================================================

-keep class flutter_riverpod.** { *; }
-keep class riverpod.** { *; }
-dontwarn flutter_riverpod.**
-dontwarn riverpod.**

# ==============================================================================
# CHARTS & UI
# ==============================================================================

# FL Chart
-keep class fl_chart.** { *; }
-dontwarn fl_chart.**

# Flutter SVG
-keep class flutter_svg.** { *; }
-dontwarn flutter_svg.**

# Cached Network Image
-keep class cached_network_image.** { *; }
-dontwarn cached_network_image.**

# ==============================================================================
# BIOMETRIC AUTH
# ==============================================================================

# Local Auth (Biometric)
-keep class io.flutter.plugins.localauth.** { *; }
-dontwarn io.flutter.plugins.localauth.**

# ==============================================================================
# FILE & STORAGE
# ==============================================================================

# Path Provider
-keep class io.flutter.plugins.pathprovider.** { *; }
-dontwarn io.flutter.plugins.pathprovider.**

# Shared Preferences
-keep class io.flutter.plugins.sharedpreferences.** { *; }
-dontwarn io.flutter.plugins.sharedpreferences.**

# ==============================================================================
# NOTIFICATIONS
# ==============================================================================

# Flutter Local Notifications
-keep class com.dexterous.** { *; }
-keep class androidx.core.app.NotificationCompat** { *; }
-dontwarn com.dexterous.**

# ==============================================================================
# BARCODE & QR SCANNING
# ==============================================================================

# Mobile Scanner
-keep class dev.steenbakker.mobile_scanner.** { *; }
-keep class com.google.zxing.** { *; }
-keep class com.google.mlkit.vision.** { *; }
-dontwarn dev.steenbakker.mobile_scanner.**
-dontwarn com.google.zxing.**

# ==============================================================================
# DEVICE INFO & SECURITY
# ==============================================================================

# Device Info Plus
-keep class dev.fluttercommunity.plus.device_info.** { *; }
-dontwarn dev.fluttercommunity.plus.device_info.**

# Safe Device (Root Detection)
-keep class com.example.safe_device.** { *; }
-dontwarn com.example.safe_device.**

# ==============================================================================
# APP-SPECIFIC RULES
# ==============================================================================

# Main Activity
-keep class io.sahool.field.MainActivity { *; }

# Application class
-keep class io.sahool.field.** extends android.app.Application { *; }

# Native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Enum values
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Parcelable
-keepclassmembers class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator CREATOR;
}

# Keep R files
-keepclassmembers class **.R$* {
    public static <fields>;
}

# ==============================================================================
# R8 FULL MODE COMPATIBILITY
# ==============================================================================

# Keep generic signatures for reflection
-keepattributes Signature
-keepattributes InnerClasses
-keepattributes EnclosingMethod

# Keep annotations
-keepattributes RuntimeVisibleAnnotations
-keepattributes RuntimeInvisibleAnnotations
-keepattributes RuntimeVisibleParameterAnnotations
-keepattributes RuntimeInvisibleParameterAnnotations
-keepattributes AnnotationDefault

# ==============================================================================
# SUPPRESS WARNINGS
# ==============================================================================

# Google ML Kit (if used)
-dontwarn com.google.mlkit.**

# XML Pull Parser
-dontwarn org.xmlpull.v1.**
-dontwarn org.kxml2.io.**

# Annotation processors
-dontwarn javax.annotation.**
-dontwarn javax.inject.**

# Conscrypt & BouncyCastle (SSL)
-dontwarn org.conscrypt.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**

# Missing classes warnings
-dontwarn java.lang.invoke.StringConcatFactory

# ==============================================================================
# END OF PROGUARD RULES
# ==============================================================================
