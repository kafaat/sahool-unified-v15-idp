pluginManagement {
    val flutterSdkPath =
        run {
            val properties = java.util.Properties()
            file("local.properties").inputStream().use { properties.load(it) }
            val flutterSdkPath = properties.getProperty("flutter.sdk")
            require(flutterSdkPath != null) { "flutter.sdk not set in local.properties" }
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
    id("com.android.application") version "8.1.4" apply false
    id("org.jetbrains.kotlin.android") version "1.9.24" apply false
}

include(":app")

// Fix namespace for third-party plugins (AGP 8.0+ requirement)
val pluginNamespaces = mapOf(
    "isar_flutter_libs" to "dev.isar.isar_flutter_libs",
    "path_provider_android" to "io.flutter.plugins.pathprovider",
    "shared_preferences_android" to "io.flutter.plugins.sharedpreferences",
    "sqflite" to "com.tekartik.sqflite",
    "sqlite3_flutter_libs" to "eu.simonbinder.sqlite3_flutter_libs",
    "connectivity_plus" to "dev.fluttercommunity.plus.connectivity",
    "flutter_secure_storage" to "com.it_nomads.fluttersecurestorage",
    "image_picker_android" to "io.flutter.plugins.imagepicker",
    "camera_android" to "io.flutter.plugins.camera",
    "workmanager" to "dev.fluttercommunity.workmanager"
)

gradle.beforeProject {
    if (name != rootProject.name && name != "app") {
        val namespace = pluginNamespaces[name] ?: "plugin.${name.replace(Regex("[^a-zA-Z0-9_]"), "_")}"
        extra.set("android.namespace", namespace)
    }
}

gradle.afterProject {
    if (plugins.hasPlugin("com.android.library")) {
        val android = extensions.findByName("android")
        if (android != null) {
            try {
                val namespaceProperty = android.javaClass.getMethod("getNamespace")
                val currentNamespace = namespaceProperty.invoke(android) as? String
                if (currentNamespace.isNullOrEmpty()) {
                    val namespace = pluginNamespaces[name] ?: "plugin.${name.replace(Regex("[^a-zA-Z0-9_]"), "_")}"
                    val setNamespace = android.javaClass.getMethod("setNamespace", String::class.java)
                    setNamespace.invoke(android, namespace)
                    println("✅ Set namespace for $name: $namespace")
                }
            } catch (e: Exception) {
                println("⚠️ Could not set namespace for $name: ${e.message}")
            }
        }
    }
}
