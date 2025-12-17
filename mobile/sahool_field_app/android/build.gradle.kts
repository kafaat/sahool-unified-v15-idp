allprojects {
    repositories {
        google()
        mavenCentral()
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
    
    // Fix for plugins missing namespace (required for AGP 8.0+)
    afterEvaluate {
        if (plugins.hasPlugin("com.android.application") || plugins.hasPlugin("com.android.library")) {
            extensions.findByType<com.android.build.gradle.BaseExtension>()?.apply {
                if (namespace == null) {
                    // Set namespace based on package name or a default
                    namespace = when (project.name) {
                        "isar_flutter_libs" -> "dev.isar.isar_flutter_libs"
                        else -> project.group?.toString() ?: "com.sahool.${project.name}"
                    }
                }
            }
        }
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
