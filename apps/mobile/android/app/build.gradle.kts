plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "io.sahool.sahool_field_app"
    compileSdk = 36
    ndkVersion = "28.2.13676358"

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
        minSdk = flutter.minSdkVersion
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
    // SECURITY: Release builds REQUIRE proper keystore configuration
    // Configure via environment variables OR keystore.properties file:
    // - KEYSTORE_FILE / storeFile: Path to the keystore file
    // - KEYSTORE_PASSWORD / storePassword: Keystore password
    // - KEY_ALIAS / keyAlias: Key alias
    // - KEY_PASSWORD / keyPassword: Key password
    signingConfigs {
        create("release") {
            // Try to load from keystore.properties file first
            val keystorePropertiesFile = rootProject.file("keystore.properties")
            val useKeystoreProperties = keystorePropertiesFile.exists()

            if (useKeystoreProperties) {
                val keystoreProperties = java.util.Properties()
                keystoreProperties.load(java.io.FileInputStream(keystorePropertiesFile))

                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
            } else {
                // Fall back to environment variables
                val keystoreFile = System.getenv("KEYSTORE_FILE")
                val keystorePassword = System.getenv("KEYSTORE_PASSWORD")
                val keyAliasEnv = System.getenv("KEY_ALIAS")
                val keyPasswordEnv = System.getenv("KEY_PASSWORD")

                if (keystoreFile != null && keystorePassword != null &&
                    keyAliasEnv != null && keyPasswordEnv != null) {
                    storeFile = file(keystoreFile)
                    storePassword = keystorePassword
                    keyAlias = keyAliasEnv
                    keyPassword = keyPasswordEnv
                } else {
                    // Configuration is incomplete - will be validated in buildTypes.release
                    storeFile = null
                    storePassword = ""
                    keyAlias = ""
                    keyPassword = ""
                }
            }
        }
    }

    buildTypes {
        debug {
            // Enable minification for debug builds to catch ProGuard issues early
            // but use less aggressive rules to maintain debuggability
            isMinifyEnabled = true
            isShrinkResources = false  // Disable resource shrinking for faster builds

            // Use debug-specific ProGuard rules
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules-debug.pro"
            )

            // Keep debug symbols and crash reporting information
            isDebuggable = true
        }

        release {
            // Enable code shrinking and minification for production
            isMinifyEnabled = true
            isShrinkResources = true

            // SECURITY: Release builds MUST use proper keystore - no fallback to debug signing
            val releaseConfig = signingConfigs.getByName("release")

            // Validate that keystore is properly configured
            if (releaseConfig.storeFile == null || !releaseConfig.storeFile!!.exists()) {
                throw GradleException(
                    """
                    |
                    |========================================================================
                    | ERROR: Release keystore is not configured!
                    |========================================================================
                    |
                    | Release builds require a proper keystore configuration for security.
                    | Debug signing is NOT allowed for release builds.
                    |
                    | To fix this, choose ONE of the following options:
                    |
                    | Option 1: Create keystore.properties file (recommended for local builds)
                    |   1. Copy android/keystore.properties.example to android/keystore.properties
                    |   2. Fill in your keystore details:
                    |      - storeFile=/path/to/your/keystore.jks
                    |      - storePassword=your_keystore_password
                    |      - keyAlias=your_key_alias
                    |      - keyPassword=your_key_password
                    |   3. Ensure keystore.properties is in .gitignore (never commit it!)
                    |
                    | Option 2: Set environment variables (recommended for CI/CD)
                    |   export KEYSTORE_FILE=/path/to/your/keystore.jks
                    |   export KEYSTORE_PASSWORD=your_keystore_password
                    |   export KEY_ALIAS=your_key_alias
                    |   export KEY_PASSWORD=your_key_password
                    |
                    | For development/testing only, you can use the debug build variant:
                    |   flutter build apk --debug
                    |
                    |========================================================================
                    |
                    """.trimMargin()
                )
            }

            signingConfig = releaseConfig

            // Use production ProGuard rules with aggressive obfuscation
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
