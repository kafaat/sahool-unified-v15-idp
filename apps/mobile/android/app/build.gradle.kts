plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "io.sahool.sahool_field_app"
    compileSdk = 36
    ndkVersion = "27.0.12077973"

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
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "io.sahool.sahool_field_app"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        // Camera libraries (camera_android_camerax) require API 23+
        minSdk = 23
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
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

    // Release signing configuration
    // SECURITY: In production, use proper keystore via environment variables:
    // - KEYSTORE_FILE: Path to the keystore file
    // - KEYSTORE_PASSWORD: Keystore password
    // - KEY_ALIAS: Key alias
    // - KEY_PASSWORD: Key password
    signingConfigs {
        create("release") {
            val keystoreFile = System.getenv("KEYSTORE_FILE")
            if (keystoreFile != null && file(keystoreFile).exists()) {
                storeFile = file(keystoreFile)
                storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
                keyAlias = System.getenv("KEY_ALIAS") ?: "sahool"
                keyPassword = System.getenv("KEY_PASSWORD") ?: ""
            }
        }
    }

    buildTypes {
        release {
            // Enable code shrinking and minification for production
            isMinifyEnabled = true
            isShrinkResources = true

            // Use release signing if available, otherwise fall back to debug for development
            val releaseConfig = signingConfigs.findByName("release")
            signingConfig = if (releaseConfig?.storeFile != null) {
                releaseConfig
            } else {
                // WARNING: Debug signing for development only
                println("WARNING: Using debug signing config. Set KEYSTORE_* env vars for production.")
                signingConfigs.getByName("debug")
            }

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

flutter {
    source = "../.."
}

dependencies {
    // Core library desugaring for Java 8+ API support on older Android versions
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")
}
