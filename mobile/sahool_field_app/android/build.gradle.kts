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
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
    
    // Fix namespace for plugins that don't define it (AGP 8+ requirement)
    // This must be set up BEFORE evaluationDependsOn is called
    afterEvaluate {
        if (project.hasProperty("android")) {
            val android = project.extensions.findByName("android")
            if (android != null) {
                val androidExtension = android as com.android.build.gradle.BaseExtension
                if (androidExtension.namespace == null || androidExtension.namespace!!.isEmpty()) {
                    androidExtension.namespace = project.group.toString().ifEmpty { "com.sahool.plugin.${project.name.replace("-", "_")}" }
                }
            }
        }
    }
    
    // Force evaluation of the app subproject after setting up afterEvaluate
    project.evaluationDependsOn(":app")
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
