pluginManagement {
    val flutterSdkPath =
        run {
            val properties = java.util.Properties()
            val localPropertiesFile = file("local.properties")
            if (localPropertiesFile.exists()) {
                localPropertiesFile.inputStream().use { properties.load(it) }
            }
            val flutterSdkPath = properties.getProperty("flutter.sdk")
                ?: System.getenv("FLUTTER_ROOT")
                ?: run {
                    // Try common Flutter installation paths
                    listOf(
                        "${System.getProperty("user.home")}/flutter",
                        "${System.getProperty("user.home")}/.flutter",
                        "/opt/hostedtoolcache/flutter",
                        System.getenv("HOME")?.let { "$it/flutter" }
                    ).firstOrNull { path -> path != null && file(path).exists() }
                }
            require(flutterSdkPath != null) {
                "flutter.sdk not set in local.properties and FLUTTER_ROOT environment variable not defined"
            }
            flutterSdkPath
        }

    includeBuild("$flutterSdkPath/packages/flutter_tools/gradle")

    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

plugins {
    id("dev.flutter.flutter-plugin-loader") version "1.0.0"
    id("com.android.application") version "8.9.1" apply false
    id("org.jetbrains.kotlin.android") version "2.1.0" apply false
}

include(":app")
