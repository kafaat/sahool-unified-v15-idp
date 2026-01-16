import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "io.sahool.field"
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
        applicationId = "io.sahool.field"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        // Camera libraries require API 23+
        minSdk = 23
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    // APK Split Configuration for optimized APK sizes
    // تقسيم APK حسب ABI لتقليل حجم التطبيق
    splits {
        abi {
            isEnabled = true
            reset()
            include("arm64-v8a", "armeabi-v7a", "x86_64")
            isUniversalApk = true  // Also generate universal APK
        }
    }

    signingConfigs {
        // Debug signing configuration
        getByName("debug") {
            storeFile = file("debug.keystore")
            storePassword = "android"
            keyAlias = "debug"
            keyPassword = "android"
        }
        // Release signing configuration
        // Reads from keystore.properties file or falls back to environment variables for CI/CD
        create("release") {
            // Load from keystore.properties for security
            val keystorePropertiesFile = rootProject.file("keystore.properties")
            if (keystorePropertiesFile.exists()) {
                val keystoreProperties = Properties()
                keystoreProperties.load(FileInputStream(keystorePropertiesFile))

                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
            } else {
                // Fallback for CI/CD - use environment variables
                storeFile = file(System.getenv("RELEASE_STORE_FILE") ?: "release.keystore")
                storePassword = System.getenv("RELEASE_STORE_PASSWORD") ?: ""
                keyAlias = System.getenv("RELEASE_KEY_ALIAS") ?: ""
                keyPassword = System.getenv("RELEASE_KEY_PASSWORD") ?: ""
            }
        }
    }

    buildTypes {
        debug {
            signingConfig = signingConfigs.getByName("debug")
        }
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
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
