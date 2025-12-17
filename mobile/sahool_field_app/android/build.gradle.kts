allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

// Fix namespace for third-party plugins (AGP 8.0+ requirement)
subprojects {
    afterEvaluate {
        if (plugins.hasPlugin("com.android.library")) {
            extensions.findByType(com.android.build.gradle.LibraryExtension::class.java)?.apply {
                if (namespace.isNullOrEmpty()) {
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
                    namespace = pluginNamespaces[project.name]
                        ?: "plugin.${project.name.replace(Regex("[^a-zA-Z0-9_]"), "_")}"
                    println("✅ Set namespace for ${project.name}: $namespace")
                }
            }
        }
    }
}

val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    project.evaluationDependsOn(":app")
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
