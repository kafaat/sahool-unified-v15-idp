import java.util.Properties

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

// Load signing configuration from key.properties file (if exists)
// For release builds, create android/key.properties with:
//   storePassword=<keystore password>
//   keyPassword=<key password>
//   keyAlias=<key alias>
//   storeFile=<path to keystore file>
val keystorePropertiesFile = rootProject.file("key.properties")
val keystoreProperties = Properties()
if (keystorePropertiesFile.exists()) {
    keystorePropertiesFile.inputStream().use { keystoreProperties.load(it) }
}

android {
    namespace = "io.sahool.field"
    compileSdk = 36  // Android 16 — aligned across all SAHOOL mobile apps
    ndkVersion = "27.2.12479018"

    compileOptions {
        // Required for flutter_local_notifications and other libraries using Java 8+ APIs
        isCoreLibraryDesugaringEnabled = true
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    defaultConfig {
        applicationId = "io.sahool.field"
        // Camera, mobile_scanner, and geolocator require API 23+
        // SQLCipher and biometric auth also benefit from API 23+
        // flutter_tts requires API 24+ for full compatibility
        minSdk = 24
        targetSdk = 36  // Target Android 16 — aligned across all SAHOOL mobile apps
        versionCode = flutter.versionCode
        versionName = flutter.versionName

        // Enable multidex for large app with many dependencies
        multiDexEnabled = true

        // NDK ABI filters for ARM devices (most Android phones)
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64")
        }
    }

    // APK Split Configuration for optimized APK sizes
    // تقسيم APK حسب ABI لتقليل حجم التطبيق
    splits {
        abi {
            isEnable = true
            reset()
            include("arm64-v8a", "armeabi-v7a", "x86_64")
            isUniversalApk = true  // Also generate universal APK
        }
    }

    // Signing configurations for release builds
    signingConfigs {
        create("release") {
            if (keystorePropertiesFile.exists()) {
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
    }

    buildTypes {
        debug {
            // Debug build optimizations
            isDebuggable = true
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }

        release {
            // Enable code shrinking and minification for smaller APKs
            // ProGuard rules configured in proguard-rules.pro (2026-02-02)
            isMinifyEnabled = true
            isShrinkResources = true

            // Use release signing config if key.properties exists, otherwise use debug
            signingConfig = if (keystorePropertiesFile.exists()) {
                signingConfigs.getByName("release")
            } else {
                signingConfigs.getByName("debug")
            }

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // Lint options to prevent build failures on warnings
    lint {
        checkReleaseBuilds = true
        abortOnError = false
        warningsAsErrors = false
    }
}

flutter {
    source = "../.."
}

dependencies {
    // Core library desugaring for Java 8+ API support on older Android versions
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.4")
}
