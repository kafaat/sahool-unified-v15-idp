plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "io.sahool.atmosphere"
    compileSdk = 36  // Android 16 - aligned with CI and field app
    ndkVersion = "27.0.12077973"

    compileOptions {
        // Required for libraries using Java 8+ APIs
        isCoreLibraryDesugaringEnabled = true
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    defaultConfig {
        applicationId = "io.sahool.atmosphere"
        // Sensors and other plugins require API 23+
        // speech_to_text requires API 24+ for full compatibility
        minSdk = 24
        targetSdk = 36  // Target Android 16
        versionCode = flutter.versionCode
        versionName = flutter.versionName

        // Enable multidex for large app with many dependencies
        multiDexEnabled = true

        // NDK ABI filters for ARM devices (most Android phones)
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64")
        }
    }

    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }

        release {
            // Enable code shrinking and minification for smaller APKs
            // Set to true once ProGuard rules are properly configured
            isMinifyEnabled = false
            isShrinkResources = false

            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig = signingConfigs.getByName("debug")

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
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")
}
