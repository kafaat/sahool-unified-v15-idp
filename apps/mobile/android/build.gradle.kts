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

    // Fix for older Flutter plugins that don't have namespace defined in build.gradle
    // AGP 8.0+ requires namespace to be set in build.gradle instead of AndroidManifest.xml
    afterEvaluate {
        if (project.hasProperty("android")) {
            val android = project.extensions.findByName("android")
            if (android != null) {
                val androidExt = android as com.android.build.gradle.BaseExtension
                if (androidExt.namespace.isNullOrEmpty()) {
                    val manifestFile = file("${project.projectDir}/src/main/AndroidManifest.xml")
                    if (manifestFile.exists()) {
                        val manifest = groovy.xml.XmlSlurper().parse(manifestFile)
                        val packageName = manifest.getProperty("@package")?.toString()
                        if (!packageName.isNullOrEmpty()) {
                            androidExt.namespace = packageName
                        }
                    }
                }
            }
        }
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
